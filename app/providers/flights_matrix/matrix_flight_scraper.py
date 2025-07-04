import asyncio
import json
import os
import time
import uuid
import random
from datetime import datetime, timedelta
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Tuple
import itertools
import signal
import sys
from collections import defaultdict
import multiprocessing as mp

import uuid
from app.providers.flights_matrix.flight_search import flight_search
from app.providers.flights_matrix.utils.flight_quote_model import UserQuery
from app.utils.city_regional_mapping import get_all_cities_flat
from app.utils.flight_checkpoint_manager import FlightCheckpointManager
from app.utils.helpers import generate_biased_monthly_dates

# BASE DIRECTORY OF PROJECT
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
RESULTS_DIR = os.path.join(BASE_DIR, "flight_matrix_results")
# Ensure results directory exists at import time (for child processes)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Configuration
SAVE_INTERVAL = 120  # 2 minutes in seconds for more frequent saves
AGGREGATED_FILE = "aggregated_flight_data.json"
MAX_WORKERS = 4

# Throttling and Rate Limiting Configuration
BASE_DELAY = 3  # Base delay between requests in seconds
MAX_DELAY = 30  # Maximum delay for exponential backoff
JITTER_RANGE = 0.5  # Random jitter factor (±50%)
MAX_RETRIES = 3  # Maximum number of retries per task
RETRY_DELAY_MULTIPLIER = 2  # Exponential backoff multiplier

# Provider-specific rate limits (requests per minute)
PROVIDER_RATE_LIMITS = {
    "booking.com": 15,  # Conservative rate limit
    "kiwi": 20,        # Slightly higher for Kiwi
    "default": 10      # Default for unknown providers
}

# Circuit breaker thresholds
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5  # Consecutive failures before opening circuit
CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 300  # 5 minutes before trying again

# Passenger configurations
PASSENGER_CONFIGS = [
    {"name": "Single", "adults": 1, "children": 0, "infants": 0},
    # {"name": "Couple", "adults": 2, "children": 0, "infants": 0},
    # {"name": "Couple+1", "adults": 2, "children": 1, "infants": 0},
    # {"name": "Couple+2", "adults": 2, "children": 2, "infants": 0},
]

# Global counter for individual results
INDIVIDUAL_RESULT_COUNTER = 0

class RateLimiter:
    """Smart rate limiter with per-provider limits and adaptive delays"""
    
    def __init__(self):
        self.last_request_times = {}
        self.failure_counts = {}
        self.circuit_breaker_open_until = {}
    
    def calculate_delay(self, provider: str = "default", failure_count: int = 0) -> float:
        """Calculate adaptive delay based on provider and failure count"""
        base_rate_limit = PROVIDER_RATE_LIMITS.get(provider, PROVIDER_RATE_LIMITS["default"])
        min_interval = 60.0 / base_rate_limit  # Convert RPM to seconds between requests
        
        # Exponential backoff for failures
        if failure_count > 0:
            backoff_delay = min(BASE_DELAY * (RETRY_DELAY_MULTIPLIER ** failure_count), MAX_DELAY)
        else:
            backoff_delay = BASE_DELAY
        
        # Use the longer of rate limit or backoff delay
        delay = max(min_interval, backoff_delay)
        
        # Add jitter to avoid thundering herd
        jitter = random.uniform(-JITTER_RANGE, JITTER_RANGE) * delay
        final_delay = max(0.1, delay + jitter)  # Minimum 0.1 second delay
        
        return final_delay
    
    def is_circuit_open(self, provider: str) -> bool:
        """Check if circuit breaker is open for a provider"""
        if provider in self.circuit_breaker_open_until:
            if time.time() < self.circuit_breaker_open_until[provider]:
                return True
            else:
                # Recovery time passed, reset failure count
                del self.circuit_breaker_open_until[provider]
                self.failure_counts[provider] = 0
        return False
    
    def record_failure(self, provider: str):
        """Record a failure and potentially open circuit breaker"""
        if provider not in self.failure_counts:
            self.failure_counts[provider] = 0
        self.failure_counts[provider] += 1
        if self.failure_counts[provider] >= CIRCUIT_BREAKER_FAILURE_THRESHOLD:
            self.circuit_breaker_open_until[provider] = time.time() + CIRCUIT_BREAKER_RECOVERY_TIMEOUT
            print(f"🔴 Circuit breaker OPEN for {provider} (too many failures)")
    
    def record_success(self, provider: str):
        """Record a success and reset failure count"""
        self.failure_counts[provider] = 0
        if provider in self.circuit_breaker_open_until:
            del self.circuit_breaker_open_until[provider]
    
    async def wait_for_rate_limit(self, provider: str = "default", failure_count: int = 0):
        """Wait according to rate limit and failure count"""
        if self.is_circuit_open(provider):
            print(f"🔴 Skipping request - circuit breaker open for {provider}")
            return False
        
        delay = self.calculate_delay(provider, failure_count)
        
        # Clean old request times (older than 1 minute)
        current_time = time.time()
        if provider not in self.last_request_times:
            self.last_request_times[provider] = []
        
        self.last_request_times[provider] = [
            t for t in self.last_request_times[provider] 
            if current_time - t < 60
        ]
        
        # Check if we need to wait based on recent requests
        if len(self.last_request_times[provider]) > 0:
            time_since_last = current_time - self.last_request_times[provider][-1]
            if time_since_last < delay:
                additional_wait = delay - time_since_last
                print(f"⏱️  Rate limiting: waiting {additional_wait:.1f}s for {provider}")
                await asyncio.sleep(additional_wait)
        
        # Record this request time
        self.last_request_times[provider].append(time.time())
        return True

