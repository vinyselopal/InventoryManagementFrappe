import frappe
from frappe.tests.utils import FrappeTestCase
from inventory_management.inventory_management.report.stock_balance.stock_balance import (
    get_balance_qty_for_sle,
)
from inventory_management.inventory_management.doctype.stock_entry.test_stock_entry import (
    create_test_item,
    create_test_stock_entry,
)


class TestStockBalanceReport(FrappeTestCase):
    def setUp(self):
        frappe.db.delete("Stock Entry")
        frappe.db.delete("Stock Ledger Entry")
        frappe.db.delete("Warehouse")
        frappe.db.delete("Item")
        frappe.db.delete("Stock Entry Item")

    def test_get_balance_qty_for_sle(self):
        wh1, wh2 = create_test_warehouses()

        item1 = create_test_item("ITEM-001", "wh1", 3, 100)

        stock_entry_item1 = {
            "item": item1.name,
            "qty": 1,
            "rate": 300,
            "source_warehouse": wh1,
            "target_warehouse": wh2,
            "name": "item1_ledger_entry",
        }

        create_test_stock_entry([stock_entry_item1], "Transfer")

        last_sle = frappe.db.get_all(
            "Stock Ledger Entry",
            filters={"item": item1.name, "warehouse": wh1},
            order_by="posting_time desc",
            fields=["item", "warehouse", "qty_change", "posting_time"],
        )[0]

        balance_qty = get_balance_qty_for_sle(last_sle)

        self.assertEqual(balance_qty, 2)


def create_test_warehouses():
    wh1 = frappe.new_doc("Warehouse")
    wh1.warehouse_name = "wh1"
    wh1.insert(ignore_if_duplicate=True)

    wh2 = frappe.new_doc("Warehouse")
    wh2.warehouse_name = "wh2"
    wh2.insert(ignore_if_duplicate=True)

    return wh1.name, wh2.name
