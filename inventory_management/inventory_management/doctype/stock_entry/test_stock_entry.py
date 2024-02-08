# Copyright (c) 2024, Viny Selopal and Contributors
# See license.txt

from frappe.tests.utils import FrappeTestCase
import frappe
from frappe.utils import today
from .stock_entry import MandatoryWarehouseMissing


class TestStockEntry(FrappeTestCase):
    def setUp(self):
        frappe.db.delete("Stock Entry")
        frappe.db.delete("Stock Ledger Entry")
        frappe.db.delete("Warehouse")
        frappe.db.delete("Item")
        frappe.db.delete("Stock Entry Item")

    def test_stock_entry(self):
        parent_warehouse, child_warehouse = create_test_parent_child_warehouses()

        item1 = create_test_item("nord", "child_warehouse", 2, 4000)

        all_sles = frappe.db.get_all(
            "Stock Ledger Entry",
            fields=["valuation_rate", "item", "warehouse", "qty_change"],
        )

        for sle in all_sles:
            print("sle", sle.valuation_rate, sle.warehouse, sle.item)

        stock_entry_item1 = {
            "item": item1.name,
            "qty": 1,
            "rate": 3000,
            "source_warehouse": child_warehouse,
            "target_warehouse": parent_warehouse,
            "name": "nord_ledger_entry",
        }

        create_test_stock_entry([stock_entry_item1], "Transfer")

        sle_valuation_rate = frappe.db.get_value(
            doctype="Stock Ledger Entry",
            filters={"item": item1.name},
            fieldname="valuation_rate",
            order_by="creation desc",
        )

        self.assertEqual(sle_valuation_rate, 5000)

    def test_invalid_warehouse_for_consume_stock_entry(self):
        parent_warehouse, child_warehouse = create_test_parent_child_warehouses()

        item1 = create_test_item("nord", "child_warehouse", 2, 4000)

        stock_entry_item1 = {
            "item": item1.name,
            "qty": 1,
            "rate": 3000,
            "name": "nord_ledger_entry",
        }

        with self.assertRaises(MandatoryWarehouseMissing):
            create_test_stock_entry([stock_entry_item1], "Consume")


def create_test_parent_child_warehouses() -> tuple[str, str]:
    parent_warehouse = frappe.new_doc("Warehouse")
    parent_warehouse.warehouse_name = "parent_warehouse"
    parent_warehouse.is_group = 1
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


def create_test_stock_entry(stock_entry_items, type):
    doc = frappe.new_doc("Stock Entry")
    doc.date = today()
    doc.type = type

    for item in stock_entry_items:
        print(item)
        doc.append("stock_entry_items", item)

    doc.insert(ignore_if_duplicate=True)
    doc.submit()
