# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from inventory_management.inventory_management.doctype.stock_entry.stock_entry import (
    get_warehouse_balance,
)


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)

    return columns, data


def get_columns(filters):
    columns = [
        {
            "fieldname": "item",
            "label": _("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "reqd": 1,
        },
        {
            "fieldname": "warehouse",
            "label": _("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "reqd": 1,
        },
        {
            "fieldname": "qty_change",
            "label": _("Qty Change"),
            "fieldtype": "Int",
            "reqd": 1,
        },
        {
            "fieldname": "valuation_rate",
            "label": _("Valuation Rate"),
            "fieldtype": "Currency",
            "reqd": 1,
        },
        {
            "fieldname": "balance_qty",
            "label": _("Balance Qty"),
            "fieldtype": "Int",
            "reqd": 1,
        },
    ]
    return columns


def get_data(filters):
    Sle = frappe.qb.DocType("Stock Ledger Entry")
    query = frappe.qb.from_(Sle).select("*")

    if filters.get("To Date") and filters.get("From Date"):
        query = query.where(Sle.posting_date[filters.from_date : filters.to_date])

    for condition in ["Warehouse", "Item"]:
        if filters.get(condition):
            query = query.where((Sle[condition] == filters.get(condition)))

    sles = query.run(as_dict=True, debug=True)

    for sle in sles:
        prev_sles = frappe.db.get_all(
            "Stock Ledger Entry",
            filters={
                "posting_time": ("<=", sle.posting_time),
                "item": sle.item,
                "warehouse": sle.warehouse,
            },
            fields=["qty_change"],
        )
        print("prev_sles", prev_sles)
        balance_qty = sum(prev_sle.qty_change for prev_sle in prev_sles)
        sle.balance_qty = balance_qty

    return sles
