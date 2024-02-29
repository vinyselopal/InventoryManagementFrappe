# Copyright (c) 2024, Viny Selopal and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from inventory_management.inventory_management.report.stock_ledger.stock_ledger import (
    get_data,
)
from inventory_management.inventory_management.doctype.stock_entry.test_stock_entry import (
    create_test_parent_child_warehouses,
    create_test_item,
    create_test_stock_entry,
)
from frappe.utils import today
from datetime import timedelta, datetime


class TestStockLedgerReport(FrappeTestCase):
    def setUp(self):
        frappe.db.delete("Stock Entry")
        frappe.db.delete("Stock Ledger Entry")
        frappe.db.delete("Warehouse")
        frappe.db.delete("Item")
        frappe.db.delete("Stock Entry Item")

    def test_get_data(self):
        parent_warehouse, child_warehouse = create_test_parent_child_warehouses()

        item1 = create_test_item("ITEM-001", "child_warehouse", 1, 100)
        item2 = create_test_item("ITEM-002", "parent_warehouse", 1, 200)

        stock_entry_item1 = {
            "item": item1.name,
            "qty": 1,
            "rate": 300,
            "source_warehouse": child_warehouse,
            "target_warehouse": parent_warehouse,
            "name": "item1_ledger_entry",
        }

        create_test_stock_entry([stock_entry_item1], "Transfer")

        filters = {
            "from_date": get_relative_date(today(), 1),
            "to_date": get_relative_date(today(), 2),
        }

        data = get_data(filters)
        self.assertEqual(data, [])


def get_relative_date(date, day_difference):
    return (
        datetime.strptime(date, "%Y-%m-%d") + timedelta(days=day_difference)
    ).strftime("%Y-%m-%d")
