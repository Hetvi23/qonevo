// Copyright (c) 2024, Qonevo and contributors
// For license information, please see license.txt

// Override helpdesk Vue functionality for qonevo
(function() {
    'use strict';
    
    // Wait for Frappe to be ready
    function initializeHelpdeskOverrides() {
        console.log('Qonevo Helpdesk Override: Starting...');
        
        // Override API methods first
        overrideAPIMethods();
        
        // Then try to override the Vue store
        setTimeout(() => {
            overrideTicketStatusStore();
        }, 1000);
        
        // Also try again after a longer delay
        setTimeout(() => {
            overrideTicketStatusStore();
        }, 3000);
    }
    
    // Try multiple initialization methods
    if (typeof frappe !== 'undefined') {
        if (frappe.ready) {
            frappe.ready(initializeHelpdeskOverrides);
        } else {
            // Frappe is loaded but ready might not be available
            setTimeout(initializeHelpdeskOverrides, 1000);
        }
    } else {
        // Fallback: wait for DOM to be ready
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(initializeHelpdeskOverrides, 2000);
        });
    }
    
    function overrideTicketStatusStore() {
        console.log('Qonevo Helpdesk Override: Attempting to override ticket status store...');
        
        // Method 1: Try to find and override the existing store
        if (window.frappe && window.frappe.helpdesk && window.frappe.helpdesk.ticketStatusStore) {
            console.log('Qonevo Helpdesk Override: Found existing store, extending it...');
            const store = window.frappe.helpdesk.ticketStatusStore;
            
            // Extend options with custom statuses
            if (store.options) {
                const newOptions = [
                    ...store.options,
                    'Engineer Alligned',
                    'Spare Requested',
                    'Hold',
                    'Reopen'
                ];
                store.options = newOptions;
                console.log('Qonevo Helpdesk Override: Extended options:', store.options);
            }
            
            // Extend color mappings
            if (store.colorMap) {
                store.colorMap = {
                    ...store.colorMap,
                    'Engineer Alligned': 'blue',
                    'Spare Requested': 'orange',
                    'Hold': 'yellow',
                    'Reopen': 'purple'
                };
            }
            
            // Extend text color mappings
            if (store.textColorMap) {
                store.textColorMap = {
                    ...store.textColorMap,
                    'Engineer Alligned': 'white',
                    'Spare Requested': 'white',
                    'Hold': 'black',
                    'Reopen': 'white'
                };
            }
            
            // Extend state active mappings
            if (store.stateActive) {
                store.stateActive = [
                    ...store.stateActive,
                    'Reopen'
                ];
            }
        }
        
        // Method 2: Try to override Pinia store if available
        if (window.Pinia && window.Pinia.defineStore) {
            console.log('Qonevo Helpdesk Override: Found Pinia, attempting to override...');
            
            // Store the original defineStore
            const originalDefineStore = window.Pinia.defineStore;
            
            // Override defineStore
            window.Pinia.defineStore = function(id, setup) {
                if (id === 'ticketStatus') {
                    console.log('Qonevo Helpdesk Override: Intercepting ticketStatus store creation...');
                    
                    return originalDefineStore(id, () => {
                        const store = setup();
                        
                        // Extend options with custom statuses
                        if (store.options) {
                            store.options = [
                                ...store.options,
                                'Engineer Alligned',
                                'Spare Requested',
                                'Hold',
                                'Reopen'
                            ];
                        }
                        
                        // Extend color mappings
                        if (store.colorMap) {
                            store.colorMap = {
                                ...store.colorMap,
                                'Engineer Alligned': 'blue',
                                'Spare Requested': 'orange',
                                'Hold': 'yellow',
                                'Reopen': 'purple'
                            };
                        }
                        
                        // Extend text color mappings
                        if (store.textColorMap) {
                            store.textColorMap = {
                                ...store.textColorMap,
                                'Engineer Alligned': 'white',
                                'Spare Requested': 'white',
                                'Hold': 'black',
                                'Reopen': 'white'
                            };
                        }
                        
                        // Extend state active mappings
                        if (store.stateActive) {
                            store.stateActive = [
                                ...store.stateActive,
                                'Reopen'
                            ];
                        }
                        
                        console.log('Qonevo Helpdesk Override: Store created with custom statuses');
                        return store;
                    });
                }
                
                return originalDefineStore(id, setup);
            };
        }
        
        // Method 3: Try to find the store in the DOM or global scope
        if (window.frappe && window.frappe.helpdesk) {
            // Look for any store-like objects
            for (let key in window.frappe.helpdesk) {
                if (key.includes('ticket') || key.includes('status')) {
                    const obj = window.frappe.helpdesk[key];
                    if (obj && obj.options && Array.isArray(obj.options)) {
                        console.log('Qonevo Helpdesk Override: Found potential store:', key);
                        
                        // Extend options
                        obj.options = [
                            ...obj.options,
                            'Engineer Alligned',
                            'Spare Requested',
                            'Hold',
                            'Reopen'
                        ];
                        
                        // Extend color mappings if they exist
                        if (obj.colorMap) {
                            obj.colorMap = {
                                ...obj.colorMap,
                                'Engineer Alligned': 'blue',
                                'Spare Requested': 'orange',
                                'Hold': 'yellow',
                                'Reopen': 'purple'
                            };
                        }
                    }
                }
            }
        }
    }
    
    function overrideAPIMethods() {
        console.log('Qonevo Helpdesk Override: Setting up API method overrides...');
        
        // Override frappe.call to intercept specific API calls
        const originalFrappeCall = window.frappe.call;
        
        window.frappe.call = function(options) {
            // Intercept specific API calls and redirect them
            if (options.method === 'helpdesk.api.doc.get_status_counts') {
                console.log('Qonevo Helpdesk Override: Redirecting get_status_counts to qonevo.api.get_status_counts');
                options.method = 'qonevo.api.get_status_counts';
            } else if (options.method === 'helpdesk.api.doc.get_list_data') {
                console.log('Qonevo Helpdesk Override: Redirecting get_list_data to qonevo.api.get_list_data');
                options.method = 'qonevo.api.get_list_data';
            } else if (options.method === 'helpdesk.api.doc.get_filterable_fields') {
                console.log('Qonevo Helpdesk Override: Redirecting get_filterable_fields to qonevo.api.get_filterable_fields');
                options.method = 'qonevo.api.get_filterable_fields';
            } else if (options.method === 'helpdesk.api.doc.get_quick_filters') {
                console.log('Qonevo Helpdesk Override: Redirecting get_quick_filters to qonevo.api.get_quick_filters');
                options.method = 'qonevo.api.get_quick_filters';
            }
            
            return originalFrappeCall.call(this, options);
        };
        
        // Add custom API methods to frappe.qonevo.helpdesk
        if (!window.frappe.qonevo) {
            window.frappe.qonevo = {};
        }
        
        if (!window.frappe.qonevo.helpdesk) {
            window.frappe.qonevo.helpdesk = {};
        }
        
        window.frappe.qonevo.helpdesk.getTicketHistory = function(ticketName) {
            return window.frappe.call({
                method: 'qonevo.api.get_ticket_history',
                args: { ticket_name: ticketName }
            });
        };
        
        window.frappe.qonevo.helpdesk.getStatusCounts = function() {
            return window.frappe.call({
                method: 'qonevo.api.get_status_counts'
            });
        };
        
        window.frappe.qonevo.helpdesk.getListData = function(doctype, filters, kwargs) {
            return window.frappe.call({
                method: 'qonevo.api.get_list_data',
                args: { doctype: doctype, filters: filters, ...kwargs }
            });
        };
        
        window.frappe.qonevo.helpdesk.getFilterableFields = function(doctype) {
            return window.frappe.call({
                method: 'qonevo.api.get_filterable_fields',
                args: { doctype: doctype }
            });
        };
        
        window.frappe.qonevo.helpdesk.getQuickFilters = function(doctype) {
            return window.frappe.call({
                method: 'qonevo.api.get_quick_filters',
                args: { doctype: doctype }
            });
        };
    }
    
    function addCustomComponents() {
        console.log('Qonevo Helpdesk Override: Adding custom components...');
        
        // Add any custom components if needed
        // This can be used to inject custom Vue components or modify existing ones
    }
    
    // Also try to run the override when the page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(() => {
                overrideTicketStatusStore();
            }, 2000);
        });
    } else {
        setTimeout(() => {
            overrideTicketStatusStore();
        }, 2000);
    }
    
    // Try again after a longer delay to catch late-loading components
    setTimeout(() => {
        overrideTicketStatusStore();
    }, 5000);
    
    console.log('Qonevo Helpdesk Override: Script loaded successfully');
})(); 