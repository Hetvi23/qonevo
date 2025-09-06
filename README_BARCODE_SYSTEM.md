# Barcode System Implementation

## Overview

This barcode system allows you to generate barcodes that store both Item Code and Model Number (manufacturer part number). When scanned in logistics modules, the system automatically populates item tables with the data extracted from the barcode.

## Features

### 1. Barcode Generation
- **Structured Barcodes**: Store both item code and model number in a single barcode
- **Multiple Formats**: Support for CODE128, CODE39, EAN13, EAN8, UPC, and QR codes
- **Visual Generation**: Generate barcode images for printing
- **Bulk Generation**: Create barcodes for multiple items at once

### 2. Barcode Scanning
- **Automatic Item Detection**: Scan barcodes to automatically populate item details
- **Model Number Extraction**: Extract and display model numbers from barcodes
- **Integration**: Works seamlessly with all logistics modules

### 3. Logistics Integration
- **Delivery Notes**: Scan barcodes to add items to delivery notes
- **Purchase Receipts**: Use barcode scanning for receiving items
- **Stock Entries**: Scan barcodes for stock transfers and adjustments
- **Material Requests**: Add items via barcode scanning
- **Purchase Orders**: Scan barcodes when creating purchase orders
- **Sales Orders**: Use barcode scanning for sales order creation

## Barcode Format

The barcode stores data in the format: `ITEM_CODE|MODEL_NUMBER|SERIAL_NUMBER`

**Examples:**
- **With Serial Number**: `LAPTOP-001|Dell-XPS-13-2024|SN123456789`
- **Without Serial Number**: `LAPTOP-001|Dell-XPS-13-2024`
- **Simple Item Code**: `LAPTOP-001`

**Note**: Serial numbers are automatically included when the item has `has_serial_no` enabled.

## Installation

The barcode system is automatically installed when you install the Qonevo app. If you need to manually set it up:

```bash
bench --site your-site.com execute qonevo.setup_barcode_system.setup_barcode_system
```

## Usage

### 1. Generating Barcodes

#### Method 1: Using Item Barcode Generator
1. Go to **Barcode Management** workspace
2. Click **Generate New Barcode**
3. Select the item code
4. Enter or verify the model number
5. Enter serial number (if applicable)
6. Choose barcode type (default: CODE128)
7. Save to generate barcode

#### Method 2: Automatic Generation for Serial Numbers
1. Create a serial number for an item
2. Barcode is automatically generated and stored
3. Check **Serial No** doctype for barcode information

#### Method 3: Bulk Generation
1. Go to **Barcode Manager** page
2. Click **Bulk Generate**
3. Enter item codes separated by commas
4. System will generate barcodes for all items

### 2. Scanning Barcodes in Logistics Modules

#### In Delivery Notes, Purchase Receipts, etc.:
1. Open the logistics document
2. Click **Scan Barcode** button (or press Ctrl+B)
3. Scan the barcode or manually enter it
4. Item details will be automatically populated

#### Features:
- **Duplicate Detection**: If item already exists, quantity is increased
- **Model Number Display**: Shows model number in item table
- **Barcode Tracking**: Stores original barcode string for reference

### 3. Barcode Manager Dashboard

Access the dashboard at **Barcode Management > Barcode Manager** to:
- View statistics (total items, items with barcodes, coverage)
- See recent barcode generations
- Find items without barcodes
- View barcode type distribution
- Generate barcodes for specific items

## Custom Fields Added

The system adds the following custom fields to logistics modules:

### For all Item tables (Delivery Note Item, Purchase Receipt Item, etc.):
- **Model Number**: Displays the model number from barcode scan
- **Scanned Serial Number**: Displays the serial number from barcode scan
- **Scanned Barcode**: Stores the original barcode string

### For Serial No doctype:
- **Barcode String**: Stores the generated barcode string
- **Barcode Generated**: Indicates whether barcode has been generated

