# Copyright (c) 2024, Viny Selopal and Contributors
# See license.txt

from frappe.tests.utils import FrappeTestCase
import frappe
from frappe.utils import getdate, today, datetime
import datetime


class TestStockEntry(FrappeTestCase):
    def setUp(self):
        self.create_test_parent_child_warehouses()
        self.create_test_items()

    def tearDown(self):
        frappe.db.rollback()

    def testStockLedgerEntryFromStockEntry(self):
        self.create_test_stock_entry_for_transfer()
        stock_ledger_entry = frappe.get_doc(
            doctype="Stock Ledger Entry",
            posting_date=frappe.utils.getdate(),
            name="nord_ledger_entry",
            qty_change=1,
        )
        self.assertTrue(stock_ledger_entry)

    def create_test_parent_child_warehouses(self):
        parent_warehouse = frappe.new_doc("Warehouse")
        parent_warehouse.warehouse_name = "parent_warehouse"
        parent_warehouse.insert(ignore_if_duplicate=True)

        child_warehouse = frappe.new_doc("Warehouse")
        child_warehouse.warehouse_name = "child_warehouse"
        child_warehouse.parent_warehouse = "parent_warehouse"
        child_warehouse.insert(ignore_if_duplicate=True)

    def create_test_items(self):
        item1 = frappe.new_doc("Item")
        item1.item_code = "nord"
        item1.opening_warehouse = "child_warehouse"
        item1.opening_qty = 30

        item1.insert(ignore_if_duplicate=True)
        item2 = frappe.new_doc("Item")
        item2.item_code = "boat"
        item2.opening_warehouse = "parent_warehouse"
        item2.opening_qty = 20

        item2.insert(ignore_if_duplicate=True)

    def create_test_stock_entry_for_transfer(self):
        doc = frappe.new_doc("Stock Entry")
        doc.date = today()
        doc.type = "Transfer"

        doc.append(
            "items",
            {
                "item": datetime.datetime.strftime(datetime.date.today(), "%y-%m-%d")
                + "-"
                + "nord",
                "qty": 1,
                "rate": 3000,
                "name": "nord_ledger_entry",
                "source_warehouse": "child_warehouse",
                "target_Warehouse": "parent_warehouse",
            },
        )
        doc.append(
            "items",
            {
                "item": datetime.datetime.strftime(datetime.date.today(), "%y-%m-%d")
                + "-"
                + "boat",
                "qty": 1,
                "rate": 5000,
                "name": "boat_ledger_entry",
                "source_warehouse": "parent_warehouse",
                "target_Warehouse": "child_warehouse",
            },
        )
        doc.insert(ignore_if_duplicate=True)
        doc.submit()
