import frappe
from frappe import _
import json
from datetime import datetime, timedelta

@frappe.whitelist()
def get_status_counts():
    """Get ticket counts by status - Direct API endpoint"""
    try:
        # Get all statuses including custom ones
        statuses = [
            "Open", "Replied", "Resolved", "Closed", 
            "Engineer Alligned", "Spare Requested", "Hold", "Reopen"
        ]
        
        counts = {}
        for status in statuses:
            count = frappe.db.count("HD Ticket", {"status": status})
            counts[status] = count
        
        return counts
    except Exception as e:
        frappe.log_error(f"Error in qonevo get_status_counts: {str(e)}")
        return {}

@frappe.whitelist()
def get_list_data(doctype="HD Ticket", filters=None, **kwargs):
    """Get list data with custom filters and OR logic - Direct API endpoint"""
    try:
        print(f"QONEVO API: Received doctype={doctype}, filters={filters}, kwargs={kwargs}")
        
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
        
        # Convert dictionary filters to list format if needed
        if isinstance(filters, dict):
            filter_list = []
            for key, value in filters.items():
                if isinstance(value, list) and len(value) >= 2:
                    # Already in list format like ['>=', '2023-01-01'] or ['between', [date1, date2]]
                    filter_list.append([key] + value)
                elif isinstance(value, list) and len(value) == 1:
                    # Single value in list like ['Open']
                    filter_list.append([key, "=", value[0]])
                elif isinstance(value, list) and len(value) > 1:
                    # Multiple values like ['Open', 'Closed'] - use 'in' operator
                    filter_list.append([key, "in", value])
                else:
                    # Simple value like 'Open'
                    filter_list.append([key, "=", value])
            filters = filter_list
        
        # Ensure filters is a list
        if not isinstance(filters, list):
            filters = []
        
        # Handle OR filter logic
        if filters and len(filters) > 0 and isinstance(filters[0], list) and len(filters[0]) > 0:
            if filters[0][0] == "or":
                # Handle OR filter
                return handle_or_filter(doctype, filters, **kwargs)
        
        # Default behavior - call original helpdesk method
        return call_original_get_list_data(doctype, filters, **kwargs)
        
    except Exception as e:
        return call_original_get_list_data(doctype, filters, **kwargs)

@frappe.whitelist()
def get_filterable_fields(doctype="HD Ticket"):
    """Get filterable fields including custom date and SLA filters"""
    try:
        # Get original filterable fields
        from helpdesk.api.doc import get_filterable_fields as original_get_filterable_fields
        original_fields = original_get_filterable_fields(doctype)
        
        # Add custom fields
        custom_fields = [
            {"label": "Start Date", "fieldname": "opening_date", "fieldtype": "Date"},
            {"label": "End Date", "fieldname": "resolution_date", "fieldtype": "Date"},
            {"label": "Tentative End Date", "fieldname": "resolution_by", "fieldtype": "Datetime"},
            {"label": "SLA Status", "fieldname": "agreement_status", "fieldtype": "Select", "options": "\nFirst Response Due\nResolution Due\nFailed\nFulfilled\nPaused"},
            {"label": "SLA", "fieldname": "sla", "fieldtype": "Link", "options": "HD Service Level Agreement"},
            {"label": "Response By", "fieldname": "response_by", "fieldtype": "Datetime"},
            {"label": "Resolution By", "fieldname": "resolution_by", "fieldtype": "Datetime"}
        ]
        
        # Combine original and custom fields
        all_fields = original_fields + custom_fields
        
        return all_fields
        
    except Exception as e:
        frappe.log_error(f"Error in qonevo get_filterable_fields: {str(e)}")
        return []

