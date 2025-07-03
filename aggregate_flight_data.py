#!/usr/bin/env python3
"""
Flight Data Aggregation Script

Simple command-line script to aggregate flight data from multiple sources
into a centralized JSON file.

Usage:
    python aggregate_flight_data.py                    # Standard aggregation
    python aggregate_flight_data.py --force-refresh    # Force refresh (ignore existing data)
    python aggregate_flight_data.py --results-dir custom_dir  # Custom results directory
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.utils.flight_data_aggregator import FlightDataAggregator

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Aggregate flight data from multiple sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python aggregate_flight_data.py                          # Standard aggregation
  python aggregate_flight_data.py --force-refresh          # Force complete refresh
  python aggregate_flight_data.py --results-dir my_data    # Custom data directory
        """
    )
    
    parser.add_argument(
        "--results-dir", 
        default="flight_matrix_results", 
        help="Directory containing flight data files (default: flight_matrix_results)"
    )
    
    parser.add_argument(
        "--force-refresh", 
        action="store_true",
        help="Force refresh - ignore existing centralized data and rebuild from scratch"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    print("🚀 Flight Data Aggregation")
    print("="*50)
    print(f"📁 Results directory: {args.results_dir}")
    print(f"🔄 Force refresh: {args.force_refresh}")
    print(f"📊 Verbose logging: {args.verbose}")
    print("-"*50)
    
    try:
        # Create aggregator
        aggregator = FlightDataAggregator(results_dir=args.results_dir)
        
        # Run aggregation
        centralized_file = aggregator.run_aggregation(force_refresh=args.force_refresh)
        
        print(f"\n✅ SUCCESS!")
        print(f"📄 Centralized flight data saved to: {centralized_file}")
        
        # Additional file information
        if os.path.exists(centralized_file):
            file_size = os.path.getsize(centralized_file)
            file_size_mb = file_size / (1024 * 1024)
            print(f"📏 File size: {file_size_mb:.2f} MB")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 