// Copyright (c) 2025, Tati and contributors
// For license information, please see license.txt

frappe.ui.form.on('Skills', {
    hours_per_session: function(frm) {
        calculate_sessions(frm);
    },
    total_course_hours: function(frm) {
        calculate_sessions(frm);
    }
});

function calculate_sessions(frm) {
    let hours = frm.doc.hours_per_session || 0;
    let total_hours = frm.doc.total_course_hours || 0;
    
    if(hours > 0 && total_hours > 0) {
        frm.set_value('number_of_sessions', total_hours / hours);
    } else {
        frm.set_value('number_of_sessions', 0);
    }
}