@frappe.whitelist()
def get_quick_filters(doctype="HD Ticket"):
    """Get quick filters including custom date and SLA filters"""
    try:
        # Get original quick filters
        from helpdesk.api.doc import get_quick_filters as original_get_quick_filters
        original_filters = original_get_quick_filters(doctype)
        
        # Add custom quick filters
        custom_filters = [
            {"label": "Today's Tickets", "filter": [["opening_date", "=", "today"]]},
            {"label": "This Week's Tickets", "filter": [["opening_date", ">=", "week_start"], ["opening_date", "<=", "week_end"]]},
            {"label": "Overdue SLA", "filter": [["agreement_status", "in", ["First Response Due", "Resolution Due"]]]},
            {"label": "Failed SLA", "filter": [["agreement_status", "=", "Failed"]]},
            {"label": "Fulfilled SLA", "filter": [["agreement_status", "=", "Fulfilled"]]},
            {"label": "Tickets Due Today", "filter": [["resolution_by", "=", "today"]]},
            {"label": "Tickets Due This Week", "filter": [["resolution_by", ">=", "week_start"], ["resolution_by", "<=", "week_end"]]}
        ]
        
        # Combine original and custom filters
        all_filters = original_filters + custom_filters
        
        return all_filters
        
    except Exception as e:
        frappe.log_error(f"Error in qonevo get_quick_filters: {str(e)}")
        return []

def handle_or_filter(doctype, filters, **kwargs):
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
                result = call_original_get_list_data(doctype, single_filter, **kwargs)
                
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
        return call_original_get_list_data(doctype, filters, **kwargs)

def call_original_get_list_data(doctype, filters, **kwargs):
    """Call the original helpdesk get_list_data method"""
    try:
        # Import the original method
        from helpdesk.api.doc import get_list_data as original_get_list_data
        
        # Convert list format filters to dict format for the original API
        if isinstance(filters, list):
            filter_dict = {}
            for filter_item in filters:
                if isinstance(filter_item, list) and len(filter_item) >= 3:
                    field, operator, value = filter_item[0], filter_item[1], filter_item[2]
                    if operator == "=":
                        filter_dict[field] = value
                    elif operator == "in":
                        filter_dict[field] = ["in", value]
                    elif operator == "like":
                        filter_dict[field] = ["like", value]
                    elif operator == ">=":
                        filter_dict[field] = [">=", value]
                    elif operator == "<=":
                        filter_dict[field] = ["<=", value]
                    elif operator == "between":
                        filter_dict[field] = ["between", value]
                    elif operator == ">":
                        filter_dict[field] = [">", value]
                    elif operator == "<":
                        filter_dict[field] = ["<", value]
            filters = filter_dict
        
        # Filter out parameters that the original function doesn't expect
        filtered_kwargs = {}
        allowed_params = ['default_filters', 'order_by', 'page_length', 'columns', 'rows', 
                         'show_customer_portal_fields', 'view', 'is_default']
        
        for key, value in kwargs.items():
            if key in allowed_params:
                # Special handling for columns parameter
                if key == 'columns' and isinstance(value, list):
                    # Ensure columns are in the correct format
                    formatted_columns = []
                    for col in value:
                        if isinstance(col, str):
                            # Convert string to object format
                            formatted_columns.append({"key": col, "label": col.title()})
                        elif isinstance(col, dict) and 'key' in col:
                            # Already in correct format
                            formatted_columns.append(col)
                    filtered_kwargs[key] = formatted_columns
                else:
                    filtered_kwargs[key] = value
        
        result = original_get_list_data(doctype, filters, **filtered_kwargs)
        print(f"QONEVO API: Original API returned {len(result.get('data', []))} tickets")
        return result
    except ImportError:
        # Fallback if original method is not available
        frappe.log_error("Original helpdesk get_list_data method not found")
        return {'data': [], 'total_count': 0}


@frappe.whitelist()
def get_demo_conversion_data():
    completed = frappe.db.count("Lead", {"custom_demo_status": "Completed"})
    converted = frappe.db.count("Lead", {"custom_demo_status": "Converted to Order"})
    ratio = round((converted / completed) * 100, 2) if completed else 0

    return {
        "completed": completed,
        "converted": converted,
        "ratio": ratio
    }