class TaskProcessor:
    """Robust task processor with retries and error handling"""
    
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
        self.stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "skipped_tasks": 0,
            "total_quotes": 0,
            "provider_success": {},
            "provider_failures": {}
        }
    
    async def process_task_with_retries(self, task: Dict) -> List[Dict]:
        """Process a single task with retries and error handling"""
        self.stats["total_tasks"] += 1
        
        for attempt in range(MAX_RETRIES + 1):
            try:
                # Check rate limits before attempting
                can_proceed = await self.rate_limiter.wait_for_rate_limit(
                    provider="default",  # We don't know provider until after search
                    failure_count=attempt
                )
                
                if not can_proceed:
                    self.stats["skipped_tasks"] += 1
                    return []
                
                # Create UserQuery
                user_query = UserQuery(
                    origin_city=task["origin_city"],
                    destination_city=task["destination_city"],
                    departure_date=task["departure_date"],
                    departure_time=task["departure_time"],
                    airline=task["airline"],
                    search_location=task["search_location"],
                    quoted_price=task["quoted_price"],
                    num_adults=task["passenger_config"]["adults"],
                    num_children=task["passenger_config"]["children"],
                    num_infants=task["passenger_config"]["infants"],
                )
                
                # Prepare region info for flight search
                region_info = {
                    "origin_city_region": task["origin_city_region"],
                    "destination_city_region": task["destination_city_region"]
                }
                
                # Run flight search with timeout
                results = await asyncio.wait_for(
                    flight_search(user_query, region_info),
                    timeout=60.0  # 60 second timeout per search
                )
                
                # Check if we got results
                if not results:
                    print(f"⚠️  No quotes returned for {task['origin_city']} → {task['destination_city']} (attempt {attempt + 1})")
                    if attempt < MAX_RETRIES:
                        continue
                    else:
                        self.stats["failed_tasks"] += 1
                        return []
                
                # Record success for each provider
                providers_used = set()
                for result in results:
                    provider = result.get("source", "unknown")
                    providers_used.add(provider)
                    self.rate_limiter.record_success(provider)
                    if provider not in self.stats["provider_success"]:
                        self.stats["provider_success"][provider] = 0
                    self.stats["provider_success"][provider] += 1
                
                # Add metadata to results
                for result in results:
                    result.update({
                        "search_task_id": task["task_id"],
                        "passenger_type": task["passenger_config"]["name"],
                        "num_passengers": task["passenger_config"]["adults"] + task["passenger_config"]["children"] + task["passenger_config"]["infants"],
                        "origin_city_region": task["origin_city_region"],
                        "destination_city_region": task["destination_city_region"],
                        "attempt_number": attempt + 1,
                        # "search_params": {
                        #     "origin": task["origin_city"],
                        #     "destination": task["destination_city"],
                        #     "origin_name": task["origin_city_name"],
                        #     "destination_name": task["destination_city_name"],
                        #     "departure_date": task["departure_date"],
                        #     "adults": task["passenger_config"]["adults"],
                        #     "children": task["passenger_config"]["children"],
                        #     "infants": task["passenger_config"]["infants"]
                        # }
                    })
                
                self.stats["successful_tasks"] += 1
                self.stats["total_quotes"] += len(results)
                
                print(f"✅ Found {len(results)} quotes for {task['origin_city']} → {task['destination_city']} "
                      f"({task['passenger_config']['name']}) [attempt {attempt + 1}]")
                
                return results
                
            except asyncio.TimeoutError:
                error_msg = f"⏱️  Timeout for {task['origin_city']} → {task['destination_city']} (attempt {attempt + 1})"
                print(error_msg)
                self.rate_limiter.record_failure("timeout")
                
            except Exception as e:
                error_msg = f"❌ Error for {task['origin_city']} → {task['destination_city']} (attempt {attempt + 1}): {str(e)}"
                print(error_msg)
                
                # Record failure for rate limiting
                self.rate_limiter.record_failure("general")
                
                # If this is the last attempt, mark as failed
                if attempt == MAX_RETRIES:
                    self.stats["failed_tasks"] += 1
                    return []
            
            # Wait before retry (exponential backoff)
            if attempt < MAX_RETRIES:
                retry_delay = BASE_DELAY * (RETRY_DELAY_MULTIPLIER ** attempt)
                jitter = random.uniform(0, retry_delay * 0.3)
                total_delay = retry_delay + jitter
                print(f"🔄 Retrying in {total_delay:.1f}s...")
                await asyncio.sleep(total_delay)
        
        # All retries exhausted
        self.stats["failed_tasks"] += 1
        return []
    
    def get_stats_summary(self) -> str:
        """Get formatted statistics summary"""
        success_rate = (self.stats["successful_tasks"] / max(1, self.stats["total_tasks"])) * 100
        
        summary = f"""
📊 Task Processing Statistics:
   Total Tasks: {self.stats["total_tasks"]}
   Successful: {self.stats["successful_tasks"]} ({success_rate:.1f}%)
   Failed: {self.stats["failed_tasks"]}
   Skipped: {self.stats["skipped_tasks"]}
   Total Quotes: {self.stats["total_quotes"]}
   
🎯 Provider Performance:
"""
        for provider in set(list(self.stats["provider_success"].keys()) + list(self.stats["provider_failures"].keys())):
            success = self.stats["provider_success"][provider]
            failures = self.stats["provider_failures"][provider]
            total = success + failures
            rate = (success / max(1, total)) * 100
            summary += f"   {provider}: {success}/{total} ({rate:.1f}%)\n"
        
        return summary

