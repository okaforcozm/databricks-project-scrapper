#!/usr/bin/env python3
"""
Quick Demo of the Matrix Flight Scraper

This runs a very limited example to show the system working.
"""

import asyncio
from app.matrix_flight_scraper import MatrixFlightScraper
from app.utils.city_regional_mapping import get_all_cities_flat

def show_available_cities():
    """Show all available cities for scraping"""
    cities = get_all_cities_flat()
    print("🌍 Available Cities for Matrix Search:")
    print("=" * 50)
    
    by_region = {}
    for city in cities:
        region = city.point_id.split('_')[0]  # Rough region grouping
        if region not in by_region:
            by_region[region] = []
        by_region[region].append(f"{city.full_name} ({city.short_code})")
    
    for region, city_list in by_region.items():
        print(f"\n📍 {region}:")
        for city in city_list[:10]:  # Limit display
            print(f"   {city}")
        if len(city_list) > 10:
            print(f"   ... and {len(city_list) - 10} more")
    
    print(f"\n📊 Total: {len(cities)} cities available")

def run_quick_demo():
    """Run a very quick demo with minimal tasks"""
    print("🚀 Quick Demo - Matrix Flight Scraper")
    print("=" * 50)
    print("This will run a small test with:")
    print("   - 2 workers")
    print("   - 3 tasks per worker (6 total)")
    print("   - Screenshots enabled")
    print("   - Regional mapping included")
    print("   - All passenger types")
    
    input("\nPress Enter to start the demo...")
    
    # Create scraper with minimal configuration
    scraper = MatrixFlightScraper(max_workers=2)
    
    # Run with very limited tasks
    scraper.run_matrix_search(max_tasks_per_worker=3)
    
    print("\n✅ Demo completed! Check the results files:")
    print("   - flight_matrix_results/ (individual worker files)")
    print("   - aggregated_flight_data.json (combined results)")

def main():
    print("🚁 Matrix Flight Scraper - Quick Demo")
    print("=" * 40)
    print("1. Show available cities")
    print("2. Run quick demo")
    print("0. Exit")
    
    choice = input("\nChoose an option (0-2): ").strip()
    
    if choice == "1":
        show_available_cities()
    elif choice == "2":
        run_quick_demo()
    elif choice == "0":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 