@frappe.whitelist()
def get_ticket_history(ticket_no):
    if not ticket_no:
        frappe.throw("Please provide a ticket number")

    history = []
    logs = frappe.get_all(
        "HD Ticket Activity",
        filters={"ticket": ticket_no},
        fields=["action", "owner", "creation"],
        order_by="creation asc"
    )
    for log in logs:
        history.append({
            "state": log.action,
            "action_by": log.owner,
            "time": log.creation
        })

    if not history:
        # Return empty list instead of throwing error
        return []

    return history



@frappe.whitelist()
def get_inventory_html():
    # Query the Serial No table
    rows = frappe.db.sql("""
        SELECT
            sn.item_code,
            sn.custom_model_number AS model_number,
            sn.custom_size AS size,
            COUNT(sn.name) AS current_qty,
            SUM(CASE WHEN sn.status = 'Reserved' THEN 1 ELSE 0 END) AS reserved_qty,
            COUNT(sn.name) - SUM(CASE WHEN sn.status = 'Reserved' THEN 1 ELSE 0 END) AS available_qty
        FROM
            `tabSerial No` sn
        WHERE
            sn.docstatus < 2
        GROUP BY
            sn.item_code, sn.custom_model_number, sn.custom_size
        ORDER BY
            sn.item_code
    """, as_dict=1)

    # Start building HTML
    html = """
    <table class="table table-bordered">
        <thead>
            <tr>
                <th>Item</th>
                <th>Model</th>
                <th>Size</th>
                <th>Current Qty</th>
                <th>Reserved Qty</th>
                <th>Available Qty</th>
            </tr>
        </thead>
        <tbody>
    """

    # Populate rows
    for row in rows:
        html += f"""
            <tr>
                <td>{row.item_code}</td>
                <td>{row.model_number or ''}</td>
                <td>{row.size or ''}</td>
                <td>{row.current_qty}</td>
                <td>{row.reserved_qty or 0}</td>
                <td>{row.available_qty}</td>
            </tr>
        """

    html += """
        </tbody>
    </table>
    """

    return html



@frappe.whitelist()
def get_sales_orders_html(customer=None, item_code=None):
    filters = ""
    if customer:
        filters += f" AND so.customer = '{customer}'"
    if item_code:
        filters += f" AND soi.item_code = '{item_code}'"

    rows = frappe.db.sql(f"""
        SELECT
            so.name AS sales_order,
            so.customer,
            soi.item_code,
            soi.qty AS qty_ordered,
            IFNULL(bin.reserved_qty, 0) AS qty_reserved
        FROM
            `tabSales Order` so
        INNER JOIN
            `tabSales Order Item` soi ON soi.parent = so.name
        LEFT JOIN
            `tabBin` bin ON bin.item_code = soi.item_code
        WHERE
            so.docstatus = 1
            {filters}
        ORDER BY
            so.transaction_date
    """, as_dict=1)

    html = """
    <table class="table table-bordered">
        <thead>
            <tr>
                <th>Sales Order</th>
                <th>Customer</th>
                <th>Item</th>
                <th>Qty Ordered</th>
                <th>Qty Reserved</th>
            </tr>
        </thead>
        <tbody>
    """
    for r in rows:
        html += f"""
        <tr>
            <td>{r.sales_order}</td>
            <td>{r.customer}</td>
            <td>{r.item_code}</td>
            <td>{r.qty_ordered}</td>
            <td>{r.qty_reserved}</td>
        </tr>
        """
    html += "</tbody></table>"
    return html


    
