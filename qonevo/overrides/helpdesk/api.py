# Copyright (c) 2024, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cstr, cint, getdate, get_datetime, add_days, today, get_datetime_str
from frappe.utils.data import flt
import json

def get_status_counts():
    """Get ticket counts by status - Override for qonevo"""
    try:
        # Get all statuses including custom ones
        statuses = [
            "Open", "Replied", "Resolved", "Closed", 
            "Engineer Alligned", "Spare Requested"
        ]
        
        counts = {}
        for status in statuses:
            count = frappe.db.count("HD Ticket", {"status": status})
            counts[status] = count
        
        return counts
    except Exception as e:
        frappe.log_error(f"Error in get_status_counts: {str(e)}")
        return {}

def get_list_data(filters=None, **kwargs):
    """Override get_list_data to handle custom filters and OR logic"""
    try:
        # Handle filters parameter
        if isinstance(filters, str):
            if not filters or filters.strip() == "":
                filters = []
            else:
                try:
                    filters = json.loads(filters)
                except json.JSONDecodeError:
                    filters = []
        elif filters is None:
            filters = []
        
        # Ensure filters is a list
        if not isinstance(filters, list):
            filters = []
        
        # Handle OR filter logic
        if filters and len(filters) > 0 and isinstance(filters[0], list) and len(filters[0]) > 0:
            if filters[0][0] == "or":
                # Handle OR filter
                return handle_or_filter(filters, **kwargs)
        
        # Default behavior - call original method
        return call_original_get_list_data(filters, **kwargs)
        
    except Exception as e:
        frappe.log_error(f"Error in qonevo get_list_data override: {str(e)}")
        return call_original_get_list_data(filters, **kwargs)

def handle_or_filter(filters, **kwargs):
    """Handle OR filter logic by making multiple queries and merging results"""
    try:
        or_conditions = filters[0][1:]  # Get the OR conditions
        
        all_results = []
        total_count = 0
        
        for condition in or_conditions:
            if isinstance(condition, list) and len(condition) >= 3:
                # Create a new filter with this condition
                single_filter = [condition]
                
                # Call the original method with this single condition
                result = call_original_get_list_data(single_filter, **kwargs)
                
                if result and isinstance(result, dict):
                    if 'data' in result:
                        all_results.extend(result['data'])
                    if 'total_count' in result:
                        total_count += result['total_count']
        
        # Remove duplicates based on name
        seen_names = set()
        unique_results = []
        for item in all_results:
            if item.get('name') not in seen_names:
                seen_names.add(item.get('name'))
                unique_results.append(item)
        
        return {
            'data': unique_results,
            'total_count': len(unique_results)
        }
        
    except Exception as e:
        frappe.log_error(f"Error in handle_or_filter: {str(e)}")
        return call_original_get_list_data(filters, **kwargs)

def call_original_get_list_data(filters, **kwargs):
    """Call the original helpdesk get_list_data method"""
    try:
        # Import the original method
        from helpdesk.api.doc import get_list_data as original_get_list_data
        return original_get_list_data(filters, **kwargs)
    except ImportError:
        # Fallback if original method is not available
        frappe.log_error("Original helpdesk get_list_data method not found")
        return {'data': [], 'total_count': 0}

def get_ticket_history(ticket_name):
    """Get detailed ticket history including status transitions"""
    try:
        ticket = frappe.get_doc("HD Ticket", ticket_name)
        
        # Get status transitions from ticket activity
        activities = frappe.get_all(
            "HD Ticket Activity",
            filters={"ticket": ticket_name},
            fields=["*"],
            order_by="creation asc"
        )
        
        # Build status transition timeline
        status_transitions = []
        previous_status = "Created"
        
        for activity in activities:
            if activity.get('field') == 'status' and activity.get('value'):
                current_status = activity.get('value')
                status_transitions.append({
                    'from_status': previous_status,
                    'to_status': current_status,
                    'date': activity.get('creation'),
                    'user': activity.get('user')
                })
                previous_status = current_status
        
        # Get recent activities (excluding status changes)
        recent_activities = []
        for activity in activities:
            if activity.get('field') != 'status':
                recent_activities.append({
                    'field': activity.get('field'),
                    'old_value': activity.get('old_value'),
                    'new_value': activity.get('value'),
                    'date': activity.get('creation'),
                    'user': activity.get('user')
                })
        
        return {
            'status_transitions': status_transitions,
            'recent_activities': recent_activities
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_ticket_history: {str(e)}")
        return {'status_transitions': [], 'recent_activities': []} 