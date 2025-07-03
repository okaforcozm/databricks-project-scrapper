#!/usr/bin/env python3
"""
Production script to run full flight matrix scraper with checkpointing.

ENHANCED WITH COMPREHENSIVE CHECKPOINTING:
- 10-minute interval saves for each worker process
- Task combination tracking and resume capability
- Centralized aggregation maintaining single source of truth
- Graceful shutdown with complete data preservation
- Auto-resume from existing checkpoints
"""

import os
import sys
import signal
import atexit
import argparse
from datetime import datetime
from app.matrix_flight_scraper import MatrixFlightScraper

# Global variable to track scraper instance
current_scraper = None

def main():
    """Main entry point with comprehensive checkpointing"""
    parser = argparse.ArgumentParser(description="Flight Matrix Scraper with Checkpointing")
    parser.add_argument("--max-workers", type=int, default=4, help="Number of worker processes")
    parser.add_argument("--tasks-per-worker", type=int, default=100, help="Tasks per worker")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--fresh-start", action="store_true", help="Clear checkpoints and start fresh")
    
    args = parser.parse_args()
    
    print("🚀 COMPREHENSIVE CHECKPOINTED FLIGHT MATRIX SCRAPER")
    print("="*70)
    print(f"💾 Checkpoint directory: flight_checkpoints")
    print(f"⏰ Checkpoint interval: 10 minutes per worker")
    print(f"🔄 Centralized aggregation: Continuous")
    print("="*70)
    
    # Create checkpointed scraper
    global current_scraper
    current_scraper = MatrixFlightScraper(
        max_workers=args.max_workers,
        enable_checkpointing=True,
        checkpoint_dir="flight_checkpoints"
    )
    
    # Handle fresh start
    if args.fresh_start and current_scraper.checkpoint_manager:
        print("🔄 Fresh start - clearing checkpoints...")
        current_scraper.checkpoint_manager.clear_checkpoints()
    
    # Start the matrix search
    print(f"\n🚀 Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        flight_quotes = current_scraper.run_matrix_search(
            max_tasks_per_worker=args.tasks_per_worker,
            resume=args.resume
        )
        print(f"✅ Completed! {len(flight_quotes)} quotes collected")
    except KeyboardInterrupt:
        print("🛑 Interrupted - checkpoints saved")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 