@frappe.whitelist()
def get_dispatch_html(customer=None, item_code=None):
    filters = ""
    if customer:
        filters += f" AND dn.customer = '{customer}'"
    if item_code:
        filters += f" AND dni.item_code = '{item_code}'"

    query = f"""
        SELECT
            dn.name AS delivery_note,
            dn.customer,
            dni.item_code,
            dni.serial_no
        FROM
            `tabDelivery Note` dn
        INNER JOIN
            `tabDelivery Note Item` dni
            ON dni.parent = dn.name
        WHERE
            dn.docstatus = 0
            {filters}
        ORDER BY
            dn.posting_date
    """

    rows = frappe.db.sql(query, as_dict=1)

    html = """
    <table class="table table-bordered">
        <thead>
            <tr>
                <th>Delivery Note</th>
                <th>Customer</th>
                <th>Item</th>
                <th>Serial No</th>
            </tr>
        </thead>
        <tbody>
    """

    for r in rows:
        serials = r.serial_no.split(",") if r.serial_no else []
        for s in serials:
            html += f"""
            <tr>
                <td>{r.delivery_note}</td>
                <td>{r.customer}</td>
                <td>{r.item_code}</td>
                <td>{s.strip()}</td>
            </tr>
            """

    html += "</tbody></table>"
    return html


@frappe.whitelist()
def get_dashboard_data(from_date=None, to_date=None):
    from datetime import datetime
    try:
        filters = {"docstatus": 1}
        if from_date and to_date:
            filters["delivery_date"] = ["between", [from_date, to_date]]
        
        orders = frappe.get_all(
            "Sales Order",
            filters=filters,
            fields=["name", "customer", "custom_priority", "delivery_date", "grand_total"],
            limit=100
        )
        delivery_data = []
        for order in orders:
            qty_result = frappe.db.sql("""
                SELECT SUM(qty) as total_qty 
                FROM `tabSales Order Item` 
                WHERE parent = %s
            """, order.name, as_dict=True)
            qty = qty_result[0].total_qty if qty_result and qty_result[0].total_qty else 0
            priority_colors = {
                "Urgent": "urgent",
                "High": "high", 
                "Medium": "medium",
                "Low": "low"
            }
            status_colors = {
                "Pending": "pending",
                "In Progress": "pending",
                "Completed": "completed",
                "On Hold": "pending"
            }
            delivery_data.append({
                "name": order.name,
                "customer": order.customer or "N/A",
                "priority": order.custom_priority or "Medium",
                "priority_color": priority_colors.get(order.custom_priority, "medium"),
                "delivery_date": order.delivery_date.strftime("%d-%m-%Y") if order.delivery_date else "",
                "priority_status": "Pending",  # Default status since field doesn't exist
                "status_color": "pending",  # Default color
                "total_qty": qty,
                "grand_total": order.grand_total or 0
            })
        return {
            "delivery_data": delivery_data
        }
    except Exception as e:
        frappe.log_error(f"Dashboard API Error: {str(e)}")
        return {
            "delivery_data": [],
            "error": str(e)
        }

@frappe.whitelist()
def create_purchase_receipt(purchase_order, items_data):
    """Create Purchase Receipt from Purchase Order with custom quantities"""
    try:
        # Parse items data
        if isinstance(items_data, str):
            items_data = json.loads(items_data)
        
        # Get Purchase Order
        po = frappe.get_doc("Purchase Order", purchase_order)
        if not po:
            frappe.throw(f"Purchase Order {purchase_order} not found")
        
        # Create Purchase Receipt
        pr = frappe.new_doc("Purchase Receipt")
        pr.supplier = po.supplier
        pr.purchase_order = purchase_order
        pr.posting_date = frappe.utils.today()
        pr.posting_time = frappe.utils.nowtime()
        
        # Add items based on provided data
        for item_data in items_data:
            # Find corresponding PO item
            po_item = None
            for po_item_row in po.items:
                if po_item_row.item_code == item_data.get('item_code'):
                    po_item = po_item_row
                    break
            
            if po_item:
                pr.append("items", {
                    "item_code": item_data.get('item_code'),
                    "item_name": po_item.item_name,
                    "qty": flt(item_data.get('accepted_qty', 0)),
                    "uom": po_item.uom,
                    "rate": po_item.rate,
                    "amount": flt(item_data.get('accepted_qty', 0)) * flt(po_item.rate),
                    "purchase_order": purchase_order,
                    "purchase_order_item": po_item.name,
                    "rejected_qty": flt(item_data.get('rejected_qty', 0)),
                    "remarks": item_data.get('remarks', '')
                })
        
        pr.insert()
        pr.submit()
        
        frappe.msgprint(f"Purchase Receipt {pr.name} created successfully")
        return pr.name
        
    except Exception as e:
        frappe.log_error(f"Error creating Purchase Receipt: {str(e)}")
        frappe.throw(f"Error creating Purchase Receipt: {str(e)}")

