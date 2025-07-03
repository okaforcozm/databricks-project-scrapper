#!/usr/bin/env python3
"""
Flight Data Aggregator Utility

This module provides functionality to aggregate flight data from multiple sources:
1. Individual batch result files
2. Progress files from ongoing processes  
3. Existing centralized data files
4. Manual backup files

It creates a clean, deduplicated centralized JSON file with all flight quotes.
"""

import os
import json
import glob
from datetime import datetime
from typing import List, Dict, Set, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlightDataAggregator:
    """Aggregates flight data from multiple JSON sources into centralized file"""
    
    def __init__(self, results_dir: str = "flight_matrix_results"):
        self.results_dir = results_dir
        self.centralized_file = os.path.join(results_dir, "centralized_flight_data.json")
        self.backup_file = os.path.join(results_dir, "centralized_flight_data_backup.json")
        
        # Ensure results directory exists
        os.makedirs(results_dir, exist_ok=True)
    
    def find_all_data_files(self) -> Dict[str, List[str]]:
        """Find all flight data files in the results directory"""
        
        file_patterns = {
            "batch_final": "batch_*_final_*.json",
            "batch_progress": "batch_*_progress_*.json", 
            "intermediate": "intermediate_results_*.json",
            "manual_backup": "manual_backup_*.json",
            "flight_matrix": "flight_matrix_results_*.json",
            "existing_centralized": "centralized_flight_data*.json"
        }
        
        found_files = {}
        
        for file_type, pattern in file_patterns.items():
            file_path = os.path.join(self.results_dir, pattern)
            files = glob.glob(file_path)
            found_files[file_type] = sorted(files)
            
            if files:
                logger.info(f"Found {len(files)} {file_type} files")
        
        return found_files
    
    def load_flight_data_from_file(self, file_path: str) -> List[Dict]:
        """Load flight data from a single JSON file"""
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle different file structures
            if isinstance(data, list):
                # Direct list of flight quotes
                return data
            elif isinstance(data, dict):
                # Structured data with results field
                if "results" in data:
                    return data["results"]
                elif "flight_quotes" in data:
                    return data["flight_quotes"]
                else:
                    # Try to find any list field that looks like flight data
                    for key, value in data.items():
                        if isinstance(value, list) and value and isinstance(value[0], dict):
                            # Check if it looks like flight data
                            if "departure_city" in value[0] and "destination_city" in value[0]:
                                return value
                    
                    logger.warning(f"No flight data found in {file_path}")
                    return []
            else:
                logger.warning(f"Unexpected data format in {file_path}")
                return []
                
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            return []
    
    def standardize_flight_quote(self, quote: Dict) -> Dict:
        """Standardize a flight quote to ensure all required fields are present"""
        
        standardized = {
            "departure_airport": quote.get("departure_airport", ""),
            "destination_airport": quote.get("destination_airport", ""),
            "departure_city": quote.get("departure_city", ""),
            "destination_city": quote.get("destination_city", ""),
            "origin_city_region": quote.get("origin_city_region", "UNKNOWN"),
            "destination_city_region": quote.get("destination_city_region", "UNKNOWN"),
            "flight_date": quote.get("flight_date", ""),
            "departure_time": quote.get("departure_time", ""),
            "arrival_time": quote.get("arrival_time", ""),
            "total_flight_time": quote.get("total_flight_time", ""),
            "airline_code": quote.get("airline_code", ""),
            "cabin_bags": quote.get("cabin_bags", 0),
            "checked_bags": quote.get("checked_bags", 0),
            "num_stops": quote.get("num_stops", 0),
            "price": quote.get("price", 0.0),
            "currency": quote.get("currency", "USD"),
            "num_adults": quote.get("num_adults", 1),
            "num_children": quote.get("num_children", 0),
            "num_infants": quote.get("num_infants", 0),
            "passenger_type": quote.get("passenger_type", "1A_0C_0I"),
            "scraping_datetime": quote.get("scraping_datetime", ""),
            "source": quote.get("source", "unknown"),
            "screenshot_url": quote.get("screenshot_url"),
            "booking_url": quote.get("booking_url", "")
        }
        
        return standardized
    
    def create_quote_signature(self, quote: Dict) -> str:
        """Create a unique signature for deduplication"""
        
        signature_fields = [
            quote.get("departure_city", ""),
            quote.get("destination_city", ""),
            quote.get("flight_date", ""),
            quote.get("departure_time", ""),
            quote.get("airline_code", ""),
            str(quote.get("price", 0)),
            quote.get("source", ""),
            str(quote.get("num_adults", 1)),
            str(quote.get("num_children", 0)),
            str(quote.get("num_infants", 0))
        ]
        
        return "|".join(signature_fields)
    
    def aggregate_all_data(self, force_refresh: bool = False) -> List[Dict]:
        """Aggregate all flight data from available sources"""
        
        logger.info("🔄 Starting flight data aggregation...")
        
        # Find all data files
        all_files = self.find_all_data_files()
        
        # Load existing centralized data (unless force refresh)
        existing_quotes = []
        if not force_refresh and os.path.exists(self.centralized_file):
            logger.info("📂 Loading existing centralized data...")
            existing_quotes = self.load_flight_data_from_file(self.centralized_file)
            logger.info(f"   Found {len(existing_quotes)} existing quotes")
        
        # Collect all quotes from all sources
        all_quotes = existing_quotes.copy()
        
        # Process files in priority order (most reliable first)
        file_priority = [
            "batch_final",
            "flight_matrix", 
            "manual_backup",
            "batch_progress",
            "intermediate"
        ]
        
        for file_type in file_priority:
            if file_type in all_files:
                for file_path in all_files[file_type]:
                    logger.info(f"📖 Processing {file_type}: {os.path.basename(file_path)}")
                    quotes = self.load_flight_data_from_file(file_path)
                    all_quotes.extend(quotes)
        
        logger.info(f"📊 Total quotes collected: {len(all_quotes)}")
        
        # Standardize and deduplicate
        logger.info("🔧 Standardizing and deduplicating quotes...")
        
        standardized_quotes = []
        seen_signatures = set()
        
        for quote in all_quotes:
            if not quote or not isinstance(quote, dict):
                continue
            
            # Standardize the quote
            std_quote = self.standardize_flight_quote(quote)
            
            # Skip if missing essential data
            if not (std_quote["departure_city"] and std_quote["destination_city"] and std_quote["source"]):
                continue
            
            # Create signature for deduplication
            signature = self.create_quote_signature(std_quote)
            
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                standardized_quotes.append(std_quote)
        
        logger.info(f"✅ After deduplication: {len(standardized_quotes)} unique quotes")
        
        return standardized_quotes
    
    def save_centralized_data(self, quotes: List[Dict]) -> str:
        """Save aggregated data to centralized file"""
        
        # Create backup if centralized file exists
        if os.path.exists(self.centralized_file):
            try:
                import shutil
                shutil.copy2(self.centralized_file, self.backup_file)
                logger.info(f"💾 Created backup: {self.backup_file}")
            except Exception as e:
                logger.warning(f"Could not create backup: {e}")
        
        # Prepare centralized data structure
        centralized_data = {
            "aggregation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_quotes": len(quotes),
            "data_sources": self.get_data_source_summary(),
            "statistics": self.calculate_statistics(quotes),
            "flight_quotes": quotes
        }
        
        # Save centralized file
        try:
            with open(self.centralized_file, 'w') as f:
                json.dump(centralized_data, f, indent=2, default=str)
            
            logger.info(f"✅ Saved centralized data: {self.centralized_file}")
            logger.info(f"📈 Total flight quotes: {len(quotes)}")
            
            return self.centralized_file
            
        except Exception as e:
            logger.error(f"❌ Error saving centralized data: {e}")
            raise
    
    def get_data_source_summary(self) -> Dict:
        """Get summary of data sources used"""
        
        all_files = self.find_all_data_files()
        summary = {}
        
        for file_type, files in all_files.items():
            if files:
                summary[file_type] = {
                    "count": len(files),
                    "latest": os.path.basename(files[-1]) if files else None
                }
        
        return summary
    
    def calculate_statistics(self, quotes: List[Dict]) -> Dict:
        """Calculate statistics for the aggregated data"""
        
        if not quotes:
            return {}
        
        # Count by various dimensions
        providers = {}
        routes = {}
        passenger_types = {}
        regions = {}
        
        for quote in quotes:
            # Provider stats
            provider = quote.get("source", "unknown")
            providers[provider] = providers.get(provider, 0) + 1
            
            # Route stats
            route = f"{quote.get('departure_city')} → {quote.get('destination_city')}"
            routes[route] = routes.get(route, 0) + 1
            
            # Passenger type stats
            passenger_type = quote.get("passenger_type", "unknown")
            passenger_types[passenger_type] = passenger_types.get(passenger_type, 0) + 1
            
            # Region stats
            origin_region = quote.get("origin_city_region", "unknown")
            dest_region = quote.get("destination_city_region", "unknown")
            region_pair = f"{origin_region} → {dest_region}"
            regions[region_pair] = regions.get(region_pair, 0) + 1
        
        # Price statistics
        prices = [q.get("price", 0) for q in quotes if q.get("price", 0) > 0]
        price_stats = {}
        if prices:
            price_stats = {
                "min": min(prices),
                "max": max(prices),
                "average": sum(prices) / len(prices),
                "count": len(prices)
            }
        
        return {
            "providers": providers,
            "unique_routes": len(routes),
            "passenger_types": passenger_types,
            "regional_coverage": len(regions),
            "price_statistics": price_stats
        }
    
    def run_aggregation(self, force_refresh: bool = False) -> str:
        """Run complete aggregation process"""
        
        logger.info("🚀 Starting flight data aggregation process...")
        
        # Aggregate all data
        quotes = self.aggregate_all_data(force_refresh=force_refresh)
        
        # Save centralized file
        centralized_file = self.save_centralized_data(quotes)
        
        # Print summary
        self.print_aggregation_summary(quotes)
        
        return centralized_file
    
    def print_aggregation_summary(self, quotes: List[Dict]):
        """Print summary of aggregation results"""
        
        if not quotes:
            logger.warning("⚠️  No flight quotes found!")
            return
        
        stats = self.calculate_statistics(quotes)
        
        print("\n" + "="*60)
        print("📊 FLIGHT DATA AGGREGATION SUMMARY")
        print("="*60)
        print(f"✈️  Total Flight Quotes: {len(quotes)}")
        print(f"🗺️  Unique Routes: {stats.get('unique_routes', 0)}")
        print(f"🌍 Regional Coverage: {stats.get('regional_coverage', 0)} region pairs")
        
        if "providers" in stats:
            print(f"\n🏢 Providers:")
            for provider, count in sorted(stats["providers"].items(), key=lambda x: x[1], reverse=True):
                print(f"   • {provider}: {count} quotes")
        
        if "passenger_types" in stats:
            print(f"\n👥 Passenger Configurations:")
            for ptype, count in sorted(stats["passenger_types"].items(), key=lambda x: x[1], reverse=True):
                print(f"   • {ptype}: {count} quotes")
        
        if "price_statistics" in stats and stats["price_statistics"]:
            price_stats = stats["price_statistics"]
            print(f"\n💰 Price Statistics:")
            print(f"   • Range: ${price_stats['min']:.2f} - ${price_stats['max']:.2f}")
            print(f"   • Average: ${price_stats['average']:.2f}")
            print(f"   • Quotes with prices: {price_stats['count']}")
        
        print(f"\n📁 Centralized file: {self.centralized_file}")
        print("="*60)


def main():
    """Main entry point for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aggregate flight data from multiple sources")
    parser.add_argument("--results-dir", default="flight_matrix_results", 
                       help="Directory containing flight data files")
    parser.add_argument("--force-refresh", action="store_true",
                       help="Force refresh - ignore existing centralized data")
    
    args = parser.parse_args()
    
    # Create aggregator and run
    aggregator = FlightDataAggregator(results_dir=args.results_dir)
    centralized_file = aggregator.run_aggregation(force_refresh=args.force_refresh)
    
    print(f"\n✅ Aggregation completed!")
    print(f"📄 Centralized file: {centralized_file}")


if __name__ == "__main__":
    main() 