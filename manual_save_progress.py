#!/usr/bin/env python3
"""
Manual save script to save current flight matrix scraping progress.
Can be run at any time to save current results.
"""

import os
import json
import glob
from datetime import datetime
from app.matrix_flight_scraper import MatrixFlightScraper

def manual_save_current_progress():
    """Manually save all current progress from flight matrix scraping"""
    
    results_dir = "flight_matrix_results"
    
    print("🔍 Checking for current flight matrix progress...")
    
    # Check if results directory exists
    if not os.path.exists(results_dir):
        print(f"❌ No results directory found: {results_dir}")
        return
    
    # Look for any existing files
    all_files = os.listdir(results_dir)
    if not all_files:
        print("⚠️  No intermediate files found yet")
        print("💡 The scraper may not have completed its first batch yet")
        return
    
    print(f"📁 Found {len(all_files)} files in results directory")
    
    # Create a scraper instance to use its aggregation methods
    scraper = MatrixFlightScraper(max_workers=1)
    
    try:
        # Force save current progress
        print("💾 Manually saving current progress...")
        clean_results = scraper.aggregate_flight_quotes()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save manual backup
        manual_backup_file = os.path.join(results_dir, f"manual_backup_{timestamp}.json")
        with open(manual_backup_file, 'w') as f:
            json.dump(clean_results, f, indent=2, default=str)
        
        # Save CSV backup
        csv_backup_file = os.path.join(results_dir, f"manual_backup_{timestamp}.csv")
        scraper.save_quotes_to_csv(clean_results, csv_backup_file)
        
        print(f"✅ Manual backup completed!")
        print(f"   📄 JSON: {manual_backup_file}")
        print(f"   📊 CSV: {csv_backup_file}")
        print(f"   📈 Total quotes saved: {len(clean_results)}")
        
        if clean_results:
            # Show quick stats
            providers = set(q.get("source", "unknown") for q in clean_results)
            routes = set((q.get("departure_city"), q.get("destination_city")) for q in clean_results)
            
            print(f"\n📊 Current Progress:")
            print(f"   • Flight quotes: {len(clean_results)}")
            print(f"   • Unique routes: {len(routes)}")
            print(f"   • Providers: {', '.join(providers)}")
            
            # Show latest quotes
            print(f"\n🎯 Most recent quotes:")
            for i, quote in enumerate(clean_results[-3:]):
                print(f"   {i+1}. {quote.get('departure_city')} → {quote.get('destination_city')} "
                      f"${quote.get('price', 0):.2f} via {quote.get('source')}")
        
        return clean_results
        
    except Exception as e:
        print(f"❌ Error during manual save: {e}")
        return None

if __name__ == "__main__":
    manual_save_current_progress() 