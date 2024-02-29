# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder.functions import Sum


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
            "label": _("Posting Date"),
            "fieldtype": "Date",
            "reqd": 1,
        },
    ]
    return columns


def get_data(filters: dict):
    from_date = frappe.format(filters.get("from_date"), {"date_format": "yyyy-MM-dd"})
    to_date = frappe.format(filters.get("to_date"), {"date_format": "yyyy-MM-dd"})

    stock_balance = frappe.db.sql(
        f"""
        SELECT
            item,
            warehouse,
            SUM(qty_change) AS balance_qty,
            posting_date
        FROM
            `tabStock Ledger Entry`
        WHERE
            posting_date >= '{from_date}' AND posting_date <= '{to_date}'
        GROUP BY
            item, warehouse, posting_date
        ORDER BY
            posting_date DESC
    """,
        as_dict=True,
    )

    print("stock balance", stock_balance)
    return stock_balance
