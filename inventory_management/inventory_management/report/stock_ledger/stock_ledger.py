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
            "fieldtype": "Int",
            "reqd": 1,
        },
        {
            "fieldname": "in_out_rate",
            "label": _("In Out Rate"),
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
            "fieldname": "stock_entry",
            "label": _("Stock Entry"),
            "fieldtype": "Link",
            "options": "Stock Entry",
            "reqd": 1,
        },
        {
            "fieldname": "posting_date",
            "label": _("Posting Date"),
            "fieldtype": "Date",
            "reqd": 1,
        },
        {
            "fieldname": "posting_time",
            "label": _("Posting Time"),
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
        Sle.in_out_rate,
        Sle.valuation_rate,
        Sle.stock_entry,
        Sle.posting_date,
        Sle.posting_time,
	)

    if filters.get("to_date") and filters.get("from_date"):
        query = query.where(Sle.posting_date[filters["from_date"] : filters["to_date"]])

    if filters.get("stock_entry"):
        query = query.where(Sle.stock_entry == filters["stock_entry"])

    for condition in ["warehouse", "item"]:
        if filters.get(condition):
            query = query.where((Sle[condition] == filters.get(condition)))

    sles = query.run(as_dict=True)

    return sles
