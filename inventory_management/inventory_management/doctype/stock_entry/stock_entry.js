// Copyright (c) 2024, Viny Selopal and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stock Entry", {
  refresh: function (frm) {
    frm.add_custom_button(__("View Ledger"), function () {
      frappe.set_route("query-report", "Stock Ledger", {
        stock_entry: frm.doc.name,
      });
    });
  },
});

frappe.ui.form.on("Stock Entry Item", {
  item: (frm, cdt, cdn) => onFieldChange(frm, cdt, cdn),
  source_warehouse: (frm, cdt, cdn) => onFieldChange(frm, cdt, cdn),
});

function onFieldChange(frm, cdt, cdn) {
  const child_doc = frappe.get_doc(cdt, cdn);
  if (
    frm.doc.type == "Consume" &&
    child_doc.item &&
    child_doc.source_warehouse
  ) {
    frm.call(
      "get_last_sle_for_item_warehouse",
      {
        item: child_doc.item,
        warehouse: child_doc.source_warehouse
      }
    ).then(r => {
      child_doc.rate = r.message
      frm.refresh()
    });
  }
}
