# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder.functions import Sum
from frappe.utils import today, now, get_time


class MandatoryWarehouseMissing(frappe.ValidationError):
    pass


class NotEnoughQuantity(frappe.ValidationError):
    pass


class StockEntry(Document):
    def validate(self):
        self.validate_balance_qty()
        self.validate_mandatory_warehouses()

    def validate_balance_qty(self):
        if self.type == "Receive":
            return

        for item in self.stock_entry_items:
            item_warehouse_balance = get_warehouse_balance(
                item.source_warehouse, item.item, self.stock_entry_items
            )

            if item_warehouse_balance < item.qty:
                frappe.throw(
                    title="Error",
                    msg="Warehouse balance lower than requested item quantity",
                    exc=NotEnoughQuantity,
                )

    def validate_mandatory_warehouses(self):
        condition_msg_mapping = {
            "Consume": {
                "condition": lambda item: item.source_warehouse == None,
                "msg": "Please provide source warehouse for the items",
            },
            "Receive": {
                "condition": lambda item: item.target_warehouse == None,
                "msg": "Please provide target warehouse for the items",
            },
            "Transfer": {
                "condition": lambda item: item.source_warehouse == None
                or item.target_warehouse == None,
                "msg": "Please provide both source and target warehouses for the items",
            },
        }

        for item in self.stock_entry_items:
            msg = condition_msg_mapping[self.type]["msg"]
            condition = condition_msg_mapping[self.type]["condition"](item)

            if condition:
                frappe.throw(
                    title="Error",
                    msg=msg,
                    exc=MandatoryWarehouseMissing,
                )

    def before_insert(self):
        self.stock_entry_items = club_similar_item_rows(self.stock_entry_items)

    def on_submit(self):

        for item_row in self.stock_entry_items:
            receipt_valuation_rate = get_valuation_rate(
                item_row.item, item_row.rate, item_row.qty
            )
            consume_valuation_rate = get_valuation_rate(
                item_row.item, item_row.rate, -item_row.qty
            )

            if self.type == "Receive":
                create_sle(
                    item_row.target_warehouse,
                    item_row.qty,
                    item_row.item,
                    receipt_valuation_rate,
                )

            elif self.type == "Consume":
                create_sle(
                    item_row.source_warehouse,
                    -item_row.qty,
                    item_row.item,
                    consume_valuation_rate,
                )

            else:
                create_sle(
                    item_row.target_warehouse,
                    item_row.qty,
                    item_row.item,
                    receipt_valuation_rate,
                )
                create_sle(
                    item_row.source_warehouse,
                    -item_row.qty,
                    item_row.item,
                    consume_valuation_rate,
                )

    def on_cancel(self):
        for item in self.stock_entry_items:
            receipt_valuation_rate = get_valuation_rate(item.item, item.rate, item.qty)
            consume_valuation_rate = get_valuation_rate(item.item, item.rate, -item.qty)

            if self.type == "Receive":
                create_sle(
                    item.target_warehouse, -item.qty, item.item, consume_valuation_rate
                )

            elif self.type == "Consume":
                create_sle(
                    item.source_warehouse, item.qty, item.item, receipt_valuation_rate
                )

            else:
                create_sle(
                    item.target_warehouse, -item.qty, item.item, consume_valuation_rate
                )
                create_sle(
                    item.source_warehouse, item.qty, item.item, receipt_valuation_rate
                )


def club_similar_item_rows(stock_entry_items):
    dict_items = {}
    for item_row in stock_entry_items:
        if not (item_row.item in dict_items):
            dict_items[item_row.item] = item_row
            continue
        existing_item_row = dict_items[item_row.item]
        existing_item_row.qty = existing_item_row.qty + item_row.qty
        stock_entry_items.remove(item_row)
    return stock_entry_items


def validate_item_warehouses(se_items, msg, condition):
    for item in se_items:
        if condition(item):
            frappe.throw(title="Error", msg=msg, exc=MandatoryWarehouseMissing)


def create_sle(warehouse: str, qty: float, item: dict, valuation_rate: int) -> None:
    sle = frappe.new_doc("Stock Ledger Entry")
    sle.item = item
    sle.warehouse = warehouse
    sle.qty_change = qty
    sle.valuation_rate = valuation_rate
    sle.posting_date = today()
    sle.posting_time = now()
    sle.insert()


def get_valuation_rate(item: str, item_rate, item_qty) -> float:
    StockLedgerEntry = frappe.qb.DocType("Stock Ledger Entry")

    result = (
        frappe.qb.from_(StockLedgerEntry)
        .select(
            Sum(StockLedgerEntry.valuation_rate * StockLedgerEntry.qty_change).as_(
                "valuation_rate_sum"
            ),
            Sum(StockLedgerEntry.qty_change).as_("qty_change"),
        )
        .where((StockLedgerEntry.item == item))
    ).run(as_dict=True)

    denominator = (result[0].qty_change or 0) + item_qty

    if not denominator == 0:
        return (
            (
                ((result[0].valuation_rate_sum or 0) + (item_rate * item_qty))
                / denominator
            )
            if result
            else 0
        )


def get_warehouse_balance(warehouse, item, stock_entry_items):
    all_sles = frappe.get_all(
        doctype="Stock Ledger Entry", fields=["qty_change", "item", "warehouse"]
    )

    StockLedgerEntry = frappe.qb.DocType("Stock Ledger Entry")
    result = (
        frappe.qb.from_(StockLedgerEntry)
        .select(Sum(StockLedgerEntry.qty_change).as_("qty_balance"))
        .where(
            (StockLedgerEntry.item == item) & (StockLedgerEntry.warehouse == warehouse)
        )
    ).run()
    return result[0][0] or 0
