# Sales Order Priority System & Delivery Tracking Dashboard

This implementation adds a comprehensive priority system to Sales Orders with approval workflow and delivery tracking dashboard.

## Features

### 1. Priority System
- **Priority Levels**: Low, Medium, High, Urgent
- **Priority Status**: Pending, In Progress, Completed, On Hold
- **Visual Indicators**: Color-coded priority badges and highlights
- **Validation**: Automatic validation for high-priority orders

### 2. Approval Workflow
- **Finance Approval**: Required before inventory approval
- **Inventory Approval**: Required after finance approval
- **Approval Tracking**: Date and user tracking for each approval
- **Status Management**: Automatic status updates

### 3. Delivery Tracking Dashboard
- **Weekly View**: Shows deliveries scheduled for current week
- **Priority Distribution**: Visual breakdown of orders by priority
- **Approval Status**: Overview of approval status across orders
- **Action Buttons**: Direct approval actions from dashboard
- **Summary Cards**: Key metrics and totals

### 4. Enhanced Sales Order Form
- **Priority Field**: Required field with dropdown options
- **Approval Buttons**: Direct approval actions in form
- **Visual Indicators**: Priority highlighting and status badges
- **Delivery Week**: Automatic calculation of delivery week

## Installation

### 1. Install Custom Fields
```bash
bench --site your-site.com execute qonevo.setup_priority_system.install
```

### 2. Restart Frappe
```bash
bench restart
```

### 3. Clear Cache
```bash
bench --site your-site.com clear-cache
```

## Usage

### Sales Order Workflow

1. **Create Sales Order**
   - Set priority level (Low, Medium, High, Urgent)
   - Set delivery date
   - Submit the order

2. **Finance Approval**
   - Finance team reviews and approves
   - Click "Approve Finance" button
   - Status changes to "Approved"

3. **Inventory Approval**
   - Inventory team reviews and approves
   - Click "Approve Inventory" button
   - Status changes to "Approved"

4. **Delivery Processing**
   - Create delivery note
   - Process delivery
   - Update priority status

### Dashboard Access

1. **Navigate to Dashboard**
   - Go to Desk > Dashboard > Delivery Tracking Dashboard
   - Or access via: `/app/delivery-tracking-dashboard`

2. **View Weekly Deliveries**
   - See all deliveries scheduled for current week
   - Filter by priority, approval status
   - Take direct actions from dashboard

3. **Monitor Metrics**
   - Total orders for the week
   - Total quantity and amount
   - Priority distribution
   - Approval status overview

## Custom Fields Added

### Sales Order Fields
- `priority`: Priority level (Low, Medium, High, Urgent)
- `priority_status`: Current status (Pending, In Progress, Completed, On Hold)
- `finance_approval_status`: Finance approval status
- `finance_approval_date`: Finance approval date
- `finance_approver`: Finance approver user
- `inventory_approval_status`: Inventory approval status
- `inventory_approval_date`: Inventory approval date
- `inventory_approver`: Inventory approver user
- `delivery_week`: Calculated delivery week

## Files Created/Modified

### Core Files
- `apps/qonevo/qonevo/overrides/sales_order.py` - Sales Order class override
- `apps/qonevo/qonevo/hooks.py` - App configuration
- `apps/qonevo/qonevo/setup_priority_system.py` - Installation script

### Custom Fields
- `apps/qonevo/qonevo/fixtures/custom_fields.json` - Custom field definitions

### Dashboard
- `apps/qonevo/qonevo/qonevo/page/delivery_tracking_dashboard/` - Dashboard page
- `apps/qonevo/qonevo/qonevo/doctype/delivery_tracking_dashboard/` - Dashboard doctype

### Reports
- `apps/qonevo/qonevo/qonevo/report/delivery_tracking_report/` - Custom report

### JavaScript
- `apps/qonevo/qonevo/public/js/sales_order_priority.js` - Form enhancements

## Permissions

The system respects existing Frappe/ERPNext permissions:
- **Sales User**: Can create and manage sales orders
- **Sales Manager**: Full access to sales orders and dashboard
- **Stock User**: Can view delivery information
- **Accounts User**: Can view financial information

## Customization

### Adding New Priority Levels
1. Update the `priority` field options in custom fields
2. Update the JavaScript color coding
3. Update the validation logic

### Modifying Approval Workflow
1. Edit the approval methods in `sales_order.py`
2. Update the custom fields for new approval steps
3. Modify the dashboard to show new approval status

### Customizing Dashboard
1. Edit the dashboard page template
2. Modify the data retrieval logic
3. Add new charts or metrics

## Troubleshooting

### Custom Fields Not Appearing
1. Clear cache: `bench --site your-site.com clear-cache`
2. Restart Frappe: `bench restart`
3. Check if custom fields are properly installed

### Dashboard Not Loading
1. Check if the page route is properly configured
2. Verify the dashboard doctype exists
3. Check browser console for JavaScript errors

### Approval Buttons Not Working
1. Verify user has proper permissions
2. Check if the custom methods are properly registered
3. Ensure the Sales Order is submitted

## Support

For issues or questions:
1. Check the Frappe/ERPNext documentation
2. Review the implementation files
3. Contact the development team

## License

This implementation is part of the Qonevo app and follows the same license terms. 