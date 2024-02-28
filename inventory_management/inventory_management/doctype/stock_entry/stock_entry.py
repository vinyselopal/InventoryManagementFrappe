# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder.functions import Sum


class MandatoryWarehouseMissing(frappe.ValidationError):
    pass


class InsufficientItems(frappe.ValidationError):
    pass


class StockEntry(Document):
    @frappe.whitelist()
    def get_last_sle_for_item_warehouse(self, item, warehouse):
        print("warehouse", warehouse)
        sle = frappe.get_last_doc("Stock Ledger Entry", filters={"item": item, "warehouse": warehouse})
        return sle

    def validate(self):
        self.validate_balance_qty()
        self.validate_mandatory_warehouses()

    def validate_balance_qty(self):
        if self.type == "Receive":
            return

        for item_row in self.stock_entry_items:
            item_warehouse_balance = get_item_balance_for_warehouse(
                item_row.source_warehouse, item_row.item
            )

            if item_warehouse_balance < item_row.qty:
                frappe.throw(
                    title="Error",
                    msg="Warehouse balance lower than requested item quantity",
                    exc=InsufficientItems,
                )

    def validate_mandatory_warehouses(self):
        for item_row in self.stock_entry_items:
            if self.type == "Consume":
                if item_row.source_warehouse == None:
                    frappe.throw(
                        title="Error",
                        msg="Please provide source warehouse for the items",
                        exc=MandatoryWarehouseMissing,
                    )
            if self.type == "Receive":
                if item_row.target_warehouse == None:
                    frappe.throw(
                        title="Error",
                        msg="Please provide target warehouse for the items",
                        exc=MandatoryWarehouseMissing,
                    )
            if self.type == "Transfer":
                if item_row.target_warehouse == None or item_row.source_warehouse == None:
                    frappe.throw(
                        title="Error",
                        msg="Please provide both source and target warehouses for the items",
                        exc=MandatoryWarehouseMissing,
                    )

    def club_similar_item_rows(self) -> None:
        item_warehouse_combination_mapping = {}

        def add_to_dict(item_warehouse_combination_mapping, key):
            current_combination = key
            if not (current_combination in item_warehouse_combination_mapping):
                item_warehouse_combination_mapping[current_combination] = item_row
                return
            existing_item_row = item_warehouse_combination_mapping[current_combination]
            existing_item_row.qty = existing_item_row.qty + item_row.qty
            self.stock_entry_items.remove(item_row)

        for item_row in self.stock_entry_items:
            if self.type == "Consume":
                add_to_dict(item_warehouse_combination_mapping, (item_row.item, item_row.source_warehouse))
            if self.type == "Receive":
                add_to_dict(item_warehouse_combination_mapping, (item_row.item, item_row.target_warehouse))
            if self.type == "Transfer":
                add_to_dict(
                    item_warehouse_combination_mapping,
                    (
                        item_row.item,
                        item_row.source_warehouse,
                        item_row.target_warehouse,
                    ),
                )

    def before_insert(self):
        self.club_similar_item_rows()

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
                    self.date,
                    self.time,
                    self.name
                )

            elif self.type == "Consume":
                create_sle(
                    item_row.source_warehouse,
                    -item_row.qty,
                    item_row.item,
                    consume_valuation_rate,
                    self.date,
                    self.time,
                    self.name
                )

            else:
                create_sle(
                    item_row.target_warehouse,
                    item_row.qty,
                    item_row.item,
                    receipt_valuation_rate,
                    self.date,
                    self.time,
                    self.name
                )
                create_sle(
                    item_row.source_warehouse,
                    -item_row.qty,
                    item_row.item,
                    consume_valuation_rate,
                    self.date,
                    self.time,
                    self.name
                )

    def on_cancel(self):
        for item_row in self.stock_entry_items:
            receipt_valuation_rate = get_valuation_rate(item_row.item, item_row.rate, item_row.qty)
            consume_valuation_rate = get_valuation_rate(item_row.item, item_row.rate, -item_row.qty)

            if self.type == "Receive":
                create_sle(
                    item_row.target_warehouse,
                    -item_row.qty,
                    item_row.item,
                    consume_valuation_rate,
                    self.date,
                    self.time,
                    self.name
                )

            elif self.type == "Consume":
                create_sle(
                    item_row.source_warehouse,
                    item_row.qty,
                    item_row.item,
                    receipt_valuation_rate,
                    self.date,
                    self.time,
                    self.name
                )

            else:
                create_sle(
                    item_row.target_warehouse,
                    -item_row.qty,
                    item_row.item,
                    consume_valuation_rate,
                    self.date,
                    self.time,
                    self.name
                )
                create_sle(
                    item_row.source_warehouse,
                    item_row.qty,
                    item_row.item,
                    receipt_valuation_rate,
                    self.date,
                    self.time,
                    self.name
                )


def create_sle(
    warehouse: str, qty: float, item: str, valuation_rate: int, date: str, time: str, stock_entry: str
) -> None:
    sle = frappe.new_doc("Stock Ledger Entry")
    sle.item = item
    sle.warehouse = warehouse
    sle.qty_change = qty
    sle.valuation_rate = valuation_rate
    sle.posting_date = date
    sle.posting_time = time
    sle.stock_entry = stock_entry
    sle.insert()


def get_valuation_rate(item: str, item_rate: float, item_qty: float) -> float:
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

    total_qty = (result[0].qty_change or 0) + item_qty

    if not total_qty == 0:
        return (
            (((result[0].valuation_rate_sum or 0) + (item_rate * item_qty)) / total_qty)
            if result
            else 0
        )


def get_item_balance_for_warehouse(warehouse: str, item: str) -> float :

    StockLedgerEntry = frappe.qb.DocType("Stock Ledger Entry")

    result = (
        frappe.qb.from_(StockLedgerEntry)
        .select(Sum(StockLedgerEntry.qty_change).as_("qty_balance"))
        .where(
            (StockLedgerEntry.item == item) & (StockLedgerEntry.warehouse == warehouse)
        )
    ).run()

    return result[0][0] or 0
