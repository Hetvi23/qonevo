# Installation Job System - Complete Implementation

## Overview

This document describes the complete Installation Job workflow system implemented in Qonevo/ERPNext. The system automates the entire installation process from delivery to warranty creation.

## Workflow Steps

### 1. Trigger Installation Job

**Who:** System automation  
**When:** Delivery Note is submitted (Installation is required for ALL Sales Orders)  
**What happens:**
- System creates an Installation Job linked to Sales Order + Delivery Note
- Pre-fills: Customer, Item, Serial Nos delivered, Delivery Date
- Status = Scheduled
- **Purpose:** The job appears in the Installer's task list automatically
- **Note:** Installation is automatically required for all Sales Orders

### 2. Installer starts installation

**Who:** Installer (Field Technician)  
**What happens:**
- Opens the Installation Job assigned to them
- Status automatically changes to "In Progress" when first item is marked as installed
- For each Serial No in the job:
  - Mark Installed or Not Installed using the checkbox
  - If Not Installed → choose reason (e.g. Client Delay, Vendor Issue, Missing Part)
  - Upload photos of the setup/site
  - Capture customer signature as proof of work
- **Automatic Status Updates:** Status changes automatically based on installation checkboxes
- **Mandatory fields:** At least 1 photo + client signature before marking job completed
- **Purpose:** Ensure accountability and evidence collection

### 3. Installer completes installation

**Who:** Installer  
**What happens:**
- Status automatically changes to "Completed - Full" when all items are marked as installed
- Status automatically changes to "Completed - Partial" when some items are installed but not all
- Installation date is automatically set when status becomes completed
- Warranty records are automatically created for installed items
- Clicks "Complete Installation" button to finalize → status locked
- System check: No completion allowed without mandatory photos/signature
- **Purpose:** Installer's role ends here; now Ops takes over

### 4. Ops Verification

**Who:** Operations Manager / Coordinator  
**What happens:**
- Reviews job details: serials installed vs not installed, photos, signature, installer notes
- Confirms reasons for missing installs (Client vs Vendor)
- Decides Warranty Start Action:
  - Start Now → All installed serials get warranty
  - Partial Start → Only installed serials get warranty. Others remain pending
  - Delay → No warranty yet (if vendor fault)
- Updates status to Verified
- **Purpose:** Adds control layer; warranty does not start without Ops check

### 5. System creates Warranty Records

**Who:** System automation  
**When:** Installation Job status = Completed (Full or Partial)  
**What happens:**
- For each installed Serial No, create a Warranty Record:
  - Serial No
  - Item
  - Customer (with customer name from Customer master)
  - Sales Order + Delivery Note + Installation Job links
  - Start Date = Installation Date
  - End Date = Start + Warranty Period (e.g. 3 years)
  - Warranty Type = "Standard"
  - Status = "Active"
- For uninstalled items → skip warranty creation, log pending status
- **Purpose:** Formalizes warranty per Serial No automatically when installation is completed

### 6. Closure

**Who:** Ops  
**What happens:** Once warranty creation is confirmed, Ops sets Installation Job = Closed  
**Purpose:** Closes the loop for reporting

## DocTypes Created

### Installation Job
- **Fields:**
  - Basic Info: Naming Series, Status, Sales Order, Delivery Note, Customer
  - Assignment: Installation Date, Assigned Installer
  - Items: Table of items to install (Installation Job Item)
  - Evidence: Photos table, Customer Signature, Signature Date
  - Notes: Installer Notes, Ops Verification Notes
  - Warranty: Warranty Start Action
  - Summary: Total Items, Installed Count, Not Installed Count, Completion Percentage

### Installation Job Item (Child Table)
- **Fields:**
  - Item, Quantity, Serial Number
  - Installation Status (Pending/Installed/Not Installed)
  - Not Installed Reason (Client Delay/Vendor Issue/Missing Part/Technical Issue/Other)
  - Installer Notes

### Installation Job Photo (Child Table)
- **Fields:**
  - Photo Name, Photo Type, Photo File (Attach)
  - Description, Taken Date

