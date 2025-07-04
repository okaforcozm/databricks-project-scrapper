#!/usr/bin/env python3
"""
Checkpoint Manager for Shipping Matrix Computation

This module provides robust checkpointing and resume functionality to ensure
fault tolerance and data persistence during long-running computations.
"""

import json
import csv
import os
import pickle
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class CheckpointManager:
    """
    Manages checkpointing and resume functionality for shipping matrix computation.
    """
    
    def __init__(self, checkpoint_dir: str = "checkpoints", checkpoint_interval: int = 50, excel_backup: bool = False):
        """
        Initialize checkpoint manager.
        
        Args:
            checkpoint_dir: Directory to store checkpoint files
            checkpoint_interval: Number of results to process before checkpointing
            excel_backup: Whether to save Excel backups alongside CSV
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_interval = checkpoint_interval
        self.excel_backup = excel_backup
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Checkpoint files
        self.results_file = self.checkpoint_dir / "results.json"
        self.progress_file = self.checkpoint_dir / "progress.json"
        self.completed_pairs_file = self.checkpoint_dir / "completed_pairs.pkl"
        self.metadata_file = self.checkpoint_dir / "metadata.json"
        
        # In-memory tracking - now supports (city_from, city_to, container) tuples
        self.completed_pairs: Set[Tuple[str, str, str]] = set()
        self.total_results: List[Dict[str, Any]] = []
        self.last_checkpoint_count = 0
        
        # Progress tracking for 14,280 unique combinations (85 cities × 84 × 2 containers)
        self.target_combinations = 14280  # 85 cities × 84 × 2 containers = 14,280 combinations
        self.last_logged_combination_count = 0
        
        logger.info(f"Checkpoint manager initialized: {self.checkpoint_dir}")
        logger.info(f"Checkpoint interval: {self.checkpoint_interval} results")
        logger.info(f"🎯 Target: {self.target_combinations} unique city+container combinations")
    
    def clear_checkpoints(self) -> None:
        """Clear all existing checkpoint files for a fresh start."""
        try:
            files_to_clear = [
                self.results_file,
                self.progress_file,
                self.completed_pairs_file,
                self.metadata_file
            ]
            
            for file_path in files_to_clear:
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Cleared checkpoint file: {file_path}")
            
            # Clear in-memory data
            self.completed_pairs = set()
            self.total_results = []
            self.last_checkpoint_count = 0
            
            logger.info("✅ All checkpoint files cleared for fresh start")
            
        except Exception as e:
            logger.error(f"Error clearing checkpoint files: {e}")
    
    def load_existing_checkpoint(self) -> Dict[str, Any]:
        """
        Load existing checkpoint data if available.
        
        Returns:
            Dictionary with checkpoint data and 'has_checkpoint' flag
        """
        checkpoint_data = {
            'has_checkpoint': False,
            'results': [],
            'completed_pairs': set(),
            'metadata': {}
        }
        
        try:
            # Load results
            if self.results_file.exists():
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    checkpoint_data['results'] = json.load(f)
                    self.total_results = checkpoint_data['results']
                    logger.info(f"Loaded {len(self.total_results)} results from checkpoint")
            
            # Load completed pairs (with backward compatibility)
            if self.completed_pairs_file.exists():
                with open(self.completed_pairs_file, 'rb') as f:
                    loaded_pairs = pickle.load(f)
                    
                    # Handle backward compatibility: convert 2-tuples to 3-tuples
                    if loaded_pairs and isinstance(next(iter(loaded_pairs)), tuple):
                        first_pair = next(iter(loaded_pairs))
                        if len(first_pair) == 2:
                            # Old format: (city_from, city_to) - need to migrate
                            logger.warning("🔄 Detected old checkpoint format (city pairs without container)")
                            logger.warning("🔄 Converting to new format with container types...")
                            
                            # Clear old data and start fresh with new format
                            self.completed_pairs = set()
                            self.total_results = []
                            logger.info("🆕 Starting fresh due to format change (city+container combinations)")
                            return checkpoint_data
                        elif len(first_pair) == 3:
                            # New format: (city_from, city_to, container)
                            self.completed_pairs = loaded_pairs
                            logger.info(f"Loaded {len(self.completed_pairs)} completed pairs")
                        else:
                            logger.warning(f"Unexpected pair format with {len(first_pair)} elements")
                            self.completed_pairs = set()
                    else:
                        self.completed_pairs = loaded_pairs if loaded_pairs else set()
                        logger.info(f"Loaded {len(self.completed_pairs)} completed pairs")
            
            # Load metadata
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    checkpoint_data['metadata'] = json.load(f)
                    logger.info(f"Loaded checkpoint metadata: {checkpoint_data['metadata']}")
            
            checkpoint_data['has_checkpoint'] = len(self.total_results) > 0 or len(self.completed_pairs) > 0
            checkpoint_data['completed_pairs'] = self.completed_pairs
            
            if checkpoint_data['has_checkpoint']:
                logger.info("✅ Existing checkpoint found and loaded successfully")
            else:
                logger.info("ℹ️  No existing checkpoint found")
        
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
            logger.info("🆕 Starting fresh due to checkpoint loading error")
            checkpoint_data['has_checkpoint'] = False
        
        self.completed_pairs = checkpoint_data['completed_pairs']
        self.last_checkpoint_count = len(self.total_results)
        
        return checkpoint_data
    
    def is_pair_completed(self, origin_city: str, destination_city: str, container: str) -> bool:
        """
        Check if a city pair with container has already been processed.
        
        Args:
            origin_city: Origin city name
            destination_city: Destination city name
            container: Container type (e.g., "ST20", "ST40")
            
        Returns:
            True if combination has been completed, False otherwise
        """
        return (origin_city, destination_city, container) in self.completed_pairs
    
    def add_result(self, result: Dict[str, Any]) -> None:
        """
        Add a result and mark the city+container combination as completed.
        
        Args:
            result: Result dictionary containing shipping data
        """
        self.total_results.append(result)
        
        # Mark combination as completed and track progress
        origin = result.get('city_of_origin')
        destination = result.get('city_of_destination')
        container = result.get('container_type')
        
        if origin and destination and container:
            combination = (origin, destination, container)
            if combination not in self.completed_pairs:
                # New unique combination completed!
                self.completed_pairs.add(combination)
                self._log_combination_progress()
        
        # Check if we need to checkpoint
        if len(self.total_results) - self.last_checkpoint_count >= self.checkpoint_interval:
            self.save_checkpoint()
    
    def _log_combination_progress(self) -> None:
        """Log progress toward completing all 14,280 unique combinations."""
        completed_count = len(self.completed_pairs)
        remaining_count = self.target_combinations - completed_count
        progress_percent = (completed_count / self.target_combinations) * 100
        
        # Log milestone progress (every 50 combinations or significant milestones)
        should_log = (
            completed_count % 50 == 0 or  # Every 50 combinations
            completed_count in [1, 10, 25, 100, 500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000] or  # Milestones
            remaining_count <= 100 or  # Final countdown
            remaining_count <= 10  # Last 10!
        )
        
        if should_log or completed_count > self.last_logged_combination_count + 100:
            logger.info("="*60)
            logger.info(f"📊 COMBINATION PROGRESS UPDATE")
            logger.info(f"   ✅ Unique combinations completed: {completed_count:,}/{self.target_combinations:,}")
            logger.info(f"   🎯 Progress: {progress_percent:.1f}%")
            logger.info(f"   📋 Remaining: {remaining_count:,} combinations")
            
            if remaining_count <= 50:
                logger.info(f"🔥 FINAL SPRINT: Only {remaining_count} combinations left!")
            elif remaining_count <= 200:
                logger.info(f"🚀 ALMOST THERE: Less than {remaining_count} combinations remaining!")
            
            logger.info("="*60)
            self.last_logged_combination_count = completed_count
    
    def add_batch_results(self, batch_results: List[Dict[str, Any]], batch_id: int) -> None:
        """
        Add results from a completed batch.
        
        Args:
            batch_results: List of results from a batch
            batch_id: ID of the completed batch
        """
        logger.info(f"Adding {len(batch_results)} results from batch {batch_id}")
        
        # Count unique combinations in this batch
        batch_combinations = set()
        for result in batch_results:
            origin = result.get('city_of_origin')
            destination = result.get('city_of_destination')
            container = result.get('container_type')
            if origin and destination and container:
                batch_combinations.add((origin, destination, container))
        
        # Add each result (this will trigger combination progress logging)
        for result in batch_results:
            self.add_result(result)
        
        logger.info(f"Batch {batch_id}: {len(batch_combinations)} unique combinations, {len(batch_results)} total data points")
        logger.info(f"Total results so far: {len(self.total_results)} data points from {len(self.completed_pairs)} unique combinations")
    
    def save_checkpoint(self, force: bool = False) -> None:
        """
        Save current progress to checkpoint files.
        
        Args:
            force: Force checkpoint even if interval not reached
        """
        try:
            if not force and len(self.total_results) - self.last_checkpoint_count < self.checkpoint_interval:
                return
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save results to JSON
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(self.total_results, f, indent=2, default=str)
            
            # Save completed pairs (now with container types)
            with open(self.completed_pairs_file, 'wb') as f:
                pickle.dump(self.completed_pairs, f)
            
            # Save progress metadata
            progress_data = {
                'total_results': len(self.total_results),
                'completed_pairs': len(self.completed_pairs),
                'last_checkpoint': timestamp,
                'checkpoint_interval': self.checkpoint_interval
            }
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2)
            
            # Save metadata
            metadata = {
                'last_checkpoint': timestamp,
                'total_results': len(self.total_results),
                'completed_pairs': len(self.completed_pairs),
                'checkpoint_version': '2.0',  # Updated version for container support
                'format': 'city_container_combinations'
            }
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            self.last_checkpoint_count = len(self.total_results)
            
            logger.info(f"💾 Checkpoint saved: {len(self.total_results)} results, {len(self.completed_pairs)} completed combinations")
            
            # Also save CSV backup
            self.save_csv_backup()
            
            # Save Excel backup if enabled
            if self.excel_backup:
                self.save_excel_backup()
            
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")
    
    def save_csv_backup(self) -> None:
        """Save current results to CSV backup file."""
        try:
            if not self.total_results:
                return
            
            csv_backup_file = f"checkpoints/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Import here to avoid circular imports
            from app.utils.helpers import save_results_to_csv
            
            # Save results using the same format as main export
            save_results_to_csv(self.total_results, csv_backup_file)
            
            logger.info(f"💾 CSV backup saved: {csv_backup_file}")
            
        except Exception as e:
            logger.error(f"Error saving CSV backup: {e}")
    
    def save_excel_backup(self) -> None:
        """Save current results to Excel backup file."""
        try:
            if not self.total_results:
                return
            
            # Import here to avoid circular imports
            from app.utils.helpers import save_results_to_excel
            
            excel_backup_file = f"checkpoints/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Save Excel with all enhanced features
            save_results_to_excel(self.total_results, excel_backup_file)
            
            logger.info(f"📊 Excel backup saved: {excel_backup_file}")
            
        except ImportError:
            logger.warning("📊 Excel backup skipped: openpyxl not available")
        except Exception as e:
            logger.error(f"Error saving Excel backup: {e}")
    
    def get_remaining_pairs(self, all_city_container_pairs: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
        """
        Get list of city+container combinations that haven't been processed yet.
        
        Args:
            all_city_container_pairs: Complete list of city+container combinations to process
            
        Returns:
            List of remaining city+container combinations to process
        """
        remaining = [combination for combination in all_city_container_pairs if combination not in self.completed_pairs]
        
        logger.info(f"Remaining combinations: {len(remaining)} out of {len(all_city_container_pairs)}")
        if len(all_city_container_pairs) > 0:
            logger.info(f"Completed combinations: {len(self.completed_pairs)} ({len(self.completed_pairs)/len(all_city_container_pairs)*100:.1f}%)")
        else:
            logger.info(f"Completed combinations: {len(self.completed_pairs)} (no combinations to process)")
        
        return remaining
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive progress summary.
        
        Returns:
            Dictionary with progress statistics
        """
        completed_combinations = len(self.completed_pairs)
        remaining_combinations = self.target_combinations - completed_combinations
        progress_percent = (completed_combinations / self.target_combinations) * 100 if self.target_combinations > 0 else 0
        
        return {
            'completed_combinations': completed_combinations,
            'remaining_combinations': remaining_combinations,
            'target_combinations': self.target_combinations,
            'progress_percent': progress_percent,
            'total_data_points': len(self.total_results),
            'avg_data_points_per_combination': len(self.total_results) / completed_combinations if completed_combinations > 0 else 0,
            'is_complete': completed_combinations >= self.target_combinations
        }
    
    def finalize_and_export(self, output_prefix: str = "shipping_matrix") -> Dict[str, str]:
        """
        Finalize computation and export results to final files.
        
        Args:
            output_prefix: Prefix for output files
            
        Returns:
            Dictionary containing paths to exported files
        """
        # Force final checkpoint
        self.save_checkpoint(force=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export to final files
        exported_files = {}
        
        try:
            # CSV export
            csv_filename = f"{output_prefix}_{timestamp}.csv"
            if self.total_results:
                # Collect all unique field names from all results
                all_fieldnames: Any = set()
                for result in self.total_results:
                    all_fieldnames.update(result.keys())
                fieldnames = sorted(all_fieldnames)  # Sort for consistent column order
                
                with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.total_results)
                exported_files['csv'] = csv_filename
                logger.info(f"📊 Final CSV exported: {csv_filename}")
            
            # JSON export
            json_filename = f"{output_prefix}_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(self.total_results, jsonfile, indent=2, default=str)
            exported_files['json'] = json_filename
            logger.info(f"📋 Final JSON exported: {json_filename}")
            
            # Summary report
            summary_filename = f"{output_prefix}_summary_{timestamp}.txt"
            with open(summary_filename, 'w', encoding='utf-8') as summary_file:
                summary_file.write(f"Shipping Matrix Computation Summary\n")
                summary_file.write(f"=" * 50 + "\n")
                summary_file.write(f"Completion time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                summary_file.write(f"Total results: {len(self.total_results)}\n")
                summary_file.write(f"Completed pairs: {len(self.completed_pairs)}\n")
                summary_file.write(f"Checkpoint interval: {self.checkpoint_interval}\n")
                summary_file.write(f"Files exported:\n")
                for file_type, filename in exported_files.items():
                    summary_file.write(f"  {file_type.upper()}: {filename}\n")
            
            exported_files['summary'] = summary_filename
            logger.info(f"📝 Summary report: {summary_filename}")
            
        except Exception as e:
            logger.error(f"Error during final export: {e}")
        
        return exported_files
    
    def cleanup_checkpoints(self, keep_backups: int = 3) -> None:
        """
        Clean up old checkpoint files, keeping only recent backups.
        
        Args:
            keep_backups: Number of backup files to keep
        """
        try:
            # Find all backup CSV files
            backup_files = list(self.checkpoint_dir.glob("backup_*.csv"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups
            for backup_file in backup_files[keep_backups:]:
                backup_file.unlink()
                logger.info(f"🗑️ Removed old backup: {backup_file}")
                
        except Exception as e:
            logger.error(f"Error cleaning up checkpoints: {e}") 