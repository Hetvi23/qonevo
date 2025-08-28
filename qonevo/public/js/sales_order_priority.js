// Sales Order Priority System
frappe.listview_settings['Sales Order'] = {
    add_fields: ["priority", "priority_status", "delivery_week"],
    get_indicator: function(doc) {
        if (doc.priority === "Urgent") {
            return [__("Urgent"), "red", "priority,=,Urgent"];
        } else if (doc.priority === "High") {
            return [__("High"), "orange", "priority,=,High"];
        } else if (doc.priority === "Medium") {
            return [__("Medium"), "blue", "priority,=,Medium"];
        } else if (doc.priority === "Low") {
            return [__("Low"), "gray", "priority,=,Low"];
        }
    }
};



// Form customization
frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        addPriorityIndicator(frm);
        calculateDeliveryWeek(frm);
    },
    
    priority: function(frm) {
        updatePriorityStatus(frm);
        highlightPriority(frm);
    },
    
    delivery_date: function(frm) {
        calculateDeliveryWeek(frm);
    }
});

function addPriorityIndicator(frm) {
    // Add priority indicator to sidebar
    if (frm.doc.priority) {
        const priorityColors = {
            "Urgent": "red",
            "High": "orange",
            "Medium": "blue",
            "Low": "gray"
        };
        
        const color = priorityColors[frm.doc.priority] || "gray";
        
        // Add to sidebar using the correct method
        if (frm.sidebar && frm.sidebar.add_badge) {
            frm.sidebar.add_badge(__("Priority"), frm.doc.priority, color);
        } else {
            // Fallback: add to the sidebar manually
            const sidebar = frm.page.sidebar;
            if (sidebar) {
                // Remove existing priority indicator if any
                sidebar.find('.priority-indicator').remove();
                
                // Create new priority indicator
                const priorityIndicator = $(`
                    <div class="priority-indicator" style="margin: 10px 0;">
                        <div class="text-muted small">Priority</div>
                        <span class="badge badge-${color}">${frm.doc.priority}</span>
                    </div>
                `);
                
                sidebar.append(priorityIndicator);
            }
        }
    }
}

function updatePriorityStatus(frm) {
    if (frm.doc.priority) {
        frm.set_value('priority_status', 'Pending');
    }
}

function highlightPriority(frm) {
    if (frm.doc.priority === "Urgent" || frm.doc.priority === "High") {
        // Add pulsing highlight effect
        frm.$wrapper.addClass('priority-highlight');
    } else {
        frm.$wrapper.removeClass('priority-highlight');
    }
}

function calculateDeliveryWeek(frm) {
    if (frm.doc.delivery_date) {
        const deliveryDate = new Date(frm.doc.delivery_date);
        const weekStart = new Date(deliveryDate);
        weekStart.setDate(deliveryDate.getDate() - deliveryDate.getDay());
        
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6);
        
        const weekLabel = `${weekStart.toLocaleDateString()} - ${weekEnd.toLocaleDateString()}`;
        frm.set_value('delivery_week', weekLabel);
    }
}

// Add CSS for priority highlighting
if (typeof frappe !== 'undefined' && frappe.ready) {
    frappe.ready(function() {
        $('<style>')
            .prop('type', 'text/css')
            .html(`
                .priority-highlight {
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
                    70% { box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); }
                    100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
                }
            `)
            .appendTo('head');
    });
} else {
    // Fallback: add CSS when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        const style = document.createElement('style');
        style.textContent = `
            .priority-highlight {
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
                70% { box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); }
                100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
            }
        `;
        document.head.appendChild(style);
    });
} 