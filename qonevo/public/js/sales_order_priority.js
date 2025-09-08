frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        calculateDeliveryWeek(frm);
    },
    delivery_date: function(frm) {
        calculateDeliveryWeek(frm);
    }
});


function calculateDeliveryWeek(frm) {
    if (frm.doc.delivery_date) {
        const deliveryDate = new Date(frm.doc.delivery_date);
        const weekStart = new Date(deliveryDate);
        weekStart.setDate(deliveryDate.getDate() - deliveryDate.getDay());
        
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6);
        
        const weekLabel = `${weekStart.toLocaleDateString()} - ${weekEnd.toLocaleDateString()}`;
        frm.set_value('custom_delivery_week', weekLabel);
    }
}

