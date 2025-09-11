# Consignment Note DocType

## Overview
The Consignment Note doctype is a comprehensive shipping document management system designed for tracking and managing consignments between different locations. It supports submission workflow and provides detailed tracking of shipment information.

## Features

### Core Functionality
- **Submittable Document**: Supports draft, submitted, and cancelled states
- **Auto-naming**: Uses naming series `CN-.YYYY.-` for automatic document numbering
- **Location Integration**: Uses ERPNext Location doctype for dynamic from/to locations
- **Payment Tracking**: Supports three payment types (Shipper, Receiver, 3rd Party)
- **Multi-tab Interface**: Organized in three main tabs for better user experience

### Key Fields

#### Basic Information
- **Naming Series**: Auto-generated consignment note number
- **Consignment Date**: Date of consignment (defaults to today)
- **Tracking Number**: Optional tracking reference
- **Consignment From/To**: Dynamic location selection using ERPNext Location doctype
- **Payment By**: Selection between Shipper, Receiver, or 3rd Party

#### Shipper Details Tab
- **Shipper (Supplier)**: Link to ERPNext Supplier
- **Display Name**: Auto-populated from supplier
- **Address**: Auto-fetched from supplier's primary address
- **Contact Information**: Phone, Fax, Email, Web (auto-populated)

#### Consignee Details Tab
- **Consignee (Customer)**: Link to ERPNext Customer
- **Display Name**: Auto-populated from customer
- **Address**: Auto-fetched from customer's primary address
- **Contact Information**: Phone, Fax, Email, Web (auto-populated)

#### Delivery Details Tab
- **Contact Person**: Delivery contact person
- **Address**: Delivery address
- **Contact Information**: Phone, Fax, Mobile, Email

#### Shipment Details
- **Number of Cartons**: Integer field for carton count
- **Number of Bundles**: Integer field for bundle count
- **Number of Pieces**: Integer field for piece count
- **Number of Pallets**: Integer field for pallet count
- **Number of Bags**: Integer field for bag count
- **Total No of Pieces**: Auto-calculated read-only field
- **Total Weight (Lbs)**: Float field for total weight

#### Description & Remarks
- **Description**: Rich text editor for shipment description
- **Remarks**: Rich text editor for additional remarks

## Validation Rules

### Pre-Save Validations
1. **Location Validation**: Consignment From and To cannot be the same location
2. **Total Pieces Calculation**: Automatically calculates total pieces from all shipment details
3. **Payment Validation**: 
   - If Payment By = "Shipper", Shipper (Supplier) is required
   - If Payment By = "Receiver", Consignee (Customer) is required
4. **Auto-population**: Supplier and Customer details are automatically fetched

### Submission Validations
1. **Mandatory Fields**: Consignment Date, From, To, and Payment By are required
2. **Shipment Details**: At least one shipment detail (Cartons, Bundles, Pieces, Pallets, or Bags) is required
3. **Payment-specific Requirements**: Validates supplier/customer based on payment type

## JavaScript Features

### Auto-population
- **Supplier Details**: When shipper supplier is selected, automatically populates display name, address, phone, and email
- **Customer Details**: When consignee customer is selected, automatically populates display name, address, phone, and email
- **Default Date**: Sets consignment date to today if not specified

### Dynamic Calculations
- **Total Pieces**: Real-time calculation when any shipment detail changes
- **Field Requirements**: Dynamic field requirements based on payment type selection

### Validation
- **Location Validation**: Prevents same from/to location selection
- **Pre-submission Checks**: Validates all mandatory fields before submission

### Custom Buttons
- **Print Consignment Note**: Available for submitted documents
- **Email Consignment Note**: Available for submitted documents

## Print Format

### Professional Layout
- **Header**: Clear consignment note title with document details
- **Three-column Layout**: Organized display of shipper, consignee, and delivery details
- **Shipment Table**: Structured display of all shipment quantities
- **Signature Section**: Areas for shipper, carrier, and consignee signatures
- **Footer**: Generation timestamp and document authenticity note

### Print Features
- **Responsive Design**: Adapts to different paper sizes
- **Print Optimization**: Proper page breaks and print-friendly styling
- **Conditional Display**: Only shows sections with data

## API Methods

### Server-side Methods
- `get_supplier_details(supplier)`: Returns supplier contact information
- `get_customer_details(customer)`: Returns customer contact information

### Usage Examples
```javascript
// Get supplier details
frappe.call({
    method: 'snelex.snelex.doctype.consignment_note.consignment_note.get_supplier_details',
    args: { supplier: 'SUPPLIER-001' },
    callback: function(r) {
        console.log(r.message);
    }
});
```

## Permissions

### Role-based Access
- **System Manager**: Full access (create, read, write, delete, submit, cancel)
- **Accounts Manager**: Full access (create, read, write, delete, submit, cancel)
- **Accounts User**: Limited access (create, read, write, submit - no delete)

## Testing

### Unit Tests
The doctype includes comprehensive unit tests covering:
- Basic document creation
- Total pieces calculation
- Location validation
- Payment type validation
- Submission validation
- Auto-population of supplier/customer details

### Test Execution
```bash
# Run specific tests
bench --site [site-name] run-tests snelex.snelex.doctype.consignment_note.test_consignment_note

# Run all tests for the app
bench --site [site-name] run-tests snelex
```

## Installation

### Prerequisites
- Frappe Framework
- ERPNext (for Location, Supplier, Customer doctypes)

### Installation Steps
1. Install the Snelex app
2. Run migrations: `bench --site [site-name] migrate`
3. The Consignment Note doctype will be available in the system

## Usage Workflow

### Creating a Consignment Note
1. **Navigate** to Consignment Note list
2. **Create New** consignment note
3. **Fill Basic Details**: Date, locations, payment type
4. **Add Shipper Details**: Select supplier (auto-populates details)
5. **Add Consignee Details**: Select customer (auto-populates details)
6. **Add Delivery Details**: If different from consignee
7. **Enter Shipment Details**: Quantities and weight
8. **Add Description/Remarks**: Additional information
9. **Save** as draft
10. **Submit** when ready

### After Submission
- Document becomes read-only
- Print and email options become available
- Status updates to "Submitted"
- Can be cancelled if needed

## Customization

### Adding Custom Fields
The doctype can be extended with custom fields through Frappe's customization framework without modifying core files.

### Custom Print Formats
Additional print formats can be created for different business requirements.

### Workflow Integration
Can be integrated with Frappe workflows for approval processes.

## Support

For issues or feature requests, please refer to the Snelex app documentation or contact the development team.