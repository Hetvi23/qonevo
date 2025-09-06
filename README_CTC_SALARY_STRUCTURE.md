# CTC-Based Salary Structure Assignment

This feature automatically creates and assigns salary structures to employees based on their Cost to Company (CTC) amount.

## Features

1. **Automatic Salary Structure Assignment**: When you enter a CTC for an employee, the system automatically finds or creates a matching salary structure and assigns it to the employee.

2. **CTC Range Templates**: Create templates that define salary structures for specific CTC ranges (e.g., 50,000-75,000, 75,000-100,000, etc.).

3. **Smart Matching**: The system finds the most appropriate salary structure template based on the employee's CTC, company, and currency.

4. **Automatic Assignment**: If a matching template exists, the system automatically assigns the corresponding salary structure to the employee.

## How to Use

### 1. Create CTC Salary Structure Templates

1. Go to **CTC Salary Structure Template** doctype
2. Create a new template with the following details:
   - **Template Name**: A descriptive name (e.g., "Mid-Level Employee")
   - **Company**: Select the company
   - **Currency**: Select the currency
   - **CTC Range From**: Minimum CTC for this template
   - **CTC Range To**: Maximum CTC for this template
   - **Earnings**: Define salary components and amounts
   - **Deductions**: Define deduction components and amounts

### 2. Employee CTC Entry

1. Go to **Employee** doctype
2. In the **Salary** tab, enter the employee's CTC
3. The system will automatically:
   - Find a matching CTC template
   - Create a salary structure if needed
   - Assign the salary structure to the employee

### 3. Manual Override

- You can disable automatic assignment by unchecking **Auto Assign Salary Structure**
- Use the **Get Suggested Salary Structure** button to see what template would be used
- The **Suggested Salary Structure** field shows the recommended template name

## Technical Details

### Doctypes Created

1. **CTC Salary Structure Template**: Stores templates for different CTC ranges
2. **CTC Salary Structure Earning**: Child table for earnings in templates
3. **CTC Salary Structure Deduction**: Child table for deductions in templates

### Key Functions

- `get_matching_template()`: Finds the best matching template for a given CTC
- `create_salary_structure_from_ctc()`: Creates or retrieves salary structure based on CTC
- `handle_ctc_based_salary_structure()`: Main logic for automatic assignment

### Employee Doctype Extensions

- Added **CTC-Based Salary Structure** section (custom field)
- Added **Suggested Salary Structure** field (read-only custom field)
- Added **Auto Assign Salary Structure** checkbox (custom field)
- Enhanced validation to trigger automatic assignment via document events

## Configuration

### Prerequisites

1. Ensure **Default Payroll Payable Account** is set in Company defaults
2. Create necessary **Salary Components** for earnings and deductions
3. Set up **Company** and **Currency** properly

### Best Practices

1. **Create Overlapping Ranges**: Ensure CTC ranges cover all possible employee salaries
2. **Use Descriptive Names**: Template names should clearly indicate the salary level
3. **Regular Updates**: Update templates when salary structures change
4. **Test Templates**: Verify templates work correctly before using in production

## Troubleshooting

### Common Issues

1. **No Matching Template Found**
   - Ensure CTC ranges cover the employee's salary
   - Check company and currency match

2. **Salary Structure Not Created**
   - Verify salary components exist
   - Check for validation errors in templates

3. **Assignment Failed**
   - Ensure Default Payroll Payable Account is set
   - Check employee has required fields filled

### Error Messages

- "No matching CTC template found": Create a template for the CTC range
- "Please set Default Payroll Payable Account": Configure company defaults
- "At least one earning or deduction component is required": Add components to template

## API Usage

### Get Matching Template
```python
template = get_matching_template(ctc=75000, company="Your Company", currency="INR")
```

### Create Salary Structure from CTC
```python
salary_structure = create_salary_structure_from_ctc(
    ctc=75000, 
    company="Your Company", 
    currency="INR", 
    employee_name="EMP-001"
)
```

## Support

For issues or questions, please contact the development team or create an issue in the project repository.
