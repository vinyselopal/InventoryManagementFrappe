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
        for item in self.items:
            if self.type == "Consume" or self.type == "Transfer":
                item_warehouse_balance = check_warehouse_balance(item.source_warehouse, item.name, item.qty)
                return True if item_warehouse_balance > 0 else False

    def validate_mandatory_warehouses(self):
        for item in self.items:
            if (self.type == "Consume" and item.source_warehouse == None):
                return False
            if (self.type == "Receive" and item.target_warehouse == None):
                return False
            if (self.type == "Transfer" and (item.source_warehouse == None or item.target_warehouse == None)):
                return False
            else: 
                return True

    def on_submit(self):
        for item in self.items:
            if self.type == "Receive":
                create_sle(item.target_warehouse, item.qty, item, None)

            elif self.type == "Consume":
                create_sle(item.source_warehouse, -item.qty, item, None)

            else:
                create_sle(item.target_warehouse, item.qty, item, None)
                create_sle(item.source_warehouse, -item.qty, item, None)

    def on_cancel(self):
        for item in self.items:
            if self.type == "Receive":
                create_sle(item.target_warehouse, -item.qty, item, None)

            elif self.type == "Consume":
                create_sle(item.source_warehouse, item.qty, item, None)

            else:
                create_sle(item.target_warehouse, -item.qty, item, None)
                create_sle(item.source_warehouse, item.qty, item, None)


def create_sle(warehouse: str, qty: float, item: dict, valuation_rate: int) -> None:
    sle = frappe.new_doc("Stock Ledger Entry")
    sle.item = item.item
    sle.warehouse = warehouse
    sle.qty_change = qty
    sle.valuation_rate = valuation_rate or get_valuation_rate(item)
    sle.insert()


def get_valuation_rate(item: dict) -> float:
    StockLedgerEntry = frappe.qb.DocType("Stock Ledger Entry")

    result = (
        frappe.qb.from_(StockLedgerEntry)
        .select(
            Sum(StockLedgerEntry.valuation_rate * StockLedgerEntry.qty_change).as_("valuation_rate_sum"),
            Sum(StockLedgerEntry.qty_change).as_("qty_change"),
        )
        .where(
            (StockLedgerEntry.item == item)
            & (StockLedgerEntry.docstatus == 1)
        )
    ).run(as_dict=True)

    return (
       (result[0].valuation_rate_sum + (item.rate * item.qty)) / (result[0].qty_change + item.qty)
    ) if result else 0

def check_warehouse_balance(warehouse, item, qty):
    StockLedgerEntry = frappe.qb.DocType("Stock Ledger Entry")

    result = (
        frappe.qb.from_(StockLedgerEntry)
        .select(
            "qty_change",
            Sum(StockLedgerEntry.qty_change).as_("qty_balance")
        )
        .where(
            (StockLedgerEntry.item == item)
            & (StockLedgerEntry.warehouse == warehouse)
        )
    ).run(as_dict=True)

    return result[0].qty_balance or 0
