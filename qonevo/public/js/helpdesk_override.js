function initializeHelpdeskOverride() {
    console.log("✅ helpdesk_override.js loaded!");
    const interval = setInterval(() => {
        if (window.frappe && window.frappe.helpdesk && window.frappe.helpdesk.ticketStatusStore) {
            const store = window.frappe.helpdesk.ticketStatusStore;
            console.log("✅ ticketStatusStore found", store);

            if (!store.statuses.includes("Engineer Aligned")) {
                store.statuses.push("Engineer Aligned", "Spare Requested");
            }

            store.textColorMap["Engineer Aligned"] = "text-purple-500";
            store.textColorMap["Spare Requested"] = "text-teal-500";

            clearInterval(interval);
        }
    }, 500);
}

// Try multiple initialization methods
if (typeof frappe !== 'undefined') {
    if (frappe.ready) {
        frappe.ready(initializeHelpdeskOverride);
    } else {
        // Frappe is loaded but ready might not be available
        setTimeout(initializeHelpdeskOverride, 1000);
    }
} else {
    // Fallback: wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(initializeHelpdeskOverride, 2000);
    });
}
