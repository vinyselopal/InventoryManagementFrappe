from frappe.tests.utils import FrappeTestCase
import frappe
from frappe.utils import getdate

class TestEvent(FrappeTestCase):

    def setUp(self):
        self.create_test_parent_child_warehouses()
        self.create_test_items()
    
    def tearDown(self):
        pass

    def create_test_parent_child_warehouses(self):
        parent_warehouse = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": "parent_warehouse"
            }).insert()
        print(parent_warehouse)
        frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": "child_warehouse",
            "parent_warehouse": "parent_warehouse"
        }).insert()

    def create_test_items(self):
        item1 = frappe.new_doc("Item")
        item1.update({
            "item_code": "nord",
            "opening_warehouse": "child_warehouse",
            "opening_qty": 30
        })

        item2 = frappe.new_doc("Item")
        item2.update({
            "item_code": "boat",
            "opening_warehouse": "parent_warehouse",
            "opening_qty": 20
        })

    def create_test_stock_entry_for_transfer(self):
        doc = frappe.new_doc("Stock Entry")    
        doc.update({
            "date": getdate("22-01-2024"),
            "time": "3:15:00",
            "type": "Transfer",
        })

        doc.append(
            "items",
                {
                    "item": "nord",
                    "qty": 1,
                    "rate": 3000,
                    "name": "nord_ledger_entry",
                    "source_warehouse": "child_warehouse",
                    "target_Warehouse": "parent_warehouse",
                }
        )
        doc.append(
            "items",
                {
                    "item": "boat",
                    "qty": 1,
                    "rate": 5000,
                    "name": "boat_ledger_entry",
                    "source_warehouse": "parent_warehouse",
                    "target_Warehouse": "child_warehouse",
                }
        )

    def testStockLedgerEntryFromStockEntry(self):
        self.create_test_stock_entry_for_transfer()
        stock_ledger_entry = frappe.get_doc(doctype="Stock Ledger Entry", posting_date=frappe.utils.getdate(), name="nord_ledger_entry", qty_change=1)
        self.assertTrue(stock_ledger_entry)


    