@frappe.whitelist()
def get_requirement_dashboard_data():
    """Get data for requirement dashboard"""
    try:
        requirements = frappe.get_all(
            "Requirement Generation",
            fields=["name", "date", "supplier", "supplier_name", "status", "purchase_order", "total_amount"],
            order_by="creation desc"
        )
        
        for req in requirements:
            # Get approved items count
            approved_count = frappe.db.count(
                "Requirement Generation Item",
                {"parent": req.name, "status": "Approved"}
            )
            total_count = frappe.db.count(
                "Requirement Generation Item",
                {"parent": req.name}
            )
            req.approved_items = f"{approved_count}/{total_count}"
        
        return requirements
    except Exception as e:
        frappe.log_error(f"Error getting requirement dashboard data: {str(e)}")
        return []

@frappe.whitelist()
def create_opportunities_for_lead(lead_name):
    """Create a separate Opportunity for each item in the Lead's items table"""
    try:
        lead = frappe.get_doc("Lead", lead_name)
        
        if not lead.items:
            frappe.throw(_("No items found in Lead"))

        customer_name = lead.customer
        if not customer_name:
            if frappe.db.exists("Customer", lead.lead_name):
                customer_name = lead.lead_name
            else:
                customer = frappe.new_doc("Customer")
                customer.customer_name = lead.lead_name
                customer.customer_type = "Company"
                customer.customer_group = "All Customer Groups"
                customer.territory = lead.territory or "All Territories"
                customer.lead_name = lead.name
                customer.insert(ignore_permissions=True)
                customer_name = customer.name
                
                lead.db_set("customer", customer_name)

        created_opportunities = []
        
        for item in lead.items:
            opp = frappe.new_doc("Opportunity")
            
            opp.opportunity_from = "Customer"
            opp.party_name = customer_name
            opp.opportunity_type = "Sales"
            opp.source = lead.source
            opp.title = item.item_name or item.item_code
            opp.status = "Open"
            opp.contact_email = lead.email_id
            opp.contact_mobile = lead.mobile_no
            opp.whatsapp = lead.whatsapp_no
            opp.phone = lead.phone
            opp.phone_ext = lead.phone_ext
            opp.designation = lead.designation
            opp.company = lead.company or frappe.db.get_single_value("Global Defaults", "default_company")
            opp.organisation_name = lead.company_name

            # Map item
            opp.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "rate": "10",
                "qty": 1,
                "uom": frappe.db.get_value("Item", item.item_code, "stock_uom")
            })
                
            opp.insert(ignore_permissions=True)
            
            created_opportunities.append({
                "name": opp.name,
                "url": frappe.utils.get_url_to_form("Opportunity", opp.name)
            })
            
        return created_opportunities
        
    except Exception as e:
        frappe.log_error(f"Error creating opportunities for lead {lead_name}: {str(e)}")
        raise e

