#!/usr/bin/env python3
"""
Flight Matrix Checkpoint Manager

Comprehensive checkpointing system for flight matrix scraping with:
- 10-minute interval saves for worker processes
- Task combination tracking and resume capability
- Centralized aggregation and single source of truth
- Graceful shutdown with data preservation
"""

import json
import csv
import os
import pickle
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


class FlightCheckpointManager:
    """
    Manages checkpointing and resume functionality for flight matrix computation.
    """
    
    def __init__(self, 
                 checkpoint_dir: str = "flight_checkpoints", 
                 checkpoint_interval_minutes: int = 10,
                 centralized_file: str = "centralized_flight_data.json"):
        """
        Initialize flight checkpoint manager.
        
        Args:
            checkpoint_dir: Directory to store checkpoint files
            checkpoint_interval_minutes: Save interval in minutes (default 10)
            centralized_file: Path to centralized aggregated data file
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_interval_minutes = checkpoint_interval_minutes
        self.centralized_file = centralized_file
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Checkpoint files
        self.completed_tasks_file = self.checkpoint_dir / "completed_tasks.pkl"
        self.progress_file = self.checkpoint_dir / "progress.json"
        self.metadata_file = self.checkpoint_dir / "metadata.json"
        self.worker_state_file = self.checkpoint_dir / "worker_states.json"
        
        # In-memory tracking
        self.completed_task_combinations: Set[str] = set()
        self.worker_states: Dict[int, Dict] = {}
        self.last_checkpoint_time = datetime.now()
        self.session_id = str(uuid.uuid4())
        
        logger.info(f"Flight checkpoint manager initialized: {self.checkpoint_dir}")
        logger.info(f"Checkpoint interval: {self.checkpoint_interval_minutes} minutes")
        logger.info(f"Session ID: {self.session_id}")
    
    def clear_checkpoints(self) -> None:
        """Clear all existing checkpoint files for a fresh start."""
        try:
            files_to_clear = [
                self.completed_tasks_file,
                self.progress_file,
                self.metadata_file,
                self.worker_state_file
            ]
            
            for file_path in files_to_clear:
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Cleared checkpoint file: {file_path}")
            
            # Clear worker checkpoint files
            for checkpoint_file in self.checkpoint_dir.glob("worker_*_checkpoint_*.json"):
                checkpoint_file.unlink()
                logger.info(f"Cleared worker checkpoint: {checkpoint_file}")
            
            # Clear in-memory data
            self.completed_task_combinations = set()
            self.worker_states = {}
            self.last_checkpoint_time = datetime.now()
            
            logger.info("✅ All checkpoint files cleared for fresh start")
            
        except Exception as e:
            logger.error(f"Error clearing checkpoint files: {e}")
    
    def create_task_signature(self, task: Dict) -> str:
        """Create a unique signature for a flight search task."""
        signature_parts = [
            task.get("origin_city", ""),
            task.get("destination_city", ""),
            task.get("departure_date", ""),
            task.get("passenger_config", {}).get("name", ""),
            str(task.get("passenger_config", {}).get("adults", 1)),
            str(task.get("passenger_config", {}).get("children", 0)),
            str(task.get("passenger_config", {}).get("infants", 0))
        ]
        return "|".join(signature_parts)
    
    def load_existing_checkpoint(self) -> Dict[str, Any]:
        """Load existing checkpoint data if available."""
        checkpoint_data = {
            'completed_task_combinations': set(),
            'worker_states': {},
            'metadata': {},
            'has_checkpoint': False,
            'resume_summary': {}
        }
        
        try:
            # Load completed task combinations
            if self.completed_tasks_file.exists():
                with open(self.completed_tasks_file, 'rb') as f:
                    checkpoint_data['completed_task_combinations'] = pickle.load(f)
                logger.info(f"Loaded {len(checkpoint_data['completed_task_combinations'])} completed task combinations")
            
            # Load worker states
            if self.worker_state_file.exists():
                with open(self.worker_state_file, 'r', encoding='utf-8') as f:
                    checkpoint_data['worker_states'] = json.load(f)
                logger.info(f"Loaded states for {len(checkpoint_data['worker_states'])} workers")
            
            # Load metadata
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    checkpoint_data['metadata'] = json.load(f)
                logger.info(f"Loaded checkpoint metadata from {checkpoint_data['metadata'].get('last_checkpoint', 'unknown time')}")
            
            # Check for worker checkpoint files
            worker_checkpoints = list(self.checkpoint_dir.glob("worker_*_checkpoint_*.json"))
            if worker_checkpoints:
                logger.info(f"Found {len(worker_checkpoints)} worker checkpoint files")
                checkpoint_data['has_checkpoint'] = True
            
            if checkpoint_data['completed_task_combinations'] or worker_checkpoints:
                checkpoint_data['has_checkpoint'] = True
                
                # Generate resume summary
                checkpoint_data['resume_summary'] = self._generate_resume_summary(
                    checkpoint_data['completed_task_combinations'],
                    worker_checkpoints
                )
                
                logger.info("✅ Existing checkpoint found and loaded successfully")
            else:
                logger.info("No existing checkpoint found, starting fresh")
                
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
            logger.info("Starting fresh due to checkpoint loading error")
        
        # Update internal state
        self.completed_task_combinations = checkpoint_data['completed_task_combinations']
        self.worker_states = checkpoint_data['worker_states']
        
        return checkpoint_data
    
    def _generate_resume_summary(self, completed_tasks: Set[str], worker_files: List[Path]) -> Dict[str, Any]:
        """Generate a summary for resume operations."""
        
        # Count results from worker files
        total_quotes = 0
        routes_covered = set()
        providers_used = set()
        
        for worker_file in worker_files:
            try:
                with open(worker_file, 'r') as f:
                    data = json.load(f)
                    results = data.get('results', [])
                    total_quotes += len(results)
                    
                    for result in results:
                        if isinstance(result, dict):
                            origin = result.get('departure_city', '')
                            dest = result.get('destination_city', '')
                            if origin and dest:
                                routes_covered.add(f"{origin}-{dest}")
                            
                            provider = result.get('source', '')
                            if provider:
                                providers_used.add(provider)
            except Exception as e:
                logger.warning(f"Error reading worker file {worker_file}: {e}")
        
        return {
            'completed_task_combinations': len(completed_tasks),
            'worker_checkpoint_files': len(worker_files),
            'total_quotes_found': total_quotes,
            'routes_covered': len(routes_covered),
            'providers_used': list(providers_used),
            'latest_checkpoint': max([f.stat().st_mtime for f in worker_files]) if worker_files else None
        }
    
    def is_task_completed(self, task: Dict) -> bool:
        """Check if a flight search task has already been completed."""
        task_signature = self.create_task_signature(task)
        return task_signature in self.completed_task_combinations
    
    def mark_task_completed(self, task: Dict) -> None:
        """Mark a task as completed."""
        task_signature = self.create_task_signature(task)
        self.completed_task_combinations.add(task_signature)
    
    def filter_uncompleted_tasks(self, all_tasks: List[Dict]) -> List[Dict]:
        """Filter out tasks that have already been completed."""
        uncompleted_tasks = []
        completed_count = 0
        
        for task in all_tasks:
            if self.is_task_completed(task):
                completed_count += 1
            else:
                uncompleted_tasks.append(task)
        
        logger.info(f"📊 Task filtering results:")
        logger.info(f"   • Total tasks: {len(all_tasks)}")
        logger.info(f"   • Already completed: {completed_count}")
        logger.info(f"   • Remaining to process: {len(uncompleted_tasks)}")
        
        return uncompleted_tasks
    
    def save_worker_checkpoint(self, 
                              worker_id: int, 
                              batch_results: List[Dict], 
                              completed_tasks: List[Dict],
                              batch_info: Dict) -> str:
        """Save checkpoint for a specific worker."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_file = self.checkpoint_dir / f"worker_{worker_id}_checkpoint_{timestamp}.json"
            
            # Mark tasks as completed
            for task in completed_tasks:
                self.mark_task_completed(task)
            
            # Update worker state
            self.worker_states[worker_id] = {
                'last_checkpoint': datetime.now().isoformat(),
                'total_results': len(batch_results),
                'completed_tasks_count': len(completed_tasks),
                'batch_info': batch_info,
                'checkpoint_file': str(checkpoint_file)
            }
            
            # Prepare checkpoint data
            checkpoint_data = {
                'worker_id': worker_id,
                'session_id': self.session_id,
                'timestamp': timestamp,
                'checkpoint_time': datetime.now().isoformat(),
                'batch_info': batch_info,
                'results': batch_results,
                'completed_tasks': [self.create_task_signature(task) for task in completed_tasks],
                'worker_stats': {
                    'total_results_this_session': len(batch_results),
                    'tasks_completed_this_batch': len(completed_tasks)
                }
            }
            
            # Save worker checkpoint
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, default=str)
            
            # Save master tracking files
            self._save_master_tracking()
            
            # Trigger centralized aggregation
            self._trigger_centralized_aggregation(f"worker_{worker_id}_checkpoint")
            
            logger.info(f"💾 Worker {worker_id} checkpoint saved: {checkpoint_file}")
            logger.info(f"   • Results in this batch: {len(batch_results)}")
            logger.info(f"   • Tasks completed: {len(completed_tasks)}")
            
            return str(checkpoint_file)
            
        except Exception as e:
            logger.error(f"Error saving worker {worker_id} checkpoint: {e}")
            return ""
    
    def _save_master_tracking(self) -> None:
        """Save master tracking files."""
        try:
            # Save completed task combinations
            with open(self.completed_tasks_file, 'wb') as f:
                pickle.dump(self.completed_task_combinations, f)
            
            # Save worker states
            with open(self.worker_state_file, 'w', encoding='utf-8') as f:
                json.dump(self.worker_states, f, indent=2, default=str)
            
            # Save progress metadata
            progress_data = {
                'session_id': self.session_id,
                'last_checkpoint': datetime.now().isoformat(),
                'completed_task_combinations': len(self.completed_task_combinations),
                'active_workers': len(self.worker_states),
                'checkpoint_interval_minutes': self.checkpoint_interval_minutes
            }
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2)
            
            # Save metadata
            metadata = {
                'session_id': self.session_id,
                'last_checkpoint': datetime.now().isoformat(),
                'completed_task_combinations': len(self.completed_task_combinations),
                'worker_states': len(self.worker_states),
                'checkpoint_version': '2.0',
                'system': 'flight_matrix_scraper'
            }
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error saving master tracking files: {e}")
    
    def _trigger_centralized_aggregation(self, trigger_source: str) -> None:
        """Trigger centralized aggregation of all flight data."""
        try:
            logger.info(f"🔄 Triggering centralized aggregation from: {trigger_source}")
            
            # Import here to avoid circular imports
            from app.utils.flight_data_aggregator import FlightDataAggregator
            
            # Create aggregator with flight_matrix_results directory
            aggregator = FlightDataAggregator(results_dir="flight_matrix_results")
            
            # Also aggregate from checkpoint directory
            self._aggregate_checkpoint_data_to_results()
            
            # Run aggregation
            centralized_file = aggregator.run_aggregation(force_refresh=False)
            
            logger.info(f"✅ Centralized aggregation completed: {centralized_file}")
            
        except Exception as e:
            logger.warning(f"Centralized aggregation failed: {e}")
    
    def _aggregate_checkpoint_data_to_results(self) -> None:
        """Copy checkpoint data to flight_matrix_results for aggregation."""
        try:
            results_dir = Path("flight_matrix_results")
            results_dir.mkdir(exist_ok=True)
            
            # Copy worker checkpoints to results directory
            for checkpoint_file in self.checkpoint_dir.glob("worker_*_checkpoint_*.json"):
                dest_file = results_dir / f"from_checkpoint_{checkpoint_file.name}"
                
                # Only copy if not already exists or if checkpoint is newer
                if not dest_file.exists() or checkpoint_file.stat().st_mtime > dest_file.stat().st_mtime:
                    import shutil
                    shutil.copy2(checkpoint_file, dest_file)
                    logger.debug(f"Copied checkpoint to results: {dest_file}")
                    
        except Exception as e:
            logger.warning(f"Error copying checkpoint data to results directory: {e}")
    
    def get_resume_summary(self) -> Dict[str, Any]:
        """Get comprehensive resume summary."""
        checkpoint_data = self.load_existing_checkpoint()
        
        if not checkpoint_data['has_checkpoint']:
            return {'can_resume': False, 'message': 'No checkpoint data found'}
        
        resume_summary = checkpoint_data['resume_summary']
        
        # Add time information
        worker_files = list(self.checkpoint_dir.glob("worker_*_checkpoint_*.json"))
        if worker_files:
            latest_time = max([f.stat().st_mtime for f in worker_files])
            latest_checkpoint = datetime.fromtimestamp(latest_time)
            time_since = datetime.now() - latest_checkpoint
            
            resume_summary.update({
                'latest_checkpoint_time': latest_checkpoint.isoformat(),
                'time_since_last_checkpoint': str(time_since),
                'can_resume': True
            })
        
        return resume_summary
    
    def save_final_checkpoint(self, final_results: List[Dict] = None) -> None:
        """Save final checkpoint with all collected data."""
        try:
            logger.info("💾 Saving final checkpoint...")
            
            # Save master tracking
            self._save_master_tracking()
            
            # Save final summary
            final_summary = {
                'session_id': self.session_id,
                'completion_time': datetime.now().isoformat(),
                'total_completed_tasks': len(self.completed_task_combinations),
                'total_workers': len(self.worker_states),
                'final_results_count': len(final_results) if final_results else 0,
                'status': 'completed'
            }
            
            final_file = self.checkpoint_dir / f"final_summary_{self.session_id}.json"
            with open(final_file, 'w', encoding='utf-8') as f:
                json.dump(final_summary, f, indent=2)
            
            # Trigger final aggregation
            self._trigger_centralized_aggregation("final_checkpoint")
            
            logger.info(f"✅ Final checkpoint saved: {final_file}")
            
        except Exception as e:
            logger.error(f"Error saving final checkpoint: {e}")
    
    def cleanup_old_checkpoints(self, keep_recent: int = 5) -> None:
        """Clean up old checkpoint files, keeping only recent ones."""
        try:
            worker_checkpoints = list(self.checkpoint_dir.glob("worker_*_checkpoint_*.json"))
            worker_checkpoints.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            if len(worker_checkpoints) > keep_recent:
                old_checkpoints = worker_checkpoints[keep_recent:]
                for old_file in old_checkpoints:
                    old_file.unlink()
                    logger.debug(f"Cleaned up old checkpoint: {old_file}")
                
                logger.info(f"🧹 Cleaned up {len(old_checkpoints)} old checkpoint files")
                
        except Exception as e:
            logger.warning(f"Error cleaning up old checkpoints: {e}") 