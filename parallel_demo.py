#!/usr/bin/env python3
"""
Parallel Processing Demo for Shipping Matrix

This script demonstrates how to use the new parallel processing features.
"""

import asyncio
import multiprocessing as mp
from app.utils.helpers import compute_shipping_matrix_parallel

async def demo_parallel_processing():
    """Demonstrate parallel processing capabilities."""
    
    print("🚀 SHIPPING MATRIX PARALLEL PROCESSING DEMO")
    print("=" * 60)
    
    # Show system capabilities
    cpu_count = mp.cpu_count()
    print(f"💻 Your system has {cpu_count} CPU cores available")
    print(f"📊 Recommended settings for your system:")
    print(f"   - Processes: {cpu_count} (use all cores)")
    print(f"   - City percentage: 0.1-0.5 for testing, 1.0 for full run")
    print()
    
    # Demo parameters
    date = "2025-06-25"
    container = "ST20"
    delay_range = (2, 4)  # Moderate delays
    city_percentage = 0.02  # Process 2% of cities for demo
    
    print("🔧 Demo parameters:")
    print(f"   Date: {date}")
    print(f"   Container: {container}")
    print(f"   Delay range: {delay_range[0]}-{delay_range[1]} seconds")
    print(f"   City percentage: {city_percentage * 100}%")
    print(f"   Processes: {cpu_count}")
    print()
    
    print("⚡ Starting parallel computation...")
    print("   (This will process a small subset for demonstration)")
    print()
    
    try:
        results = await compute_shipping_matrix_parallel(
            date=date,
            container=container,
            delay_range=delay_range,
            num_processes=cpu_count,
            city_percentage=city_percentage
        )
        
        print("✅ Parallel processing completed successfully!")
        print(f"📋 Results: {len(results)} shipping routes processed")
        
        if results:
            print("\n📊 Sample results:")
            for i, result in enumerate(results[:3]):  # Show first 3 results
                print(f"   {i+1}. {result['city_of_origin']} → {result['city_of_destination']}")
                print(f"      Price: ${result['price_of_shipping']} {result['currency']}")
                print(f"      Transit: {result['total_shipping_time_days']} days")
                print(f"      Carrier: {result['carrier']}")
                print()
        
        print("🎯 To run full production processing:")
        print("   python app/shipping_matrix_runner.py --parallel --city-percentage 1.0")
        print()
        print("🧪 To test with different settings:")
        print("   python app/shipping_matrix_runner.py --parallel --city-percentage 0.1 --processes 4")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Make sure all dependencies are installed and API token is valid")

if __name__ == "__main__":
    asyncio.run(demo_parallel_processing()) 