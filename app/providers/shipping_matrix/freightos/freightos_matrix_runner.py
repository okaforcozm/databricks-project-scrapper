#!/usr/bin/env python3
"""
Freightos matrix computation runner.

This script computes Freightos shipping rates for all location combinations
defined in the FREIGHTOS_LOCATIONS. It handles API rate limiting, error recovery,
and data export with parallel processing capabilities.

Usage:
    python app/freightos_matrix_runner.py --date 2025-06-18 --container container20 --delay-min 3 --delay-max 7
"""

import asyncio
import argparse
import sys
import logging
from datetime import datetime, timedelta

from app.utils.helpers import (
    compute_freightos_matrix, 
    compute_freightos_matrix_parallel, 
    save_results_to_csv, 
    save_results_to_json, 
    save_results_to_excel, 
    print_summary_stats
)
from app.utils.freightos_locations import FREIGHTOS_LOCATIONS


def setup_logging(log_level: str = "INFO"):
    """Configure logging with the specified level."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('freightos_matrix.log'),
            logging.StreamHandler()
        ]
    )


def validate_date(date_string: str) -> str:
    """Validate date format and ensure it's in the future."""
    try:
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
        if date_obj <= datetime.now():
            logging.warning(f"Date {date_string} is in the past. Using future date.")
            future_date = datetime.now() + timedelta(days=30)
            return future_date.strftime("%Y-%m-%d")
        return date_string
    except ValueError:
        raise ValueError(f"Invalid date format: {date_string}. Use YYYY-MM-DD format.")


def validate_container(container: str) -> str:
    """Validate container type."""
    valid_containers = ["container20", "container40", "container40hc", "container45"]
    if container not in valid_containers:
        logging.warning(f"Container {container} not in common types: {valid_containers}")
    return container


