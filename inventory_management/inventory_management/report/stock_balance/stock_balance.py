# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
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
            "fieldtype": "Float",
            "reqd": 1,
        },
        {
            "fieldname": "balance_qty",
            "label": _("Balance Qty"),
            "fieldtype": "Float",
            "reqd": 1,
        },
        {
            "fieldname": "valuation_rate",
            "label": _("Valuation Rate"),
            "fieldtype": "Currency",
            "reqd": 1,
        },
        {
            "fieldname": "posting_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "reqd": 1,
        },
        {
            "fieldname": "posting_time",
            "label": _("Time"),
            "fieldtype": "Time",
            "reqd": 1,
        },
    ]
    return columns


def get_data(filters: dict):
    Sle = frappe.qb.DocType("Stock Ledger Entry")
    query = frappe.qb.from_(Sle).select(
        Sle.item,
        Sle.warehouse,
        Sle.qty_change,
        Sle.valuation_rate,
        Sle.posting_date,
        Sle.posting_time
	)

    if filters.get("to_date") and filters.get("from_date"):
        query = query.where(Sle.posting_date[filters["from_date"] : filters["to_date"]])

    for condition in ["warehouse", "item"]:
        if filters.get(condition):
            query = query.where((Sle[condition] == filters.get(condition)))

    sles = get_sles_with_balance_qty(query.run(as_dict=True, debug=True))

    return sles


def get_sles_with_balance_qty(sles: list):
    for sle in sles:
        balance_qty = get_balance_qty_for_sle(sle)
        sle.balance_qty = balance_qty

    return sles


def get_balance_qty_for_sle(sle: dict) -> float:
    prev_sles = frappe.db.get_all(
        "Stock Ledger Entry",
        filters={
            "posting_time": ("<=", sle.posting_time),
            "item": sle.item,
            "warehouse": sle.warehouse,
        },
        fields=["qty_change", "item", "warehouse"],
    )

    balance_qty = sum(prev_sle.qty_change for prev_sle in prev_sles)

    return balance_qty
