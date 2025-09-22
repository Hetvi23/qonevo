# Manufacturing Serials Tracking System

## Overview

This implementation provides automatic tracking of manufactured serial numbers when stock entries are made with work order references. The system populates a custom table in Sales Orders with the serial numbers produced through manufacturing processes.

## Features

- **Automatic Serial Tracking**: When a stock entry is submitted with a work order reference, serial numbers are automatically captured and added to the connected Sales Order
- **Custom Table Integration**: Uses the existing `Manufacturing Serials` child table in Sales Orders
- **Checkbox Status**: Updates the `custom_serials_added` checkbox to indicate when serials have been added
- **Cancellation Support**: Handles stock entry cancellation by removing the corresponding serial numbers
- **Dual Serial Support**: Works with both old serial number fields and new serial and batch bundle system

## Implementation Details

### Files Created/Modified

1. **`stock_entry_hooks.py`** - Main hook implementation
   - `stock_entry_on_submit()` - Handles stock entry submission
   - `stock_entry_on_cancel()` - Handles stock entry cancellation
   - `get_serial_numbers_from_item()` - Extracts serial numbers from stock entry items
   - `add_manufacturing_serial()` - Adds serial to Manufacturing Serials table
   - `remove_manufacturing_serial()` - Removes serial from Manufacturing Serials table

2. **`setup_manufacturing_serials.py`** - Custom field setup script
   - Creates `custom_manufactured_serials` table field in Sales Order
   - Creates `custom_serials_added` checkbox field in Sales Order

3. **`hooks.py`** - Updated to register Stock Entry hooks
   - Added `on_submit` and `on_cancel` hooks for Stock Entry

4. **`test_manufacturing_serials.py`** - Test and verification script

### Custom Fields Created

#### Sales Order Custom Fields:
- **`custom_manufactured_serials`** (Table)
  - Type: Table
  - Options: Manufacturing Serials
  - Read-only: Yes
  - Description: Serial numbers manufactured through work orders

- **`custom_serials_added`** (Checkbox)
  - Type: Check
  - Read-only: Yes
  - Description: Whether manufacturing serials have been added to this sales order

### Manufacturing Serials Table Structure

The `Manufacturing Serials` child table contains:
- **`serial_no`** - Link to Serial No doctype
- **`item_code`** - Link to Item doctype
- **`manufacturing_date`** - Date when the item was manufactured

## How It Works

### Stock Entry Submission Flow

1. **Stock Entry Submitted**: When a stock entry with work order reference is submitted
2. **Work Order Check**: System checks if the work order has a connected Sales Order
3. **Serial Extraction**: Extracts serial numbers from finished goods items in the stock entry
4. **Table Population**: Adds each serial number to the `custom_manufactured_serials` table
5. **Status Update**: Sets `custom_serials_added` checkbox to 1

### Stock Entry Cancellation Flow

1. **Stock Entry Cancelled**: When a stock entry with work order reference is cancelled
2. **Serial Removal**: Removes corresponding serial numbers from the Manufacturing Serials table
3. **Status Check**: If no serials remain, sets `custom_serials_added` checkbox to 0

### Serial Number Extraction

The system handles both serial number formats:
- **Old Format**: Direct `serial_no` field (comma/newline separated)
- **New Format**: Serial and Batch Bundle system

## Usage Instructions

### Setup

1. **Install Custom Fields**:
   ```bash
   bench --site [site_name] execute qonevo.setup_manufacturing_serials.setup_manufacturing_serials
   ```

2. **Verify Installation**:
   ```bash
   bench --site [site_name] execute qonevo.test_manufacturing_serials.test_manufacturing_serials
   ```

### Normal Operation

1. **Create Sales Order** with items that have BOMs
2. **Create Work Order** from Sales Order
3. **Create Stock Entry** with work order reference for manufacturing
4. **Submit Stock Entry** - Serial numbers are automatically captured
5. **View Sales Order** - Check the "Manufactured Serials" table for captured serials

### Testing

Run the test script to verify functionality:
```bash
bench --site [site_name] execute qonevo.test_manufacturing_serials.test_manufacturing_serials
```

## Error Handling

- **Graceful Failures**: If any step fails, the system logs the error and continues
- **Validation**: Checks for required relationships (work order → sales order)
- **Duplicate Prevention**: Prevents adding duplicate serial numbers
- **Transaction Safety**: Uses database transactions for data consistency

## Logging

The system logs important events:
- Successful serial number additions
- Errors during processing
- Stock entry submission/cancellation events

Check logs in:
- Frappe logs: `sites/[site_name]/logs/`
- Console output during execution

## Troubleshooting

### Common Issues

1. **Custom Fields Not Created**
   - Run the setup script again
   - Check for permission issues

2. **Hooks Not Working**
   - Verify hooks.py is updated
   - Restart the bench server
   - Check for syntax errors in hook files

3. **Serial Numbers Not Captured**
   - Verify work order has sales order reference
   - Check if items are marked as finished goods
   - Ensure serial numbers exist in the stock entry

### Debug Steps

1. **Check Custom Fields**:
   ```python
   frappe.get_all("Custom Field", filters={"dt": "Sales Order"})
   ```

2. **Verify Hooks**:
   ```python
   from qonevo.stock_entry_hooks import stock_entry_on_submit
   ```

3. **Test Serial Extraction**:
   ```python
   # Check if serial numbers are being extracted correctly
   ```

## Future Enhancements

- **Bulk Operations**: Support for bulk serial number operations
- **Reporting**: Reports on manufacturing serial tracking
- **Notifications**: Email notifications when serials are added
- **API Integration**: REST API endpoints for external systems
- **Audit Trail**: Detailed audit trail of serial number changes

## Support

For issues or questions:
1. Check the logs for error messages
2. Run the test script to verify setup
3. Review this documentation for troubleshooting steps
4. Contact the development team for additional support

---

**Version**: 1.0  
**Last Updated**: 2025-01-27  
**Compatible With**: ERPNext v14+, Frappe Framework v14+

