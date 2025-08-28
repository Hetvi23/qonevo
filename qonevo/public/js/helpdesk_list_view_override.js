// Copyright (c) 2024, Qonevo and contributors
// For license information, please see license.txt

// Override helpdesk list view functionality for qonevo
(function() {
    'use strict';
    
    console.log('Qonevo List View Override: Starting...');
    
    // Wait for Frappe to be ready
    function initializeOverrides() {
        console.log('Qonevo List View Override: Setting up overrides...');
        
        // Override list view configuration
        overrideListViewConfiguration();
        
        // Add custom columns and filters
        addCustomColumns();
        addCustomFilters();
    }
    
    // Try multiple initialization methods
    if (typeof frappe !== 'undefined') {
        if (frappe.ready) {
            frappe.ready(initializeOverrides);
        } else {
            // Frappe is loaded but ready might not be available
            setTimeout(initializeOverrides, 1000);
        }
    } else {
        // Fallback: wait for DOM to be ready
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(initializeOverrides, 2000);
        });
    }
    
    function overrideListViewConfiguration() {
        console.log('Qonevo List View Override: Setting up list view configuration...');
        
        // Wait for frappe.views to be available
        if (!window.frappe || !window.frappe.views) {
            console.log('Qonevo List View Override: frappe.views not available yet, retrying...');
            setTimeout(overrideListViewConfiguration, 1000);
            return;
        }
        
        // Initialize default fields if not exists
        if (!window.frappe.views.ListView) {
            console.log('Qonevo List View Override: ListView not available yet, retrying...');
            setTimeout(overrideListViewConfiguration, 1000);
            return;
        }
        
        if (!window.frappe.views.ListView.default_fields) {
            window.frappe.views.ListView.default_fields = {};
        }
        
        if (!window.frappe.views.ListView.default_fields['HD Ticket']) {
            window.frappe.views.ListView.default_fields['HD Ticket'] = [];
        }
        
        // Add custom fields to default fields
        const customFields = [
            'opening_date',
            'resolution_date', 
            'resolution_by',
            'sla',
            'agreement_status'
        ];
        
        customFields.forEach(field => {
            if (!window.frappe.views.ListView.default_fields['HD Ticket'].includes(field)) {
                window.frappe.views.ListView.default_fields['HD Ticket'].push(field);
            }
        });
        
        // Initialize column config if not exists
        if (!window.frappe.views.ListView.column_config) {
            window.frappe.views.ListView.column_config = {};
        }
        
        if (!window.frappe.views.ListView.column_config['HD Ticket']) {
            window.frappe.views.ListView.column_config['HD Ticket'] = {};
        }
        
        // Add custom column configurations
        const columnConfig = {
            'opening_date': {
                label: 'Start Date',
                fieldtype: 'Date',
                width: 100
            },
            'resolution_date': {
                label: 'End Date',
                fieldtype: 'Datetime',
                width: 120
            },
            'resolution_by': {
                label: 'Tentative End Date',
                fieldtype: 'Datetime',
                width: 120
            },
            'sla': {
                label: 'SLA',
                fieldtype: 'Link',
                width: 80
            },
            'agreement_status': {
                label: 'SLA Status',
                fieldtype: 'Select',
                width: 100
            }
        };
        
        // Merge column config
        window.frappe.views.ListView.column_config['HD Ticket'] = {
            ...window.frappe.views.ListView.column_config['HD Ticket'],
            ...columnConfig
        };
        
        console.log('Qonevo List View Override: List view configuration updated');
    }
    
    function addCustomColumns() {
        console.log('Qonevo List View Override: Adding custom columns...');
        
        // Override the get_columns method if it exists
        if (window.frappe.views.ListView && window.frappe.views.ListView.prototype) {
            const originalGetColumns = window.frappe.views.ListView.prototype.get_columns;
            
            window.frappe.views.ListView.prototype.get_columns = function() {
                const columns = originalGetColumns ? originalGetColumns.call(this) : [];
                
                // Add custom columns for HD Ticket
                if (this.doctype === 'HD Ticket') {
                    const customColumns = [
                        {
                            fieldname: 'opening_date',
                            label: 'Start Date',
                            fieldtype: 'Date',
                            width: 100
                        },
                        {
                            fieldname: 'resolution_date',
                            label: 'End Date', 
                            fieldtype: 'Datetime',
                            width: 120
                        },
                        {
                            fieldname: 'resolution_by',
                            label: 'Tentative End Date',
                            fieldtype: 'Datetime',
                            width: 120
                        },
                        {
                            fieldname: 'sla',
                            label: 'SLA',
                            fieldtype: 'Link',
                            width: 80
                        },
                        {
                            fieldname: 'agreement_status',
                            label: 'SLA Status',
                            fieldtype: 'Select',
                            width: 100
                        }
                    ];
                    
                    // Add custom columns if they don't already exist
                    customColumns.forEach(customCol => {
                        const exists = columns.some(col => col.fieldname === customCol.fieldname);
                        if (!exists) {
                            columns.push(customCol);
                        }
                    });
                }
                
                return columns;
            };
        }
        
        console.log('Qonevo List View Override: Custom columns added');
    }
    
    function addCustomFilters() {
        console.log('Qonevo List View Override: Adding custom filters...');
        
        // Override the get_filter_options method if it exists
        if (window.frappe.views.ListView && window.frappe.views.ListView.prototype) {
            const originalGetFilterOptions = window.frappe.views.ListView.prototype.get_filter_options;
            
            window.frappe.views.ListView.prototype.get_filter_options = function() {
                const filterOptions = originalGetFilterOptions ? originalGetFilterOptions.call(this) : {};
                
                // Add custom filter options for HD Ticket
                if (this.doctype === 'HD Ticket') {
                    const customFilters = {
                        'opening_date': {
                            label: 'Start Date',
                            fieldtype: 'Date'
                        },
                        'resolution_date': {
                            label: 'End Date',
                            fieldtype: 'Datetime'
                        },
                        'resolution_by': {
                            label: 'Tentative End Date',
                            fieldtype: 'Datetime'
                        },
                        'agreement_status': {
                            label: 'SLA Status',
                            fieldtype: 'Select'
                        },
                        'sla': {
                            label: 'SLA',
                            fieldtype: 'Link'
                        }
                    };
                    
                    // Merge custom filters
                    filterOptions = {
                        ...filterOptions,
                        ...customFilters
                    };
                }
                
                return filterOptions;
            };
        }
        
        console.log('Qonevo List View Override: Custom filters added');
    }
    
    // Also try to run the overrides when the page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(() => {
                overrideListViewConfiguration();
                addCustomColumns();
                addCustomFilters();
            }, 2000);
        });
    } else {
        setTimeout(() => {
            overrideListViewConfiguration();
            addCustomColumns();
            addCustomFilters();
        }, 2000);
    }
    
    // Try again after a longer delay to catch late-loading components
    setTimeout(() => {
        overrideListViewConfiguration();
        addCustomColumns();
        addCustomFilters();
    }, 5000);
    
    console.log('Qonevo List View Override: Script loaded successfully');
})(); 