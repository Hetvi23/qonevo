# Requirement Gathering System Implementation

## Overview

This document describes the complete implementation of the Requirement Gathering system for ERPNext, which allows users to manage purchase requirements through a structured approval workflow and automatic creation of Purchase Orders and Purchase Receipts.

## System Architecture

### 1. Doctypes

#### Requirement Gathering (Parent Doctype)
- **Purpose**: Main document for managing purchase requirements
- **Key Fields**:
  - `date`: Date of requirement
  - `supplier`: Link to Supplier
  - `supplier_name`, `supplier_address`, `contact_person`, `gstin`: Auto-filled from supplier
  - `payment_terms`, `supply_terms`, `transport_details`: Business terms
  - `purchase_order_ref`: Link to created Purchase Order
  - `purchase_receipt_ref`: Link to created Purchase Receipt
  - `requirement_item`: Child table for items
  - `status`: Workflow status (Draft, Approved, Rejected, PO Created, PR Created)

#### Requirement Items (Child Table)
- **Purpose**: Individual items in the requirement
- **Key Fields**:
  - `item_code`: Link to Item
  - `item_name`: Auto-filled from item
  - `qty`: Quantity required
  - `rate`: Unit rate (auto-filled from Item Price)
  - `amount`: Calculated amount (qty × rate)
  - `select_ircl`: Approval status (Pending, Approved, Reject)

### 2. Workflow States

1. **Draft**: Initial state, items can be approved/rejected
2. **Approved**: At least one item is approved, PO can be created
3. **Rejected**: All items are rejected
4. **PO Created**: Purchase Order has been created
5. **PR Created**: Purchase Receipt has been created

## Implementation Details

### 1. Auto-fill Logic

#### Supplier Details Auto-fill
- **Trigger**: When `supplier` field changes
- **Method**: `fetch_supplier_details()`
- **Behavior**: Automatically populates supplier-related fields from Supplier doctype

#### Item Details Auto-fill
- **Trigger**: When `item_code` is selected in child table
- **Method**: `fetch_item_details()`
- **Behavior**: 
  - Auto-fills `item_name` from Item doctype
  - Fetches default buying rate from Item Price (Standard Buying price list)
  - Falls back to item's standard rate if no Item Price exists
  - Auto-calculates amount

#### Amount Calculation
- **Trigger**: When `qty` or `rate` changes
- **Method**: `calculate_amount()`
- **Behavior**: Automatically calculates `amount = qty × rate`

### 2. Approval & Rejection System

#### Server Methods

##### `approve_items(docname, all=False, row_idx=None)`
- **Purpose**: Approve items (all or specific row)
- **Parameters**:
  - `docname`: Document name
  - `all`: Boolean to approve all items
  - `row_idx`: Specific row index to approve
- **Behavior**: Updates `select_ircl` to "Approved" and recalculates status

##### `reject_items(docname, all=False, row_idx=None)`
- **Purpose**: Reject items (all or specific row)
- **Parameters**: Same as approve_items
- **Behavior**: Updates `select_ircl` to "Reject" and recalculates status

#### Client-side Features

##### Approve/Reject All Buttons
- **Visibility**: Only shown when status is "Draft"
- **Location**: Actions menu in form
- **Behavior**: Confirms action and calls server method

##### Row-level Buttons
- **Visibility**: Only shown for items with "Pending" status
- **Location**: Inline buttons in child table rows
- **Behavior**: Direct approve/reject for specific items

### 3. Purchase Order Creation

#### Server Method: `create_purchase_order(docname)`
- **Trigger**: "Create Purchase Order" button
- **Prerequisites**: 
  - Status must be "Approved"
  - At least one item must be approved
  - No existing Purchase Order linked
- **Behavior**:
  - Creates new Purchase Order
  - Copies supplier details from Requirement Gathering
  - Adds only approved items to PO
  - Submits the PO
  - Links PO name to `purchase_order_ref`
  - Updates status to "PO Created"

### 4. Purchase Receipt Creation

