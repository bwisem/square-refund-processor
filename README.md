# Square Refund Processor

A Python script for processing batch refunds through the Square API. This tool reads payment IDs and refund amounts from a CSV file and processes them automatically with comprehensive logging and error handling.

## Features

- **Batch Processing**: Process multiple refunds from a CSV file
- **Comprehensive Logging**: Detailed logs with timestamps for all operations
- **Error Handling**: Robust error handling with detailed error reporting
- **Environment Support**: Works with both Square sandbox and production environments
- **CSV Validation**: Validates CSV format and data before processing
- **Progress Tracking**: Real-time progress updates during processing
- **Summary Reports**: Detailed success/failure statistics

## Requirements

- Python 3.6+
- Square Python SDK (`squareup`)
- Square API access token
- CSV file with payment data

## Installation

1. Clone this repository:
```bash
git clone https://github.com/bwisem/square-refund-processor.git
cd square-refund-processor
```

2. Install required dependencies:
```bash
pip install squareup
```

## Usage

### Basic Usage

```bash
python square_refund_processor.py --csv refunds.csv --token YOUR_ACCESS_TOKEN
```

### Production Environment

```bash
python square_refund_processor.py --csv refunds.csv --token YOUR_ACCESS_TOKEN --environment production
```

### Command Line Arguments

- `--csv` (required): Path to CSV file containing payment_id and amount columns
- `--token` (required): Square API access token
- `--environment` (optional): Square API environment (`sandbox` or `production`, default: `sandbox`)

## CSV File Format

The CSV file must contain the following columns:

```csv
payment_id,amount
PAYMENT_ID_1,10.50
PAYMENT_ID_2,25.00
PAYMENT_ID_3,5.75
```

### CSV Requirements

- **Header row**: Must include `payment_id` and `amount` columns (case-sensitive)
- **payment_id**: Valid Square payment ID
- **amount**: Refund amount in dollars (positive number)
- **Encoding**: UTF-8
- **Delimiter**: Comma (,) - automatically detected

## Square API Setup

### Getting Your Access Token

1. **Sandbox Environment** (for testing):
   - Go to [Square Developer Dashboard](https://developer.squareup.com/apps)
   - Create or select your application
   - Navigate to "Credentials" tab
   - Copy the "Sandbox Access Token"

2. **Production Environment**:
   - Complete Square's application review process
   - Use the "Production Access Token" from your app credentials

### Required Permissions

Your Square application needs the following permissions:
- `PAYMENTS_READ`
- `PAYMENTS_WRITE`

## Output and Logging

The script generates detailed logs with the following information:

### Log File
- **Filename**: `square_refunds_YYYYMMDD_HHMMSS.log`
- **Location**: Same directory as the script
- **Content**: All operations, successes, failures, and summary statistics

### Console Output
- Real-time progress updates
- Success/failure notifications
- Final summary statistics

### Example Log Output
```
2024-01-15 10:30:15 - INFO - Logging initialized. Log file: square_refunds_20240115_103015.log
2024-01-15 10:30:15 - INFO - Square environment: sandbox
2024-01-15 10:30:15 - INFO - Starting refund processing from: refunds.csv
2024-01-15 10:30:15 - INFO - CSV columns found: ['payment_id', 'amount']
2024-01-15 10:30:15 - INFO - Successfully read 3 valid refund entries from CSV
2024-01-15 10:30:16 - INFO - Processing refund 1/3 - Payment ID: abc123, Amount: $10.50
2024-01-15 10:30:16 - INFO - ✓ Refund successful - Row 2 - Refund ID: def456, Status: COMPLETED, Amount: $10.50
```

## Error Handling

The script handles various error scenarios:

- **Invalid CSV format**: Missing columns, malformed data
- **Network issues**: API timeouts, connection problems
- **Square API errors**: Invalid payment IDs, insufficient funds, etc.
- **File system errors**: Missing files, permission issues

All errors are logged with detailed information for troubleshooting.

## Security Considerations

- **Never commit your access token** to version control
- Use environment variables or secure configuration files for tokens
- Test thoroughly in sandbox before using production
- Monitor refund processing logs for suspicious activity

## Example Usage Scenarios

### 1. Processing Customer Refunds
```bash
# Process a batch of customer refunds in sandbox
python square_refund_processor.py --csv customer_refunds.csv --token $SQUARE_SANDBOX_TOKEN

# Process in production after testing
python square_refund_processor.py --csv customer_refunds.csv --token $SQUARE_PRODUCTION_TOKEN --environment production
```

### 2. Handling Disputed Transactions
```bash
# Process disputed transaction refunds
python square_refund_processor.py --csv disputed_transactions.csv --token $SQUARE_TOKEN --environment production
```

## Troubleshooting

### Common Issues

1. **"square package not found"**
   ```bash
   pip install squareup
   ```

2. **"Missing required columns"**
   - Ensure CSV has `payment_id` and `amount` columns
   - Check for typos in column names (case-sensitive)
   - Verify CSV has a header row

3. **"Invalid payment_id"**
   - Verify payment IDs are correct and from the same environment
   - Check that payments exist and are eligible for refunds

4. **API Authentication Errors**
   - Verify your access token is correct
   - Ensure token has required permissions
   - Check if you're using the right environment (sandbox vs production)

### Getting Help

If you encounter issues:
1. Check the generated log file for detailed error information
2. Verify your CSV file format matches the requirements
3. Test with a small CSV file first
4. Ensure your Square application has the required permissions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Disclaimer

This tool is provided as-is for processing Square refunds. Always test thoroughly in a sandbox environment before using in production. The authors are not responsible for any financial losses or issues arising from the use of this tool.

## Support

For issues related to:
- **This script**: Open an issue on GitHub
- **Square API**: Check [Square Developer Documentation](https://developer.squareup.com/docs)
- **Square account issues**: Contact Square Support
