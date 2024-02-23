# Copyright (c) 2024, Viny Selopal and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from ..stock_entry.test_stock_entry import (
    create_test_parent_child_warehouses,
    create_test_item,
)


class TestItem(FrappeTestCase):
    def test_sle_valuation_rate_on_item_creation(self):
        create_test_parent_child_warehouses()

        item1 = create_test_item("nord", "child_warehouse", 30, 4000)
        item_valuation_rate = frappe.db.get_value(
            "Stock Ledger Entry", {"item": item1.name}, "valuation_rate"
        )

        self.assertEqual(item_valuation_rate, item1.opening_valuation_rate)
