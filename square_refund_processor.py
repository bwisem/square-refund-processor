#!/usr/bin/env python3
"""
Square Refund Processor

This script processes a CSV file containing payment_id and refund amounts,
then calls the Square CreateRefund API for each entry and logs all results.

Requirements:
- CSV file with columns: payment_id, amount
- Square API access token
- squareup Python SDK

Usage:
    python square_refund_processor.py --csv refunds.csv --token YOUR_ACCESS_TOKEN

CSV Format:
    payment_id,amount
    PAYMENT_ID_1,10.50
    PAYMENT_ID_2,25.00
"""

import csv
import logging
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Tuple
import uuid

try:
    from square.client import Client
    from square.exceptions.api_exception import APIException
except ImportError:
    print("Error: square package not found. Install with: pip install squareup")
    sys.exit(1)


class SquareRefundProcessor:
    def __init__(self, access_token: str, environment: str = 'sandbox'):
        """
        Initialize the Square refund processor.
        
        Args:
            access_token: Square API access token
            environment: 'sandbox' or 'production'
        """
        self.access_token = access_token
        self.environment = environment
        
        # Initialize Square client
        self.client = Client(
            access_token=access_token,
            environment=environment
        )
        self.refunds_api = self.client.refunds
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup comprehensive logging configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"square_refunds_{timestamp}.log"
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Setup file handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Setup logger
        self.logger = logging.getLogger('SquareRefundProcessor')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"Logging initialized. Log file: {log_filename}")
        self.logger.info(f"Square environment: {self.environment}")
        
    def read_csv_file(self, csv_file_path: str) -> List[Dict[str, str]]:
        """
        Read and validate CSV file containing payment_id and amount.
        
        Args:
            csv_file_path: Path to the CSV file
            
        Returns:
            List of dictionaries with payment_id and amount
        """
        refund_data = []
        
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Validate required columns
                required_columns = {'payment_id', 'amount'}
                if not reader.fieldnames or not required_columns.issubset(reader.fieldnames):
                    self.logger.error(f"CSV file format issue. Found columns: {reader.fieldnames}")
                    self.logger.error("Expected columns: payment_id, amount")
                    self.logger.error("Common issues:")
                    self.logger.error("- Extra empty lines at the beginning of the file")
                    self.logger.error("- Incorrect column names (case sensitive)")
                    self.logger.error("- Missing header row")
                    missing = required_columns - set(reader.fieldnames or [])
                    raise ValueError(f"Missing required columns: {missing}")
                
                self.logger.info(f"CSV columns found: {reader.fieldnames}")
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                    payment_id = row['payment_id'].strip()
                    amount_str = row['amount'].strip()
                    
                    # Validate payment_id
                    if not payment_id:
                        self.logger.warning(f"Row {row_num}: Empty payment_id, skipping")
                        continue
                    
                    # Validate and convert amount
                    try:
                        amount = float(amount_str)
                        if amount <= 0:
                            self.logger.warning(f"Row {row_num}: Invalid amount {amount}, skipping")
                            continue
                    except ValueError:
                        self.logger.warning(f"Row {row_num}: Invalid amount format '{amount_str}', skipping")
                        continue
                    
                    refund_data.append({
                        'payment_id': payment_id,
                        'amount': amount,
                        'row_number': row_num
                    })
                
        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {csv_file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {str(e)}")
            raise
        
        self.logger.info(f"Successfully read {len(refund_data)} valid refund entries from CSV")
        return refund_data
    
    def create_refund(self, payment_id: str, amount: float) -> Tuple[bool, Dict]:
        """
        Create a refund using Square API.
        
        Args:
            payment_id: Square payment ID
            amount: Refund amount in dollars
            
        Returns:
            Tuple of (success: bool, result: dict)
        """
        try:
            # Convert amount to cents for Square API
            amount_cents = int(amount * 100)
            
            # Create refund request body
            refund_request_body = {
                'idempotency_key': str(uuid.uuid4()),
                'amount_money': {
                    'amount': amount_cents,
                    'currency': 'USD'  # Adjust currency as needed
                },
                'payment_id': payment_id,
                'reason': 'Refund processed via batch script'
            }
            
            # Make API call
            result = self.refunds_api.refund_payment(body=refund_request_body)
            
            if result.is_success():
                refund = result.body.get('refund', {})
                return True, {
                    'refund_id': refund.get('id'),
                    'status': refund.get('status'),
                    'amount': amount,
                    'currency': refund.get('amount_money', {}).get('currency'),
                    'created_at': refund.get('created_at'),
                    'payment_id': payment_id
                }
            else:
                errors = result.errors if hasattr(result, 'errors') else []
                return False, {
                    'errors': [{'code': e.get('code'), 'detail': e.get('detail')} for e in errors],
                    'payment_id': payment_id,
                    'amount': amount
                }
                
        except APIException as e:
            return False, {
                'error': 'API Exception',
                'message': str(e),
                'payment_id': payment_id,
                'amount': amount
            }
        except Exception as e:
            return False, {
                'error': 'Unexpected Error',
                'message': str(e),
                'payment_id': payment_id,
                'amount': amount
            }
    
    def process_refunds(self, csv_file_path: str) -> Dict[str, int]:
        """
        Process all refunds from CSV file.
        
        Args:
            csv_file_path: Path to CSV file
            
        Returns:
            Dictionary with processing statistics
        """
        self.logger.info(f"Starting refund processing from: {csv_file_path}")
        
        # Read CSV data
        refund_data = self.read_csv_file(csv_file_path)
        
        if not refund_data:
            self.logger.warning("No valid refund data found in CSV")
            return {'total': 0, 'successful': 0, 'failed': 0}
        
        # Process each refund
        successful_refunds = 0
        failed_refunds = 0
        
        for i, refund_info in enumerate(refund_data, 1):
            payment_id = refund_info['payment_id']
            amount = refund_info['amount']
            row_number = refund_info['row_number']
            
            self.logger.info(f"Processing refund {i}/{len(refund_data)} - Payment ID: {payment_id}, Amount: ${amount:.2f}")
            
            success, result = self.create_refund(payment_id, amount)
            
            if success:
                successful_refunds += 1
                self.logger.info(
                    f"✓ Refund successful - Row {row_number} - "
                    f"Refund ID: {result['refund_id']}, "
                    f"Status: {result['status']}, "
                    f"Amount: ${result['amount']:.2f}"
                )
            else:
                failed_refunds += 1
                if 'errors' in result:
                    error_details = '; '.join([f"{e['code']}: {e['detail']}" for e in result['errors']])
                    self.logger.error(
                        f"✗ Refund failed - Row {row_number} - "
                        f"Payment ID: {payment_id}, "
                        f"Amount: ${amount:.2f}, "
                        f"Errors: {error_details}"
                    )
                else:
                    self.logger.error(
                        f"✗ Refund failed - Row {row_number} - "
                        f"Payment ID: {payment_id}, "
                        f"Amount: ${amount:.2f}, "
                        f"Error: {result.get('error', 'Unknown')}, "
                        f"Message: {result.get('message', 'No details')}"
                    )
        
        # Log summary
        total_processed = len(refund_data)
        self.logger.info(f"\n=== PROCESSING COMPLETE ===")
        self.logger.info(f"Total refunds processed: {total_processed}")
        self.logger.info(f"Successful refunds: {successful_refunds}")
        self.logger.info(f"Failed refunds: {failed_refunds}")
        self.logger.info(f"Success rate: {(successful_refunds/total_processed)*100:.1f}%")
        
        return {
            'total': total_processed,
            'successful': successful_refunds,
            'failed': failed_refunds
        }


def main():
    """Main function to handle command line arguments and run the processor."""
    parser = argparse.ArgumentParser(
        description='Process Square refunds from CSV file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CSV Format:
    payment_id,amount
    PAYMENT_ID_1,10.50
    PAYMENT_ID_2,25.00

Examples:
    python square_refund_processor.py --csv refunds.csv --token YOUR_ACCESS_TOKEN
    python square_refund_processor.py --csv refunds.csv --token YOUR_ACCESS_TOKEN --environment production
        """
    )
    
    parser.add_argument(
        '--csv', 
        required=True, 
        help='Path to CSV file containing payment_id and amount columns'
    )
    
    parser.add_argument(
        '--token', 
        required=True, 
        help='Square API access token'
    )
    
    parser.add_argument(
        '--environment', 
        choices=['sandbox', 'production'], 
        default='sandbox',
        help='Square API environment (default: sandbox)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize processor
        processor = SquareRefundProcessor(
            access_token=args.token,
            environment=args.environment
        )
        
        # Process refunds
        results = processor.process_refunds(args.csv)
        
        # Exit with appropriate code
        if results['failed'] > 0:
            print(f"\nWarning: {results['failed']} refunds failed. Check the log file for details.")
            sys.exit(1)
        else:
            print(f"\nSuccess: All {results['successful']} refunds processed successfully.")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
