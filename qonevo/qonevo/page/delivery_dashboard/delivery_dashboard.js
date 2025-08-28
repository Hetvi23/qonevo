// Copyright (c) 2025, Qonevo and contributors
// License: MIT. See LICENSE

if (typeof frappe !== 'undefined' && frappe.ready) {
    frappe.ready(function() {
        // Dashboard page JavaScript
        console.log("Delivery Dashboard loaded");
        
        // Add any dashboard-specific functionality here
        // For example, refresh data, handle user interactions, etc.
    });
} else {
    // Fallback: wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log("Delivery Dashboard loaded (fallback)");
        
        // Add any dashboard-specific functionality here
        // For example, refresh data, handle user interactions, etc.
    });
} 