@frappe.whitelist()
def get_customer_connections_html(customer):
    """Get HTML dashboard for Customer connections (Lead -> Opportunity -> Quotation)"""
    try:
        opportunities = frappe.get_all("Opportunity", 
            filters={"party_name": customer, "opportunity_from": "Customer"},
            fields=["name", "title", "status", "opportunity_amount", "creation"]
        )
        
        lead_name = frappe.db.get_value("Customer", customer, "lead_name")
        lead_link = f"<a href='/app/lead/{lead_name}' target='_blank' style='font-weight:500;'>{lead_name}</a>" if lead_name else "-"

        html = """
        <div style="border: 1px solid #d1d8dd; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <table class="table table-bordered mb-0" style="width:100%; font-size: 13px;">
                <thead style="background-color: #f8f9fa; color: #495057;">
                    <tr>
                        <th style="width:25%; font-weight: 600; padding: 12px 15px;">Lead</th>
                        <th style="width:25%; font-weight: 600; padding: 12px 15px;">Opportunity</th>
                        <th style="width:25%; font-weight: 600; padding: 12px 15px;">Quotation</th>
                        <th style="width:25%; font-weight: 600; padding: 12px 15px;">Perfoma Invoice</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        if opportunities:
            for opp in opportunities:
                quotations = frappe.get_all("Quotation",
                    filters={"opportunity": opp.name},
                    fields=["name", "status"]
                )
                
                quotation_links = []
                sales_order_links = [] # Collect SOs from all quotations
                
                for q in quotations:
                    status_color = "green" if q.status != "Lost" else "red"
                    q_link = f"""<div style="margin-bottom: 4px;">
                        <a href='/app/quotation/{q.name}' target='_blank' style='font-weight:500;'>{q.name}</a>
                        <span class="indicator-pill {status_color} no-indicator-dot" style="font-size: 10px; padding: 2px 6px;">{q.status}</span>
                    </div>"""
                    quotation_links.append(q_link)
                    
                    # Fetch Sales Orders linked to this Quotation
                    sales_orders = frappe.get_all("Sales Order", 
                        filters=[["Sales Order Item", "prevdoc_docname", "=", q.name], ["docstatus", "!=", 2]],
                        fields=["name", "status"],
                        distinct=True
                    )
                    
                    for so in sales_orders:
                         so_status_color = "green" if so.status not in ["Cancelled", "Closed"] else "red"
                         so_link = f"""<div style="margin-bottom: 4px;">
                            <a href='/app/sales-order/{so.name}' target='_blank' style='font-weight:500;'>{so.name}</a>
                            <span class="indicator-pill {so_status_color} no-indicator-dot" style="font-size: 10px; padding: 2px 6px;">{so.status}</span>
                        </div>"""
                         sales_order_links.append(so_link)
                
                quotations_html = "".join(quotation_links) if quotation_links else "<span class='text-muted'>-</span>"
                sales_orders_html = "".join(list(set(sales_order_links))) if sales_order_links else "<span class='text-muted'>-</span>" # Unique SOs
                
                opp_link = f"""<div style="font-weight:500;"><a href='/app/opportunity/{opp.name}' target='_blank'>{opp.name}</a></div>
                             <div class="text-muted" style="font-size: 12px; margin-top: 2px;">{opp.title or ''}</div>"""
                
                html += f"""
                <tr style="transition: background-color 0.2s;">
                    <td style="padding: 12px 15px; vertical-align: middle;">{lead_link}</td>
                    <td style="padding: 12px 15px; vertical-align: middle;">{opp_link}</td>
                    <td style="padding: 12px 15px; vertical-align: middle;">{quotations_html}</td>
                    <td style="padding: 12px 15px; vertical-align: middle;">{sales_orders_html}</td>
                </tr>
                """
        else:
            html += f"""
            <tr>
                <td style="padding: 12px 15px;">{lead_link}</td>
                <td colspan="3" class="text-center text-muted" style="padding: 20px;">
                    No Opportunities found for this Customer
                </td>
            </tr>
            """

        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html
        
    except Exception as e:
        frappe.log_error(f"Error getting customer dashboard: {str(e)}")
        return f"<div class='alert alert-danger'>Error loading dashboard: {str(e)}</div>"
