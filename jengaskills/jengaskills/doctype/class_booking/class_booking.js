// Copyright (c) 2025, Tati and contributors
// For license information, please see license.txt

frappe.ui.form.on("Class Booking", {
  refresh(frm) {
    
  },
});
frappe.ui.form.on('Class Session', {
    join_meet: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.google_meet_link) {
            // Extract the actual link if it's stored as HTML
            let match = row.google_meet_link.match(/href="([^"]+)"/);
            let url = match ? match[1] : row.google_meet_link;
            window.open(url, '_blank');
        } else {
            frappe.msgprint("No Google Meet link available for this session.");
        }
    }
});