def process_flight_batch(batch_data: Dict[str, any]) -> List[Dict[str, any]]:
    """
    Process a batch of flight search tasks synchronously for ProcessPoolExecutor.
    
    Args:
        batch_data: Dictionary containing tasks and configuration
        
    Returns:
        List of flight search results
    """
    import asyncio
    
    # Extract data from batch
    tasks = batch_data["tasks"]
    batch_id = batch_data.get("batch_id", 0)
    delay_range = batch_data.get("delay_range", (3, 7))
    checkpoint_dir = batch_data.get("checkpoint_dir", "flight_checkpoints")
    
    print(f"🔄 Worker {batch_id}: Processing {len(tasks)} flight search tasks with checkpointing")
    
    # Create checkpoint manager for this worker process
    checkpoint_manager = FlightCheckpointManager(
        checkpoint_dir=checkpoint_dir,
        checkpoint_interval_minutes=10  # 10-minute intervals
    )
    
    # Run the async batch processing
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        results = loop.run_until_complete(
            compute_flight_batch_async(tasks, batch_id, delay_range, checkpoint_manager)
        )
        print(f"✅ Worker {batch_id}: Completed {len(results)} searches with checkpointing")
        return results
    except Exception as e:
        print(f"❌ Worker {batch_id}: Error processing batch - {e}")
        return []
    finally:
        loop.close()

def save_single_result_immediately(task_results: List[Dict], task_info: Dict, batch_id: int, task_number: int):
    """Save individual flight results immediately after each request completes"""
    global INDIVIDUAL_RESULT_COUNTER
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for result in task_results:
            INDIVIDUAL_RESULT_COUNTER += 1
            
            # Create individual result file for each quote
            single_result_file = os.path.join(RESULTS_DIR, f"single_result_{INDIVIDUAL_RESULT_COUNTER}_{timestamp}.json")
            
            result_with_metadata = {
                "result_number": INDIVIDUAL_RESULT_COUNTER,
                "batch_id": batch_id,
                "task_number": task_number,
                "timestamp": timestamp,
                "task_info": {
                    "origin_city": task_info.get("origin_city"),
                    "destination_city": task_info.get("destination_city"),
                    "departure_date": task_info.get("departure_date"),
                    "passenger_config": task_info.get("passenger_config")
                },
                "flight_data": result,
                "saved_at": datetime.now().isoformat()
            }
            
            with open(single_result_file, 'w') as f:
                json.dump(result_with_metadata, f, indent=2, default=str)
            
            print(f"💾 IMMEDIATE SAVE #{INDIVIDUAL_RESULT_COUNTER}: {task_info['origin_city']} → {task_info['destination_city']} | File: {single_result_file}")
        
        # Trigger auto-aggregation for single source of truth
        trigger_auto_aggregation(f"single_result_{INDIVIDUAL_RESULT_COUNTER}")
        
        return len(task_results)
        
    except Exception as e:
        print(f"❌ Failed to save individual results: {e}")
        return 0

async def compute_flight_batch_async(
    tasks: List[Dict], 
    batch_id: int,
    delay_range: tuple,
    checkpoint_manager: FlightCheckpointManager = None
) -> List[Dict[str, any]]:
    """
    Process a batch of flight search tasks asynchronously with checkpointing.
    SAVES EVERY 10 MINUTES and after each individual request completes.
    
    Args:
        tasks: List of flight search task dictionaries
        batch_id: Batch identifier for logging
        delay_range: Tuple of (min, max) seconds for delays
        checkpoint_manager: Checkpoint manager for saving progress
        
    Returns:
        List of flight search results
    """
    results = []
    completed_tasks = []
    rate_limiter = RateLimiter()
    task_processor = TaskProcessor(rate_limiter)
    last_checkpoint_time = datetime.now()
    
    print(f"🔄 Batch {batch_id}: Starting CHECKPOINTED processing of {len(tasks)} tasks")
    print(f"⚡ Each flight result saved immediately + 10-minute checkpoints!")
    
    for i, task in enumerate(tasks):
        try:
            # Add random delay to prevent overwhelming APIs
            if i > 0:  # Skip delay for first task
                delay = random.uniform(delay_range[0], delay_range[1])
                await asyncio.sleep(delay)
            
            # Process the task with retries
            task_results = await task_processor.process_task_with_retries(task)
            
            if task_results:
                # IMMEDIATE SAVE: Save each result immediately
                saved_count = save_single_result_immediately(task_results, task, batch_id, i + 1)
                
                results.extend(task_results)
                completed_tasks.append(task)
                
                print(f"✅ Batch {batch_id}: Task {i+1}/{len(tasks)} - Got {len(task_results)} quotes → SAVED {saved_count} individually")
                
                # 10-MINUTE CHECKPOINT: Check if we should save checkpoint
                current_time = datetime.now()
                time_since_checkpoint = (current_time - last_checkpoint_time).total_seconds() / 60
                
                if checkpoint_manager and time_since_checkpoint >= 10 and results:
                    batch_info = {
                        'batch_id': batch_id,
                        'tasks_processed': i + 1,
                        'total_tasks': len(tasks),
                        'results_count': len(results)
                    }
                    
                    checkpoint_file = checkpoint_manager.save_worker_checkpoint(
                        worker_id=batch_id,
                        batch_results=results.copy(),
                        completed_tasks=completed_tasks.copy(),
                        batch_info=batch_info
                    )
                    
                    if checkpoint_file:
                        print(f"⏰ Batch {batch_id}: 10-minute checkpoint saved - {len(results)} results")
                        last_checkpoint_time = current_time
                
                # Also save batch progress every 5 tasks for backup
                if (i + 1) % 5 == 0:
                    save_batch_progress(batch_id, results, i + 1, len(tasks))
            else:
                print(f"⚠️  Batch {batch_id}: Task {i+1}/{len(tasks)} - No results from {task['origin_city']} → {task['destination_city']}")
                
        except Exception as e:
            print(f"❌ Batch {batch_id}: Task {i+1}/{len(tasks)} failed - {e}")
            continue
    
    # Save final batch checkpoint
    if checkpoint_manager and results:
        final_batch_info = {
            'batch_id': batch_id,
            'tasks_processed': len(tasks),
            'total_tasks': len(tasks),
            'results_count': len(results),
            'status': 'completed'
        }
        
        checkpoint_manager.save_worker_checkpoint(
            worker_id=batch_id,
            batch_results=results,
            completed_tasks=completed_tasks,
            batch_info=final_batch_info
        )
        print(f"🏁 Batch {batch_id}: Final checkpoint saved - {len(results)} total results")
    
    # Save final batch results (legacy backup)
    save_batch_final_results(batch_id, results, len(tasks))
    
    # Print batch statistics
    stats_summary = task_processor.get_stats_summary()
    print(f"📊 Batch {batch_id} completed: {stats_summary}")
    
    return results

