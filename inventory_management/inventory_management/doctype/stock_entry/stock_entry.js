// Copyright (c) 2024, Viny Selopal and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Entry', {
    refresh: function(frm) {
      frm.add_custom_button(__('View Ledger'), function(){
        frappe.set_route("query-report", "Stock Ledger", {"stock_entry": frm.doc.name})
    });
  }
});
