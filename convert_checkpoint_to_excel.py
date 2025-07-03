#!/usr/bin/env python3
"""
Convert existing checkpoint data to Excel format with enhanced features.

This script loads the latest checkpoint data and exports it to Excel with:
- Clean screenshot URLs (no dictionary objects)
- Clickable screenshot links
- Professional formatting
- Frozen headers
- Number formatting
"""

import argparse
import logging
from app.utils.helpers import save_results_to_excel, save_results_to_csv
from app.utils.checkpoint_manager import CheckpointManager

def main():
    parser = argparse.ArgumentParser(
        description="Convert checkpoint data to Excel format",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--output-prefix",
        default="shipping_matrix_export",
        help="Prefix for output files (default: shipping_matrix_export)"
    )
    
    parser.add_argument(
        "--excel-only",
        action="store_true",
        help="Export only to Excel (skip CSV)"
    )
    
    parser.add_argument(
        "--sample-size",
        type=int,
        help="Export only first N results (useful for testing)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Load existing checkpoint data
        print("📊 Loading checkpoint data...")
        checkpoint_manager = CheckpointManager()
        checkpoint_data = checkpoint_manager.load_existing_checkpoint()
        
        if not checkpoint_data or not checkpoint_data.get('results'):
            print("❌ No checkpoint data found. Please run the shipping matrix first.")
            return
        
        results = checkpoint_data['results']
        
        # Apply sample size if specified
        if args.sample_size:
            results = results[:args.sample_size]
            print(f"📋 Using sample of {len(results)} results")
        else:
            print(f"📋 Found {len(results)} total results")
        
        # Export to Excel
        print("📊 Exporting to Excel with enhanced features...")
        excel_filename = save_results_to_excel(results, f"{args.output_prefix}.xlsx")
        
        # Export to CSV unless disabled
        if not args.excel_only:
            print("📄 Exporting to CSV with clean URLs...")
            csv_filename = save_results_to_csv(results, f"{args.output_prefix}.csv")
        
        # Show statistics
        screenshot_count = sum(1 for r in results if r.get('screenshot_url'))
        website_count = sum(1 for r in results if r.get('website_link'))
        
        print(f"\n✅ Export completed successfully!")
        print(f"📈 Statistics:")
        print(f"  • Total results exported: {len(results)}")
        print(f"  • Results with screenshots: {screenshot_count}")
        print(f"  • Results with website links: {website_count}")
        print(f"  • Screenshot coverage: {screenshot_count/len(results)*100:.1f}%")
        
        print(f"\n📁 Files created:")
        print(f"  📊 Excel: {excel_filename}")
        if not args.excel_only:
            print(f"  📄 CSV: {csv_filename}")
        
        print(f"\n🎯 Excel Features:")
        print(f"  • Clean screenshot URLs (no dictionary objects)")
        print(f"  • Clickable 'View Screenshot' links")
        print(f"  • Clickable 'View Details' links")
        print(f"  • Professional formatting with colors and borders")
        print(f"  • Number formatting for prices and amounts")
        print(f"  • Frozen header row for easy navigation")
        print(f"  • Auto-sized columns")
        
    except ImportError:
        print("❌ Excel export requires openpyxl. Install with: pip install openpyxl")
    except Exception as e:
        print(f"❌ Error during export: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 