def save_batch_progress(batch_id: int, results: List[Dict], completed_tasks: int, total_tasks: int):
    """Save individual batch progress and trigger aggregation"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        progress_file = os.path.join(RESULTS_DIR, f"batch_{batch_id}_progress_{timestamp}.json")
        
        progress_data = {
            "batch_id": batch_id,
            "timestamp": timestamp,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "progress_percent": (completed_tasks / total_tasks * 100),
            "results_count": len(results),
            "results": results
        }
        
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2, default=str)
        
        print(f"💾 Batch {batch_id}: Saved progress ({completed_tasks}/{total_tasks} tasks)")
        
        # Trigger automatic aggregation
        trigger_auto_aggregation(f"batch_{batch_id}_progress")
        
    except Exception as e:
        print(f"❌ Error saving batch progress: {e}")

def save_batch_final_results(batch_id: int, results: List[Dict], total_tasks: int):
    """Save final batch results and trigger aggregation"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_file = os.path.join(RESULTS_DIR, f"batch_{batch_id}_final_{timestamp}.json")
        
        final_data = {
            "batch_id": batch_id,
            "timestamp": timestamp,
            "total_tasks": total_tasks,
            "results_count": len(results),
            "completion_status": "completed",
            "results": results
        }
        
        with open(final_file, 'w') as f:
            json.dump(final_data, f, indent=2, default=str)
        
        print(f"✅ Batch {batch_id}: Saved final results ({len(results)} flight quotes)")
        
        # Trigger automatic aggregation
        trigger_auto_aggregation(f"batch_{batch_id}_final")
        
    except Exception as e:
        print(f"❌ Error saving batch final results: {e}")

def trigger_auto_aggregation(trigger_source: str):
    """Automatically aggregate all flight data whenever a batch saves"""
    try:
        print(f"🔄 Auto-aggregation triggered by: {trigger_source}")
        
        # Import here to avoid circular imports
        from app.utils.flight_data_aggregator import FlightDataAggregator
        
        # Create aggregator and run
        aggregator = FlightDataAggregator(results_dir=RESULTS_DIR)
        centralized_file = aggregator.run_aggregation(force_refresh=False)
        
        # Get basic stats
        if os.path.exists(centralized_file):
            with open(centralized_file, 'r') as f:
                data = json.load(f)
            total_quotes = data.get("total_quotes", 0)
            print(f"✅ Auto-aggregation completed: {total_quotes} total quotes in {centralized_file}")
        else:
            print(f"✅ Auto-aggregation completed: {centralized_file}")
        
    except Exception as e:
        print(f"⚠️  Auto-aggregation failed: {e}")
        print("💡 You can run aggregation manually with: python aggregate_flight_data.py")

