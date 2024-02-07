# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder.functions import Sum

class StockEntry(Document):
    def validate(self):
        self.validate_balance_qty()
        self.validate_mandatory_warehouses()

    def validate_balance_qty(self):
        if self.type == "Receive":
            return

        for item in self.stock_entry_items:
            item_warehouse_balance = check_warehouse_balance(item.source_warehouse, item.name)
            return True if item_warehouse_balance > 0 else False

    def validate_mandatory_warehouses(self):
        for item in self.stock_entry_items:
            if (self.type == "Consume" and item.source_warehouse == None):
                return False
            if (self.type == "Receive" and item.target_warehouse == None):
                return False
            if (self.type == "Transfer" and (item.source_warehouse == None or item.target_warehouse == None)):
                return False
            else:
                return True

    def on_submit(self):
        for item_row in self.stock_entry_items:
            receipt_valuation_rate = get_valuation_rate(item_row.item, item_row.rate, item_row.qty)
            consume_valuation_rate = get_valuation_rate(item_row.item, item_row.rate, -item_row.qty)

            if self.type == "Receive":
                create_sle(item_row.target_warehouse, item_row.qty, item_row.item, receipt_valuation_rate)

            elif self.type == "Consume":
                create_sle(item_row.source_warehouse, -item_row.qty, item_row.item, consume_valuation_rate)

            else:
                create_sle(item_row.target_warehouse, item_row.qty, item_row.item, receipt_valuation_rate)
                create_sle(item_row.source_warehouse, -item_row.qty, item_row.item, consume_valuation_rate)

    def on_cancel(self):
        for item in self.stock_entry_items:
            receipt_valuation_rate = get_valuation_rate(item.item, item.rate, item.qty)
            consume_valuation_rate = get_valuation_rate(item.item, item.rate, -item.qty)

            if self.type == "Receive":
                create_sle(item.target_warehouse, -item.qty, item.item, consume_valuation_rate)

            elif self.type == "Consume":
                create_sle(item.source_warehouse, item.qty, item.item, receipt_valuation_rate)

            else:
                create_sle(item.target_warehouse, -item.qty, item.item, consume_valuation_rate)
                create_sle(item.source_warehouse, item.qty, item.item, receipt_valuation_rate)

def create_sle(warehouse: str, qty: float, item: dict, valuation_rate: int) -> None:
    sle = frappe.new_doc("Stock Ledger Entry")
    sle.item = item
    sle.warehouse = warehouse
    sle.qty_change = qty
    sle.valuation_rate = valuation_rate
    sle.insert()


def get_valuation_rate(item: str, item_rate, item_qty) -> float:
    StockLedgerEntry = frappe.qb.DocType("Stock Ledger Entry")

    result = (
        frappe.qb.from_(StockLedgerEntry)
        .select(
            Sum(StockLedgerEntry.valuation_rate * StockLedgerEntry.qty_change).as_("valuation_rate_sum"),
            Sum(StockLedgerEntry.qty_change).as_("qty_change"),
        )
        .where(
            (StockLedgerEntry.item == item)
        )
    ).run(as_dict=True)

    return (
       ((result[0].valuation_rate_sum or 0) + (item.rate * item.qty)) / ((result[0].qty_change or 0) + item.qty)
    ) if result else 0

def check_warehouse_balance(warehouse, item):
    StockLedgerEntry = frappe.qb.DocType("Stock Ledger Entry")

    result = (
        frappe.qb.from_(StockLedgerEntry)
        .select(
            Sum(StockLedgerEntry.qty_change).as_("qty_balance")
        )
        .where(
            (StockLedgerEntry.item == item)
            & (StockLedgerEntry.warehouse == warehouse)
        )
    ).run(as_dict=True)

    return result[0].qty_balance or 0
