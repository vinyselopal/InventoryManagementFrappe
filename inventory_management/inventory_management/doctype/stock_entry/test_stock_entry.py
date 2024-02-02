# Copyright (c) 2024, Viny Selopal and Contributors
# See license.txt

from frappe.tests.utils import FrappeTestCase
import frappe
from frappe.utils import today, datetime
import datetime


class TestStockEntry(FrappeTestCase):
    def test_stock_ledger_entry(self):
        parent_warehouse, child_warehouse = self.create_test_parent_child_warehouses()
        item1 = create_test_item("nord", "child_warehouse", 30)
        item2 = create_test_item("boat", "parent_warehouse", 20)

        self.create_test_stock_entry_for_transfer()
        stock_ledger_entry = frappe.get_doc(
            doctype="Stock Ledger Entry",
            posting_date=frappe.utils.getdate(),
            item=item1.name,
            qty_change=1,
        )
        self.assertTrue(stock_ledger_entry)
        # check actual valuation rate for each SLE


def create_test_parent_child_warehouses() -> tuple[str, str]:
    parent_warehouse = frappe.new_doc("Warehouse")
    parent_warehouse.warehouse_name = "parent_warehouse"
    parent_warehouse.insert(ignore_if_duplicate=True)

    child_warehouse = frappe.new_doc("Warehouse")
    child_warehouse.warehouse_name = "child_warehouse"
    child_warehouse.parent_warehouse = "parent_warehouse"
    child_warehouse.insert(ignore_if_duplicate=True)

    return parent_warehouse.name, child_warehouse.name


def create_test_item(item, opening_warehouse, opening_qty) -> dict:
    item_doc = frappe.new_doc("Item")
    item_doc.item_code = item
    item_doc.opening_warehouse = opening_warehouse
    item_doc.opening_qty = opening_qty
    item_doc.insert(ignore_if_duplicate=True)

    return item_doc


def create_test_stock_entry_for_transfer():
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
