# Copyright (c) 2024, Viny Selopal and Contributors
# See license.txt

from frappe.tests.utils import FrappeTestCase
import frappe
from frappe.utils import today

class TestStockEntry(FrappeTestCase):
    def test_stock_entry(self):
        parent_warehouse, child_warehouse = create_test_parent_child_warehouses()

        item1 = create_test_item("nord", "child_warehouse", 2, 4000)

        stock_entry_item1 = {
            "item": item1.name,
            "qty": 1,
            "rate": 3000,
            "source_warehouse": child_warehouse,
            "target_warehouse": parent_warehouse,
            "name": "nord_ledger_entry",
        }

        create_test_stock_entry_for_transfer([stock_entry_item1])

        all_sles = frappe.db.get_all("Stock Ledger Entry", fields=["valuation_rate", "item", "warehouse", "qty_change"])

        for sle in all_sles:
            print("sle", sle.valuation_rate, sle.warehouse, sle.item)

        sle_valuation_rate = frappe.db.get_value(
            doctype="Stock Ledger Entry",
            filters={"item": item1.name},
            fieldname="valuation_rate",
            order_by="creation desc",
        )

        self.assertEqual(sle_valuation_rate, 5000)


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
    item, opening_warehouse, opening_qty, opening_valuation_rate
) -> dict:
    item_doc = frappe.new_doc("Item")
    item_doc.item_code = item
    item_doc.opening_warehouse = opening_warehouse
    item_doc.opening_qty = opening_qty
    item_doc.opening_valuation_rate = opening_valuation_rate
    item_doc.insert(ignore_if_duplicate=True)

    return item_doc


def create_test_sle_item(
    item, sle_qty, sle_rate, src_warehouse, target_warehouse, sle_name
) -> dict:
    return {
        "item": item.name,
        "qty": sle_qty,
        "rate": sle_rate,
        "source_warehouse": src_warehouse,
        "target_warehouse": target_warehouse,
        "name": sle_name,
    }


def create_test_stock_entry_for_transfer(stock_entry_items):
    doc = frappe.new_doc("Stock Entry")
    doc.date = today()
    doc.type = "Transfer"

    for item in stock_entry_items:
        print(item)
        doc.append("stock_entry_items", item)

    doc.insert(ignore_if_duplicate=True)
    doc.submit()
