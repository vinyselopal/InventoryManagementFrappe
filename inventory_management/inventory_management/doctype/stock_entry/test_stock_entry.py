# Copyright (c) 2024, Viny Selopal and Contributors
# See license.txt

from frappe.tests.utils import FrappeTestCase
import frappe
from frappe.utils import today

class TestStockEntry(FrappeTestCase):
    def test_stock_ledger_entry(self):
        parent_warehouse, child_warehouse = create_test_parent_child_warehouses()

        item1, stock_entry_item1 = create_test_item(
            "nord", "child_warehouse", 30, 1, 3000, child_warehouse, parent_warehouse, "nord_ledger_entry"
        )
        item2, stock_entry_item2 = create_test_item(
            "boat", "parent_warehouse", 20, 1, 5000, parent_warehouse, child_warehouse, "boat_ledger_entry"
        )

        create_test_stock_entry_for_transfer([stock_entry_item1, stock_entry_item2])
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


def create_test_item(
    item,
    opening_warehouse,
    opening_qty,
    sle_qty,
    sle_rate,
    source_warehouse,
    target_warehouse,
    sle_name
) -> dict:
    item_doc = frappe.new_doc("Item")
    item_doc.item_code = item
    item_doc.opening_warehouse = opening_warehouse
    item_doc.opening_qty = opening_qty
    item_doc.insert(ignore_if_duplicate=True)

    slei_doc = frappe._dict({
        "item": item_doc,
        "qty": sle_qty,
        "rate": sle_rate,
        "source_warehouse": source_warehouse,
        "target_warehouse": target_warehouse,
        "name": sle_name
    })

    return item_doc, slei_doc


def create_test_stock_entry_for_transfer(stock_entry_items):
    doc = frappe.new_doc("Stock Entry")
    doc.date = today()
    doc.type = "Transfer"

    for item in stock_entry_items:
        print(item)
        doc.append("items", item)

    doc.insert(ignore_if_duplicate=True)
    doc.submit()