#### Server Method: `create_purchase_receipt(docname, items_data)`
- **Trigger**: "Create Purchase Receipt" button
- **Prerequisites**:
  - Purchase Order must exist
  - No existing Purchase Receipt linked
- **Behavior**:
  - Creates new Purchase Receipt
  - Links to existing Purchase Order
  - Adds items with accepted quantities
  - Submits the PR
  - Links PR name to `purchase_receipt_ref`
  - Updates status to "PR Created"

#### Client-side Dialog
- **Purpose**: Collect accepted/rejected quantities for each PO item
- **Fields**:
  - Item details (read-only)
  - Accepted Qty (default = ordered qty)
  - Rejected Qty (default = 0)
  - Remarks (optional)
- **Validation**: Ensures accepted + rejected ≤ ordered quantity

## File Structure

```
apps/qonevo/qonevo/doctype/
├── requirement_gathering/
│   ├── requirement_gathering.json      # Doctype definition
│   ├── requirement_gathering.py        # Server-side logic
│   └── requirement_gathering.js        # Client-side logic
└── requirement_generation_item/
    ├── requirement_generation_item.json # Child table definition
    ├── requirement_generation_item.py   # Child table server logic
    └── requirement_generation_item.js   # Child table client logic
```

## Usage Instructions

### 1. Creating a Requirement Gathering

1. Navigate to **Requirement Gathering** list
2. Click **New**
3. Select a **Supplier** (auto-fills supplier details)
4. Add items to the **Requirement Item** table:
   - Select **Item Code** (auto-fills item name and rate)
   - Enter **Quantity**
   - **Rate** is auto-filled but can be modified
   - **Amount** is auto-calculated
5. Save the document

### 2. Approving/Rejecting Items

#### Approve/Reject All
1. Click **Approve All** or **Reject All** in the Actions menu
2. Confirm the action

#### Approve/Reject Individual Items
1. Use the inline **Approve** or **Reject** buttons in each row
2. Items with "Pending" status show these buttons

### 3. Creating Purchase Order

1. Ensure at least one item is approved
2. Click **Create Purchase Order** in the Actions menu
3. Confirm the action
4. System creates and submits the PO automatically

### 4. Creating Purchase Receipt

1. Ensure a Purchase Order exists
2. Click **Create Purchase Receipt** in the Actions menu
3. In the dialog:
   - Review PO items
   - Enter accepted/rejected quantities
   - Add optional remarks
4. Click **Create Receipt**
5. System creates and submits the PR automatically

## Technical Features

### 1. Status Management
- Automatic status calculation based on child items
- Status transitions: Draft → Approved/Rejected → PO Created → PR Created

### 2. Data Validation
- Required fields validation
- Quantity and rate validation (non-negative)
- Business logic validation (e.g., approved items for PO creation)

### 3. Error Handling
- Comprehensive error messages
- Graceful handling of missing data
- Validation before server operations

### 4. User Experience
- Auto-fill functionality reduces data entry
- Confirmation dialogs for important actions
- Clear status indicators
- Inline actions for quick operations

## Compatibility

- **ERPNext Version**: v14+
- **Frappe Framework**: Compatible with latest versions
- **Browser Support**: All modern browsers
- **Mobile Support**: Responsive design

## Testing

Use the provided test script `test_requirement_system.py` to verify:
- Doctype existence
- Method functionality
- Sample data creation
- Basic workflow testing

## Troubleshooting

### Common Issues

1. **Auto-fill not working**: Check if supplier/item exists and has required data
2. **Buttons not showing**: Verify document status and permissions
3. **PO/PR creation fails**: Ensure all prerequisites are met
4. **JavaScript errors**: Check browser console and frappe logs

### Debug Mode

Enable debug mode in Frappe to see detailed error messages and trace method calls.

## Future Enhancements

1. **Email Notifications**: Notify relevant parties on status changes
2. **Approval Workflow**: Multi-level approval system
3. **Bulk Operations**: Import requirements from Excel
4. **Reporting**: Analytics and reporting features
5. **Integration**: API endpoints for external systems 