## API Endpoints

### Generate Item Barcode
```python
frappe.call('qonevo.barcode_utils.generate_item_barcode', {
    'item_code': 'ITEM-001',
    'model_number': 'MODEL-123',
    'serial_number': 'SN123456789',  # Optional
    'barcode_type': 'CODE128'
})
```

### Scan Barcode
```python
frappe.call('qonevo.barcode_utils.scan_item_barcode', {
    'barcode_string': 'ITEM-001|MODEL-123|SN123456789'
})
```

### Get Item by Barcode (ERPNext Compatible)
```python
frappe.call('qonevo.barcode_utils.get_item_by_barcode', {
    'barcode_string': 'ITEM-001|MODEL-123|SN123456789'
})
```

### Regenerate Serial Barcode
```python
frappe.call('qonevo.serial_number_handlers.regenerate_serial_barcode', {
    'serial_number': 'SN123456789'
})
```

### Bulk Generate Serial Barcodes
```python
frappe.call('qonevo.serial_number_handlers.bulk_generate_serial_barcodes', {
    'item_code': 'ITEM-001'  # Optional, generates for all items if not provided
})
```

### Bulk Generate Barcodes
```python
frappe.call('qonevo.barcode_utils.generate_bulk_barcodes', {
    'item_codes': ['ITEM-001', 'ITEM-002', 'ITEM-003'],
    'barcode_type': 'CODE128'
})
```

## Technical Details

### Barcode Structure
- **Format**: `ITEM_CODE|MODEL_NUMBER|SERIAL_NUMBER`
- **Separator**: Pipe character (`|`)
- **Fallback**: If no model number or serial number, only item code is used
- **Serial Numbers**: Automatically included when item has `has_serial_no` enabled

### Database Changes
- Custom fields added to logistics item tables
- No changes to existing ERPNext tables
- Backward compatible with existing barcode system

### Security
- Respects existing Frappe/ERPNext permissions
- Role-based access control
- Audit trail for barcode operations

## Troubleshooting

### Common Issues

1. **Barcode not scanning**
   - Check if item exists in the system
   - Verify barcode format (ITEM_CODE|MODEL_NUMBER|SERIAL_NUMBER)
   - Ensure barcode scanner is properly configured

2. **Model number not showing**
   - Check if item has `default_manufacturer_part_no` set
   - Verify barcode contains model number
   - Check custom field visibility settings

3. **Barcode generation fails**
   - Ensure barcode library is installed
   - Check item code validity
   - Verify barcode type is supported

### Error Logs
Check Frappe error logs for detailed error messages:
```bash
bench --site your-site.com logs
```

## Customization

### Adding New Barcode Types
1. Edit `barcode_utils.py`
2. Add new type to barcode type options
3. Update validation logic if needed

### Modifying Barcode Format
1. Update `_generate_barcode_image()` method
2. Update `scan_barcode()` method
3. Update documentation

### Adding to New Modules
1. Add custom fields to new doctype
2. Include barcode scanner JavaScript
3. Update hooks.py if needed

## Performance Considerations

- Barcode generation is cached for 2 minutes
- Bulk operations are optimized for large datasets
- Database queries are indexed for fast lookups

## Future Enhancements

### Planned Features
1. **Mobile App Integration**: Native mobile barcode scanning
2. **Batch Scanning**: Scan multiple barcodes at once
3. **Advanced Analytics**: Barcode usage statistics
4. **Print Templates**: Custom barcode label templates
5. **API Integration**: REST API for external systems

### Customization Options
1. **Custom Barcode Formats**: Support for different data structures
2. **Integration Hooks**: Custom processing after barcode scan
3. **Validation Rules**: Custom validation for barcode data
4. **Reporting**: Custom reports for barcode usage

## Support

For technical support or feature requests:
- Check the documentation above
- Review error logs
- Contact the development team

## License

This barcode system is part of the Qonevo app and follows the same license terms.
