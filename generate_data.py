import pandas as pd
import numpy as np
import argparse
import os
from datetime import datetime, timedelta

def generate_sample_data(num_records):
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)
    
    data = {
        'date': [
            (start_date + timedelta(days=np.random.randint(0, 365))).strftime("%Y-%m-%d")
            for _ in range(num_records)
        ],
        'sales': np.random.randint(1000, 5000, num_records),
        'expenses': np.random.randint(500, 2500, num_records),
        'region': np.random.choice(['North', 'South', 'East', 'West'], num_records),
        'product': np.random.choice(['Electronics', 'Furniture', 'Apparel'], num_records)
    }
    
    df = pd.DataFrame(data)
    df.to_csv('kpi_data.csv', index=False)
    print(f"Generated {num_records} sample records in kpi_data.csv")

def interactive_mode():
    records = []
    while True:
        print("\nNew Entry (press Ctrl+C to finish):")
        try:
            date = input("Date (YYYY-MM-DD): ")
            sales = float(input("Sales amount: "))
            expenses = float(input("Expenses amount: "))
            region = input("Region (North/South/East/West): ").capitalize()
            product = input("Product (Electronics/Furniture/Apparel): ").capitalize()
            
            records.append({
                'date': datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d"),
                'sales': sales,
                'expenses': expenses,
                'region': region,
                'product': product
            })
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f"Error: {str(e)}. Please try again.")
    
    if records:
        df = pd.DataFrame(records)
        if os.path.exists('kpi_data.csv'):
            df.to_csv('kpi_data.csv', mode='a', header=False, index=False)
        else:
            df.to_csv('kpi_data.csv', index=False)
        print(f"Added {len(records)} new records to kpi_data.csv")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate sample data for KPI Dashboard")
    subparsers = parser.add_subparsers(dest='command')
    
    gen_parser = subparsers.add_parser('generate', help='Generate random entries')
    gen_parser.add_argument('-n', '--num', type=int, default=1000, help='Number of records to generate')
    
    subparsers.add_parser('interactive', help='Enter data manually')
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        generate_sample_data(args.num)
    elif args.command == 'interactive':
        interactive_mode()
    else:
        parser.print_help()