### Warranty Record
- **Fields:**
  - Serial Number, Item, Customer
  - Links: Sales Order, Delivery Note, Installation Job
  - Warranty Period: Start Date, End Date, Warranty Period (Years)
  - Warranty Type (Standard/Extended/Limited)
  - Warranty Terms, Status

## Custom Fields Added

No custom fields are required. Installation is automatically required for all Sales Orders.

## Workflow States

1. **Scheduled** → **In Progress** (Installer starts)
2. **In Progress** → **Completed - Full** (All items installed)
3. **In Progress** → **Completed - Partial** (Some items not installed)
4. **Completed - Full** → **Verified** (Ops verification)
5. **Completed - Partial** → **Verified** (Ops verification)
6. **Verified** → **Closed** (Ops closes job)
7. **Any State** → **Cancelled** (System Manager cancels)

## Roles Created

- **Installer**: Can start and complete installations
- **Operations Manager**: Can verify installations and close jobs

## Hooks Implemented

### Delivery Note Hooks
- **on_submit**: Creates Installation Job when Delivery Note is submitted and Sales Order has Installation Required = Yes
- **on_cancel**: Cancels related Installation Jobs when Delivery Note is cancelled

## API Methods

### Installation Job Methods
- `complete_installation(installation_job, installer_notes)`: Complete installation (status auto-updated by checkboxes)
- `create_warranty_records(installation_job)`: Create warranty records for installed items automatically
- `verify_installation(installation_job, ops_notes, warranty_action)`: Verify installation
- `close_installation_job(installation_job)`: Close job

### Warranty Record Methods
- `get_warranty_status(serial_no)`: Get warranty status for a serial number
- `extend_warranty(warranty_record, additional_years)`: Extend warranty period

## Reports

### Installation Job Report
- Shows all installation jobs with filters for status, customer, installer, date range
- Columns: Job Name, Status, Customer, Sales Order, Delivery Note, Installer, Installation Date, Items Count, Completion Percentage, Created Date

## Installation

To install the complete system:

1. **Install DocTypes**: The JSON files will create all DocTypes
2. **Install Workflows**: Run fixtures to install workflows
3. **Install Reports**: Run fixtures to install reports
4. **Create Roles**: Run the setup script to create required roles
5. **Test**: Use the test functions to verify the system works

## Usage Examples

### Creating an Installation Job (Automatic)
1. Create Sales Order
2. Create Delivery Note from Sales Order with serial numbers
3. Submit Delivery Note
4. System automatically creates Installation Job for ALL Sales Orders

### Manual Installation Job Creation
1. Go to Installation Job list
2. Click "New"
3. Fill in Sales Order, Delivery Note, Customer
4. Add items to install
5. Save

### Installer Workflow
1. Open assigned Installation Job
2. Mark each item as Installed/Not Installed using checkboxes (status auto-updates)
3. Add photos using "Add Photo" button
4. Upload customer signature
5. Click "Complete Installation" when ready

### Operations Workflow
1. Review completed Installation Job
2. Click "Verify Installation"
3. Choose warranty start action
4. Add verification notes
5. Click "Close Job" when done

## Validation Rules

- Installation Job cannot be completed without at least 1 photo
- Installation Job cannot be completed without customer signature
- Not Installed items must have a reason selected
- Warranty Start Action is required for verification
- Only verified jobs can be closed

## Integration Points

- **Delivery Note**: Serial numbers trigger installation job creation
- **Warranty Record**: Automatically created for installed items
- **User Roles**: Control access to different workflow stages

## Troubleshooting

### Common Issues
1. **Installation Job not created**: Check if Delivery Note has serial numbers (required for installation jobs)
2. **Cannot complete installation**: Ensure photos and signature are uploaded
3. **Cannot verify job**: Check that job is in Completed status
4. **Warranty not created**: Verify that job is verified and warranty action is not "Delay"

### Debug Functions
- `test_installation_job_creation()`: Test job creation
- `get_installation_job_summary()`: Get status summary

## Future Enhancements

- Mobile app for field technicians
- GPS location tracking for installations
- Automated scheduling based on installer availability
- Integration with customer portal for status updates
- Advanced reporting and analytics
- Integration with maintenance scheduling
