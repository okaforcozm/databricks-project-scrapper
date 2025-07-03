#!/usr/bin/env python3
"""
Standalone Progress Checker for Shipping Matrix Computation

This script provides a quick command-line interface to check the progress
of the shipping matrix computation and display detailed metrics.

Usage:
    python check_progress.py
    python check_progress.py --json  # Output as JSON
    python check_progress.py --checkpoint-dir custom_dir
"""

import argparse
import json
import sys
from pathlib import Path

# Add the app directory to the Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "app"))

try:
    from utils.progress_reporter import ProgressReporter, print_progress_report, get_progress_report
except ImportError as e:
    print(f"❌ Error importing progress reporter: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)


def main():
    """Main CLI interface for progress checking."""
    parser = argparse.ArgumentParser(
        description="Check the progress of shipping matrix computation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python check_progress.py                    # Display formatted report
    python check_progress.py --json             # Output JSON data
    python check_progress.py --json --pretty    # Pretty JSON output
    python check_progress.py --summary          # Brief summary only
    python check_progress.py --watch            # Live monitoring mode
        """
    )
    
    parser.add_argument(
        "--checkpoint-dir",
        default="checkpoints",
        help="Directory containing checkpoint files (default: checkpoints)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output progress data as JSON instead of formatted report"
    )
    
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output (only with --json)"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show only a brief summary"
    )
    
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch progress in real-time (updates every 30 seconds)"
    )
    
    args = parser.parse_args()
    
    # Validate checkpoint directory
    if not Path(args.checkpoint_dir).exists():
        print(f"❌ Checkpoint directory '{args.checkpoint_dir}' does not exist.")
        print(f"💡 Make sure the shipping matrix runner has been started and created checkpoints.")
        sys.exit(1)
    
    if args.watch:
        watch_progress(args.checkpoint_dir)
    elif args.json:
        output_json_report(args.checkpoint_dir, args.pretty)
    elif args.summary:
        output_summary(args.checkpoint_dir)
    else:
        print_progress_report(args.checkpoint_dir)


def output_json_report(checkpoint_dir: str, pretty: bool = False):
    """Output progress report as JSON."""
    try:
        report = get_progress_report(checkpoint_dir)
        if pretty:
            print(json.dumps(report, indent=2, default=str))
        else:
            print(json.dumps(report, default=str))
    except Exception as e:
        error_report = {
            "error": str(e),
            "status": "ERROR",
            "checkpoint_dir": checkpoint_dir
        }
        print(json.dumps(error_report, indent=2 if pretty else None))
        sys.exit(1)


def output_summary(checkpoint_dir: str):
    """Output a brief summary of progress."""
    try:
        report = get_progress_report(checkpoint_dir)
        
        if "error" in report:
            print(f"❌ Error: {report['error']}")
            return
        
        basic = report.get("basic_metrics", {})
        performance = report.get("performance_metrics", {})
        estimates = report.get("time_estimates", {})
        
        print("=" * 50)
        print("📊 SHIPPING MATRIX - Quick Summary")
        print("=" * 50)
        print(f"Status: {report.get('status', 'Unknown')}")
        print(f"Progress: {basic.get('progress_percent', 0):.1f}% ({basic.get('completed_combinations', 0):,}/{basic.get('target_combinations', 14280):,})")
        print(f"Results: {basic.get('total_results', 0):,} data points")
        print(f"Speed: {performance.get('combinations_per_hour', 0):.1f} combinations/hour")
        
        if estimates.get('time_remaining') != "Cannot estimate":
            print(f"ETA: {estimates.get('time_remaining', 'Unknown')}")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        sys.exit(1)


def watch_progress(checkpoint_dir: str):
    """Watch progress in real-time with periodic updates."""
    import time
    import os
    
    print("🔍 Real-time Progress Monitoring")
    print("Press Ctrl+C to exit")
    print("=" * 80)
    
    try:
        while True:
            # Clear screen (works on most terminals)
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("🔄 Live Progress Monitoring - Updates every 30 seconds")
            print("Press Ctrl+C to exit")
            print("=" * 80)
            
            try:
                print_progress_report(checkpoint_dir)
            except Exception as e:
                print(f"❌ Error updating progress: {e}")
            
            print("=" * 80)
            print(f"🔄 Next update in 30 seconds... (or press Ctrl+C to exit)")
            
            # Wait 30 seconds
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n👋 Exiting progress monitor. Thanks for watching!")
        sys.exit(0)


if __name__ == "__main__":
    main() 