class MatrixFlightScraper:
    """Flight matrix scraper using ProcessPoolExecutor for parallel processing with checkpointing"""
    
    def __init__(self, max_workers=MAX_WORKERS, enable_checkpointing=True, checkpoint_dir="flight_checkpoints"):
        self.max_workers = max_workers
        self.results_dir = RESULTS_DIR
        self.aggregated_file = AGGREGATED_FILE
        self.all_results = []
        self.executor = None  # Will hold ProcessPoolExecutor reference
        self.is_shutting_down = False
        self.enable_checkpointing = enable_checkpointing
        self.checkpoint_dir = checkpoint_dir
        
        # Initialize checkpoint manager
        if self.enable_checkpointing:
            self.checkpoint_manager = FlightCheckpointManager(
                checkpoint_dir=checkpoint_dir,
                checkpoint_interval_minutes=10
            )
        else:
            self.checkpoint_manager = None
        
        # Ensure results directory exists
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print(f"🚀 Flight Matrix Scraper initialized with {max_workers} workers")
        print(f"📁 Results directory: {self.results_dir}")
        if self.enable_checkpointing:
            print(f"💾 Checkpointing enabled: {checkpoint_dir} (10-minute intervals)")
        else:
            print("⚠️  Checkpointing disabled")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully - properly stop all processes"""
        if self.is_shutting_down:
            print("\n⚠️  Already shutting down, please wait...")
            return
        
        self.is_shutting_down = True
        signal_names = {signal.SIGINT: "SIGINT (Ctrl+C)", signal.SIGTERM: "SIGTERM"}
        signal_name = signal_names.get(signum, f"Signal {signum}")
        
        print(f"\n🛑 Received {signal_name}. Initiating graceful shutdown...")
        print("💾 Saving current progress...")
        
        try:
            # Save final checkpoint if checkpointing is enabled
            if self.checkpoint_manager:
                print("🔄 Saving final checkpoint...")
                self.checkpoint_manager.save_final_checkpoint(self.all_results)
                print("✅ Final checkpoint saved")
            
            # Save current progress immediately (legacy backup)
            if self.all_results:
                self.save_final_results()
                print(f"✅ Saved {len(self.all_results)} results before shutdown")
            else:
                print("⚠️  No results to save in current session")
            
            # Show resume information
            if self.checkpoint_manager:
                print("\n📋 To resume this computation later:")
                print("   python run_full_flight_matrix.py --resume")
                print(f"   (Checkpoint data saved in: {self.checkpoint_dir})")
            
            # Shutdown ProcessPoolExecutor if it exists
            if self.executor:
                print("🔄 Shutting down worker processes...")
                self.executor.shutdown(wait=False)  # Don't wait for completion
                print("✅ Worker processes shutdown initiated")
            
        except Exception as e:
            print(f"❌ Error during graceful shutdown: {e}")
        
        print("👋 Shutdown complete. Exiting...")
        os._exit(0)  # Force exit to ensure all processes are terminated

    def generate_city_combinations(self) -> List[Tuple[Dict, Dict]]:
        """Generate all city-to-city combinations with region info"""
        cities = get_all_cities_flat()
        
        # Create city info dict for easy lookup
        city_info = {}
        for city in cities:
            city_info[city.short_code] = {
                "code": city.short_code,
                "name": city.full_name,
                "region": None  # We'll get this from the regional mapping
            }
        
        # Get region information
        from app.utils.city_regional_mapping import REGIONAL_CITY_MAPPING
        for region, region_cities in REGIONAL_CITY_MAPPING.items():
            for city in region_cities:
                if city.short_code in city_info:
                    city_info[city.short_code]["region"] = region.value
        
        # Generate all combinations (excluding same city pairs)
        combinations = []
        for origin_code in city_info.keys():
            for dest_code in city_info.keys():
                if origin_code != dest_code:
                    combinations.append((city_info[origin_code], city_info[dest_code]))
        
        return combinations
    
    def generate_search_tasks(self) -> List[Dict]:
        """Generate all search tasks (city combinations × passenger configs) with random distribution"""
        city_combinations = self.generate_city_combinations()
        search_tasks = []
        
        print(f"🌍 Generating tasks for {len(city_combinations)} city combinations")
        print(f"👥 With {len(PASSENGER_CONFIGS)} passenger configurations")
        
        # Generate all possible task combinations first
        for origin_info, destination_info in city_combinations:
            for passenger_config in PASSENGER_CONFIGS:
                start = datetime.now()
                dates_list = generate_biased_monthly_dates(start, total_dates=125, bias_months=(3,12), bias_ratio=0.6)
                for departure_date in dates_list:
                    
                    task = {
                        "task_id": str(uuid.uuid4()),
                        "origin_city": origin_info["code"],
                        "destination_city": destination_info["code"],
                        "origin_city_name": origin_info["name"],
                        "destination_city_name": destination_info["name"],
                        "origin_city_region": origin_info["region"],
                        "destination_city_region": destination_info["region"],
                        "departure_date": departure_date,
                        "departure_time": "10:00",
                        "passenger_config": passenger_config,
                        "airline": "",
                        "search_location": f"{origin_info['code']}-{destination_info['code']}",
                        "quoted_price": 0.0,
                    }
                    search_tasks.append(task)
        
        # RANDOMIZE THE TASK ORDER for diverse batches
        print(f"🎲 Randomizing {len(search_tasks)} tasks for diverse regional distribution...")
        random.shuffle(search_tasks)
        
        # Print distribution preview
        self.print_task_distribution_preview(search_tasks[:150])  # Preview first 150 tasks
        
        return search_tasks
    
    def print_task_distribution_preview(self, sample_tasks: List[Dict]):
        """Print a preview of task distribution to show regional diversity"""
        if not sample_tasks:
            return
            
        print(f"\n📊 RANDOMIZED TASK DISTRIBUTION PREVIEW (first {len(sample_tasks)} tasks):")
        print("-" * 70)
        
        # Count by region pairs
        region_pairs = {}
        passenger_types = {}
        cities = set()
        
        for task in sample_tasks:
            # Region pair
            region_pair = f"{task['origin_city_region']} → {task['destination_city_region']}"
            region_pairs[region_pair] = region_pairs.get(region_pair, 0) + 1
            
            # Passenger config
            pconfig = task['passenger_config']
            passenger_type = pconfig['name'] if isinstance(pconfig, dict) else str(pconfig)
            passenger_types[passenger_type] = passenger_types.get(passenger_type, 0) + 1
            
            # Cities
            cities.add(f"{task['origin_city_name']} → {task['destination_city_name']}")
        
        print(f"🌍 Region Pair Distribution:")
        for region_pair, count in sorted(region_pairs.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(sample_tasks)) * 100
            print(f"   • {region_pair}: {count} tasks ({percentage:.1f}%)")
        
        print(f"\n👥 Passenger Configuration Distribution:")
        for ptype, count in sorted(passenger_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(sample_tasks)) * 100
            print(f"   • {ptype}: {count} tasks ({percentage:.1f}%)")
        
        print(f"\n🏙️  Unique City Routes: {len(cities)}")
        if len(cities) <= 10:
            for city_route in sorted(cities):
                print(f"   • {city_route}")
        else:
            sample_cities = list(sorted(cities))[:10]
            for city_route in sample_cities:
                print(f"   • {city_route}")
            print(f"   ... and {len(cities) - 10} more routes")
        
        print("-" * 70)
        print("✅ Tasks randomized - each batch will have diverse regional coverage!")
        print()
    
    def run_matrix_search_parallel(self, max_tasks_per_worker=50, resume=False):
        """
        Run flight matrix search using ProcessPoolExecutor for parallel processing.
        
        Args:
            max_tasks_per_worker: Maximum number of tasks per worker process
            resume: Whether to resume from existing checkpoint
        """
        print("="*80)
        print("🚀 STARTING FLIGHT MATRIX SEARCH WITH PROCESSPOOL EXECUTOR")
        print("="*80)
        
        # Check for existing checkpoint and resume if requested
        if resume and self.checkpoint_manager:
            print("🔄 Checking for existing checkpoint...")
            checkpoint_data = self.checkpoint_manager.load_existing_checkpoint()
            
            if checkpoint_data['has_checkpoint']:
                resume_summary = self.checkpoint_manager.get_resume_summary()
                print("\n📋 RESUME INFORMATION:")
                print(f"   • Completed task combinations: {resume_summary.get('completed_task_combinations', 0)}")
                print(f"   • Worker checkpoint files: {resume_summary.get('worker_checkpoint_files', 0)}")
                print(f"   • Total quotes found: {resume_summary.get('total_quotes_found', 0)}")
                print(f"   • Routes covered: {resume_summary.get('routes_covered', 0)}")
                print(f"   • Latest checkpoint: {resume_summary.get('latest_checkpoint_time', 'Unknown')}")
                
                try:
                    response = input("\n❓ Resume from existing checkpoint? (Y/n): ")
                    if response.lower() not in ['n', 'no']:
                        print("✅ Resuming from checkpoint...")
                    else:
                        print("🔄 Starting fresh (checkpoint data will be cleared)")
                        self.checkpoint_manager.clear_checkpoints()
                except KeyboardInterrupt:
                    print("\n👋 Cancelled by user")
                    return []
            else:
                print("ℹ️  No existing checkpoint found, starting fresh")
        elif resume and not self.checkpoint_manager:
            print("⚠️  Resume requested but checkpointing is disabled")
        
        # Generate all search tasks
        all_tasks = self.generate_search_tasks()
        
        if not all_tasks:
            print("❌ No tasks generated. Exiting.")
            return
        
        # Filter out completed tasks if resuming
        if self.checkpoint_manager:
            original_count = len(all_tasks)
            all_tasks = self.checkpoint_manager.filter_uncompleted_tasks(all_tasks)
            
            if len(all_tasks) < original_count:
                print(f"🔄 Resume mode: {original_count - len(all_tasks)} tasks already completed")
                print(f"📝 Remaining tasks: {len(all_tasks)}")
                
                if len(all_tasks) == 0:
                    print("🎉 All tasks already completed! Running final aggregation...")
                    trigger_auto_aggregation("resume_all_completed")
                    return []
        
        print(f"📊 Processing {len(all_tasks)} search tasks")
        print(f"👥 Using {self.max_workers} worker processes")
        print(f"📦 Max tasks per worker: {max_tasks_per_worker}")
        if self.enable_checkpointing:
            print(f"💾 Checkpointing: Every 10 minutes + centralized aggregation")
        print(f"⚠️  Press Ctrl+C at any time to save progress and exit gracefully")
        
        # Split tasks into batches for workers
        task_batches = []
        for i in range(0, len(all_tasks), max_tasks_per_worker):
            batch_tasks = all_tasks[i:i + max_tasks_per_worker]
            batch_data = {
                "tasks": batch_tasks,
                "batch_id": i // max_tasks_per_worker + 1,
                "delay_range": (BASE_DELAY, MAX_DELAY),
                "checkpoint_dir": self.checkpoint_dir,  # Pass checkpoint directory to workers
            }
            task_batches.append(batch_data)
        
        print(f"📦 Split into {len(task_batches)} batches")
        
        # Process batches in parallel using ProcessPoolExecutor
        start_time = time.time()
        last_save_time = start_time
        all_results = []
        
        try:
            # Create and store executor reference for proper shutdown
            self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
            
            with self.executor as executor:
                print("🔄 Starting parallel processing with ProcessPoolExecutor...")
                
                # Submit all batch jobs
                future_to_batch = {
                    executor.submit(process_flight_batch, batch_data): batch_data["batch_id"]
                    for batch_data in task_batches
                }
                
                print(f"📤 Submitted {len(future_to_batch)} batch jobs to workers")
                
                # Collect results as they complete
                completed_batches = 0
                for future in future_to_batch:
                    # Check if we're shutting down
                    if self.is_shutting_down:
                        print("🛑 Shutdown requested, cancelling remaining tasks...")
                        break
                    
                    try:
                        batch_results = future.result(timeout=1200)  # 20 minutes timeout per batch
                        batch_id = future_to_batch[future]
                        
                        if batch_results:
                            all_results.extend(batch_results)
                            print(f"✅ Batch {batch_id} completed: {len(batch_results)} results")
                        else:
                            print(f"⚠️  Batch {batch_id} completed with no results")
                        
                        completed_batches += 1
                        print(f"📊 Progress: {completed_batches}/{len(task_batches)} batches completed")
                        
                        # Save intermediate results every 2 minutes (SAVE_INTERVAL = 120 seconds)
                        current_time = time.time()
                        if current_time - last_save_time >= SAVE_INTERVAL:
                            print(f"⏰ 2 minutes elapsed - saving intermediate results...")
                            self.all_results = all_results  # Update for signal handler
                            self.save_intermediate_results(all_results, completed_batches)
                            last_save_time = current_time
                        
                        # Also save every 3 batches as backup to ensure no data loss
                        elif completed_batches % 3 == 0:
                            print(f"💾 Batch checkpoint - saving intermediate results...")
                            self.all_results = all_results  # Update for signal handler
                            self.save_intermediate_results(all_results, completed_batches)
                        
                    except Exception as e:
                        batch_id = future_to_batch[future]
                        print(f"❌ Batch {batch_id} failed: {e}")
                        continue
                
                # Cancel any remaining futures if shutting down
                if self.is_shutting_down:
                    for future in future_to_batch:
                        if not future.done():
                            future.cancel()
                    print("🛑 Cancelled remaining batch jobs")
        
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt detected")
            self.is_shutting_down = True
            # The signal handler will take care of saving and cleanup
            
        except Exception as e:
            print(f"❌ Error in parallel processing: {e}")
            self.is_shutting_down = True
        
        finally:
            # Ensure executor is cleaned up
            self.executor = None
        
        # Final processing (only if not shutting down)
        if not self.is_shutting_down:
            elapsed_time = time.time() - start_time
            
            print("="*80)
            print("📊 FLIGHT MATRIX SEARCH COMPLETED")
            print("="*80)
            print(f"⏱️  Total processing time: {elapsed_time:.2f} seconds")
            print(f"📈 Total results collected: {len(all_results)}")
            print(f"📦 Processed {completed_batches}/{len(task_batches)} batches")
            
            if completed_batches > 0:
                print(f"⚡ Average time per batch: {elapsed_time/completed_batches:.2f}s")
            
            # Save final results and get clean flight quotes
            self.all_results = all_results
            clean_flight_quotes = self.save_final_results()
            
            return clean_flight_quotes
        else:
            print("🛑 Search terminated by user")
            return self.all_results if hasattr(self, 'all_results') else []

    def save_intermediate_results(self, results: List[Dict], batch_count: int):
        """Save intermediate results during processing"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        intermediate_file = os.path.join(
            self.results_dir, 
            f"intermediate_results_batch_{batch_count}_{timestamp}.json"
        )
        
        try:
            with open(intermediate_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"💾 Intermediate results saved: {intermediate_file}")
        except Exception as e:
            print(f"❌ Failed to save intermediate results: {e}")

    def save_final_results(self):
        """Save final aggregated results as a clean list of flight quotes"""
        print("💾 Saving final aggregated results...")
        clean_results = self.aggregate_flight_quotes()
        
        # Save the clean results to the main file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON (clean list format)
        clean_json_file = os.path.join(self.results_dir, f"flight_matrix_results_{timestamp}.json")
        with open(clean_json_file, 'w') as f:
            json.dump(clean_results, f, indent=2, default=str)
        
        # Also save to the main aggregated file
        with open(self.aggregated_file, 'w') as f:
            json.dump(clean_results, f, indent=2, default=str)
        
        # Save as CSV for easy analysis
        csv_file = os.path.join(self.results_dir, f"flight_matrix_results_{timestamp}.csv")
        self.save_quotes_to_csv(clean_results, csv_file)
        
        print(f"✅ Saved {len(clean_results)} clean flight quotes to:")
        print(f"   📄 {clean_json_file}")
        print(f"   📄 {self.aggregated_file}")
        print(f"   📊 {csv_file}")
        
        # Trigger final aggregation
        trigger_auto_aggregation("final_save")
        
        return clean_results

    def save_quotes_to_csv(self, quotes: List[Dict], filename: str):
        """Save flight quotes to CSV format"""
        if not quotes:
            print("⚠️  No quotes to save to CSV")
            return
        
        try:
            import csv
            
            # Define the field order based on the standard structure (extended)
            fieldnames = [
                "departure_airport", "destination_airport", "departure_city", "destination_city",
                "origin_city_region", "destination_city_region", "flight_date", "departure_time",
                "arrival_time", "total_flight_time", "airline_code", "cabin_bags", "checked_bags",
                "num_stops", "price", "currency", "num_adults", "num_children", "num_infants",
                "passenger_type", "scraping_datetime", "source", "screenshot_url", "booking_url"
            ]
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for quote in quotes:
                    # Ensure all fields are present
                    row = {field: quote.get(field, "") for field in fieldnames}
                    writer.writerow(row)
            
            print(f"💾 Saved {len(quotes)} quotes to CSV: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving CSV: {e}")

    def aggregate_flight_quotes(self) -> List[Dict]:
        """
        Aggregate all flight quotes into a clean list with standardized structure.
        
        Returns:
            List of flight quote dictionaries with the standard structure from flight_search.py
        """
        all_quotes = []
        
        # Read all worker result files
        for filename in os.listdir(self.results_dir):
            if filename.startswith("worker_") and filename.endswith(".json"):
                filepath = os.path.join(self.results_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        # Extract results from nested structure if needed
                        results = data.get("results", []) if isinstance(data, dict) else data
                        all_quotes.extend(results)
                except Exception as e:
                    print(f"⚠️  Error reading {filepath}: {e}")
        
        # Add current results from this session
        all_quotes.extend(self.all_results)
        
        # Clean and standardize each quote to match the flight_search.py structure
        cleaned_quotes = []
        for quote in all_quotes:
            if not quote or not isinstance(quote, dict):
                continue
                
            # Ensure each quote has the standard structure
            standardized_quote = self.standardize_flight_quote(quote)
            if standardized_quote:
                cleaned_quotes.append(standardized_quote)
        
        # Remove duplicates (based on a combination of key fields)
        unique_quotes = self.remove_duplicate_quotes(cleaned_quotes)
        
        print(f"📊 Aggregated Results Summary:")
        print(f"   • Total quotes collected: {len(all_quotes)}")
        print(f"   • After cleaning: {len(cleaned_quotes)}")
        print(f"   • After deduplication: {len(unique_quotes)}")
        
        return unique_quotes
    
    def standardize_flight_quote(self, quote: Dict) -> Dict:
        """
        Standardize a flight quote to match the exact structure from flight_search.py
        
        Args:
            quote: Raw quote dictionary
            
        Returns:
            Standardized quote dictionary or None if invalid
        """
        try:
            # The standard structure from flight_search.py lines 79-100 (extended)
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
                "scraping_datetime": quote.get("scraping_datetime", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "source": quote.get("source", "unknown"),
                "screenshot_url": quote.get("screenshot_url"),
                "booking_url": quote.get("booking_url", "")
            }
            
            # Only return if we have essential flight data
            if (standardized["departure_city"] and 
                standardized["destination_city"] and 
                standardized["source"]):
                return standardized
            else:
                return None
                
        except Exception as e:
            print(f"⚠️  Error standardizing quote: {e}")
            return None
    
    def remove_duplicate_quotes(self, quotes: List[Dict]) -> List[Dict]:
        """
        Remove duplicate quotes based on key identifying fields
        
        Args:
            quotes: List of quote dictionaries
            
        Returns:
            List with duplicates removed
        """
        seen = set()
        unique_quotes = []
        
        for quote in quotes:
            # Create a unique key based on essential flight details
            key = (
                quote.get("departure_city", ""),
                quote.get("destination_city", ""),
                quote.get("flight_date", ""),
                quote.get("departure_time", ""),
                quote.get("airline_code", ""),
                quote.get("price", 0),
                quote.get("source", "")
            )
            
            if key not in seen:
                seen.add(key)
                unique_quotes.append(quote)
        
        return unique_quotes

    def run_matrix_search(self, max_tasks_per_worker=50, resume=False):
        """
        Main entry point - uses ProcessPoolExecutor by default.
        
        Args:
            max_tasks_per_worker: Maximum number of tasks per worker process
            resume: Whether to resume from existing checkpoint
        """
        return self.run_matrix_search_parallel(max_tasks_per_worker, resume)

def create_test_example():
    """Create a test example with ProcessPoolExecutor"""
    print("🧪 Creating test flight matrix scraper example...")
    
    scraper = MatrixFlightScraper(max_workers=2)
    
    print("🔄 Running small test matrix (max 10 tasks per worker)...")
    flight_quotes = scraper.run_matrix_search(max_tasks_per_worker=10)
    
    print(f"✅ Test completed! Generated {len(flight_quotes)} flight quotes")
    
    # Show example of the clean structure
    if flight_quotes:
        print("\n📋 Example flight quote structure:")
        print("="*50)
        example_quote = flight_quotes[0]
        for key, value in example_quote.items():
            print(f"  {key}: {value}")
        print("="*50)
        
        # Show summary statistics
        providers = set(q.get("source", "unknown") for q in flight_quotes)
        routes = set((q.get("departure_city"), q.get("destination_city")) for q in flight_quotes)
        
        print(f"\n📊 Quick Statistics:")
        print(f"   • Total flight quotes: {len(flight_quotes)}")
        print(f"   • Unique routes: {len(routes)}")
        print(f"   • Providers: {', '.join(providers)}")
        
        # Show price range
        prices = [q.get("price", 0) for q in flight_quotes if q.get("price", 0) > 0]
        if prices:
            print(f"   • Price range: ${min(prices):.2f} - ${max(prices):.2f}")
    
    return flight_quotes


if __name__ == "__main__":
    # Production mode - full matrix search
    print("🚀 Starting FULL PRODUCTION flight matrix search...")
    scraper = MatrixFlightScraper(max_workers=4)
    scraper.run_matrix_search(max_tasks_per_worker=100) 