async def main():
    """Main entry point for the Freightos matrix computation."""
    parser = argparse.ArgumentParser(
        description="Compute Freightos shipping matrix for all location combinations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python app/freightos_matrix_runner.py
  python app/freightos_matrix_runner.py --date 2025-12-25 --container container40
  python app/freightos_matrix_runner.py --delay-min 5 --delay-max 10 --log-level DEBUG

Available locations ({len(FREIGHTOS_LOCATIONS)}):
{', '.join(sorted(FREIGHTOS_LOCATIONS.keys()))}

This will process {len(FREIGHTOS_LOCATIONS) * (len(FREIGHTOS_LOCATIONS) - 1)} location combinations.
        """
    )
    
    parser.add_argument(
        "--date",
        default="2025-09-01",
        help="Shipping date in YYYY-MM-DD format (default: 2025-09-01)"
    )
    
    parser.add_argument(
        "--container-types",
        nargs="+",
        default=["container20", "container40"],
        help="Container types to process (default: container20 container40)"
    )
    
    parser.add_argument(
        "--delay-min",
        type=float,
        default=1.0,
        help="Minimum delay between API requests in seconds (default: 1.0)"
    )
    
    parser.add_argument(
        "--delay-max",
        type=float,
        default=3.0,
        help="Maximum delay between API requests in seconds (default: 3.0)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without making actual requests"
    )
    
    parser.add_argument(
        "--resume-from",
        type=int,
        help="Resume processing from a specific combination number (1-based)"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit processing to first N combinations (useful for testing)"
    )
    
    parser.add_argument(
        "--output-prefix",
        default="freightos_matrix",
        help="Prefix for output files (default: freightos_matrix)"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Use parallel processing for faster computation"
    )
    
    parser.add_argument(
        "--processes",
        type=int,
        help="Number of processes to use for parallel processing (default: CPU count)"
    )
    
    parser.add_argument(
        "--location-percentage",
        type=float,
        default=0.1,
        help="Percentage of locations to process (default: 0.1 = 10%%)"
    )
    
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=50,
        help="Number of results to process before checkpointing (default: 50)"
    )
    
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Start fresh instead of resuming from checkpoint"
    )
    
    parser.add_argument(
        "--checkpoint-dir",
        default="freightos_checkpoints",
        help="Directory to store checkpoint files (default: freightos_checkpoints)"
    )
    
    parser.add_argument(
        "--excel",
        action="store_true",
        help="Export results to Excel format (.xlsx) with enhanced formatting"
    )
    
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Skip CSV export (useful when only Excel is needed)"
    )
    
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Skip JSON export (useful when only Excel is needed)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Validate inputs
        validated_date = validate_date(args.date)
        validated_container_types = [validate_container(c) for c in args.container_types]
        
        if args.delay_min > args.delay_max:
            raise ValueError("delay-min cannot be greater than delay-max")
        
        # Show configuration
        locations = list(FREIGHTOS_LOCATIONS.keys())
        total_combinations = len(locations) * (len(locations) - 1)
        
        logger.info("="*60)
        logger.info("FREIGHTOS MATRIX COMPUTATION STARTING")
        logger.info("="*60)
        logger.info(f"Date: {validated_date}")
        logger.info(f"Container types: {validated_container_types}")
        logger.info(f"Delay range: {args.delay_min}-{args.delay_max} seconds")
        logger.info(f"Total locations: {len(locations)}")
        logger.info(f"Total combinations: {total_combinations}")
        logger.info(f"Processing mode: {'PARALLEL' if args.parallel else 'SEQUENTIAL'}")
        
        if args.parallel:
            import multiprocessing as mp
            num_processes = args.processes or mp.cpu_count()
            logger.info(f"Using {num_processes} parallel processes")
            logger.info(f"Location percentage: {args.location_percentage * 100:.1f}%")
            logger.info(f"Checkpoint interval: {args.checkpoint_interval} results")
            logger.info(f"Resume mode: {'Disabled' if args.no_resume else 'Enabled'}")
            logger.info(f"Checkpoint directory: {args.checkpoint_dir}")
        
        if args.resume_from:
            logger.info(f"Resuming from combination: {args.resume_from}")
        
        if args.limit:
            logger.info(f"Processing limited to: {args.limit} combinations")
        
        if args.dry_run:
            logger.info("DRY RUN MODE - No actual requests will be made")
            logger.info("Location+container combinations that would be processed:")
            count = 0
            for i, origin in enumerate(locations):
                for j, destination in enumerate(locations):
                    if origin == destination:
                        continue
                    for container_type in validated_container_types:
                        count += 1
                        if args.resume_from and count < args.resume_from:
                            continue
                        if args.limit and count > args.limit:
                            break
                        logger.info(f"  {count}: {origin} -> {destination} ({container_type})")
                    if args.limit and count > args.limit:
                        break
                if args.limit and count > args.limit:
                    break
            return
        
        # Run the computation
        if args.parallel:
            results = await compute_freightos_matrix_parallel(
                date=validated_date,
                container_types=validated_container_types,
                delay_range=(args.delay_min, args.delay_max),
                num_processes=args.processes,
                location_percentage=args.location_percentage,
                checkpoint_interval=args.checkpoint_interval,
                resume=not args.no_resume,
                checkpoint_dir=args.checkpoint_dir
            )
        else:
            # For sequential processing, process each container type separately
            results = []
            for container_type in validated_container_types:
                container_results = await compute_freightos_matrix(
                    date=validated_date,
                    container=container_type,
                    delay_range=(args.delay_min, args.delay_max),
                    location_percentage=args.location_percentage
                )
                results.extend(container_results)
        
        # Print summary statistics
        print_summary_stats(results)
        
        # Save results to files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_files = []
        
        # CSV export (unless disabled)
        if not args.no_csv:
            csv_filename = f"{args.output_prefix}_{timestamp}.csv"
            save_results_to_csv(results, csv_filename)
            exported_files.append(f"CSV: {csv_filename}")
        
        # JSON export (unless disabled)
        if not args.no_json:
            json_filename = f"{args.output_prefix}_{timestamp}.json"
            save_results_to_json(results, json_filename)
            exported_files.append(f"JSON: {json_filename}")
        
        # Excel export (if requested)
        if args.excel:
            excel_filename = f"{args.output_prefix}_{timestamp}.xlsx"
            try:
                save_results_to_excel(results, excel_filename)
                exported_files.append(f"Excel: {excel_filename} (with enhanced formatting)")
            except ImportError:
                logger.error("❌ Excel export failed: openpyxl library not installed")
                logger.info("💡 To enable Excel export, run: pip install openpyxl")
            except Exception as e:
                logger.error(f"❌ Excel export failed: {e}")
        
        logger.info("="*60)
        logger.info("FREIGHTOS COMPUTATION COMPLETED SUCCESSFULLY")
        logger.info("="*60)
        logger.info(f"Results exported to:")
        for file_info in exported_files:
            logger.info(f"  📄 {file_info}")
        
        if args.excel and exported_files and any("Excel" in f for f in exported_files):
            logger.info("\n🎯 Excel Features:")
            logger.info("  • Professional styling with borders and colors")
            logger.info("  • Formatted numbers with thousand separators")
            logger.info("  • Frozen header row for easy scrolling")
        
        return results
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 