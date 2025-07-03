#!/usr/bin/env python3
"""
Progress Reporter for Shipping Matrix Computation

This module provides detailed progress analysis and time estimation
based on actual performance data from checkpoint files.
"""

import json
import pickle
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)


class ProgressReporter:
    """
    Comprehensive progress reporting with time estimation based on actual performance.
    """
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        self.target_combinations = 14280
        self.target_results_estimate = 20000  # Conservative estimate based on avg 1.4 results per combination
        
    def get_detailed_progress_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive progress report with time estimates.
        
        Returns:
            Dictionary containing detailed progress metrics and estimates
        """
        try:
            # Load checkpoint data
            checkpoint_data = self._load_checkpoint_data()
            if not checkpoint_data:
                return self._create_no_progress_report()
            
            # Calculate basic metrics
            basic_metrics = self._calculate_basic_metrics(checkpoint_data)
            
            # Calculate timing metrics
            timing_metrics = self._calculate_timing_metrics(checkpoint_data)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(checkpoint_data, timing_metrics)
            
            # Generate time estimates
            time_estimates = self._calculate_time_estimates(basic_metrics, timing_metrics, performance_metrics)
            
            # Analyze progress patterns
            progress_patterns = self._analyze_progress_patterns(checkpoint_data)
            
            # Create comprehensive report
            report = {
                "timestamp": datetime.now().isoformat(),
                "status": "IN_PROGRESS" if basic_metrics["progress_percent"] < 100 else "COMPLETE",
                "basic_metrics": basic_metrics,
                "timing_metrics": timing_metrics,
                "performance_metrics": performance_metrics,
                "time_estimates": time_estimates,
                "progress_patterns": progress_patterns,
                "recommendations": self._generate_recommendations(basic_metrics, performance_metrics)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating progress report: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def print_progress_report(self) -> None:
        """Print a formatted progress report to console."""
        report = self.get_detailed_progress_report()
        
        if "error" in report:
            print(f"❌ Error generating report: {report['error']}")
            return
            
        print("=" * 80)
        print("🚀 SHIPPING MATRIX PROGRESS REPORT")
        print("=" * 80)
        
        # Basic Status
        basic = report["basic_metrics"]
        print(f"📊 STATUS: {report['status']}")
        print(f"📅 Report Time: {report['timestamp']}")
        print(f"🎯 Progress: {basic['progress_percent']:.2f}% ({basic['completed_combinations']:,}/{basic['target_combinations']:,} combinations)")
        print(f"📄 Data Points: {basic['total_results']:,} results collected")
        print(f"📈 Efficiency: {basic['avg_results_per_combination']:.1f} results per combination")
        print()
        
        # Timing Information
        timing = report["timing_metrics"]
        print("⏱️  TIMING ANALYSIS:")
        print(f"   Started: {timing['start_time']}")
        print(f"   Running: {timing['elapsed_time']}")
        print(f"   Last Activity: {timing['last_checkpoint_time']}")
        print()
        
        # Performance Metrics
        perf = report["performance_metrics"]
        print("🚀 PERFORMANCE METRICS:")
        print(f"   Combinations/Hour: {perf['combinations_per_hour']:.1f}")
        print(f"   Results/Hour: {perf['results_per_hour']:.1f}")
        print(f"   Avg Time/Combination: {perf['avg_seconds_per_combination']:.1f} seconds")
        print(f"   Current Rate: {perf['recent_rate_description']}")
        print()
        
        # Time Estimates
        estimates = report["time_estimates"]
        if estimates.get("estimated_completion_time"):
            print("🔮 TIME ESTIMATES:")
            print(f"   Estimated Completion: {estimates['estimated_completion_time']}")
            print(f"   Time Remaining: {estimates['time_remaining']}")
            print(f"   Confidence: {estimates['confidence_level']}")
            print(f"   Based on: {estimates['estimation_method']}")
            print()
        
        # Progress Patterns
        patterns = report["progress_patterns"]
        print("📈 PROGRESS PATTERNS:")
        print(f"   Checkpoints Created: {patterns['total_checkpoints']}")
        print(f"   Avg Checkpoint Interval: {patterns['avg_checkpoint_interval']:.1f} results")
        print(f"   Data Growth Rate: {patterns['data_growth_pattern']}")
        print()
        
        # Recommendations
        recommendations = report["recommendations"]
        if recommendations:
            print("💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
            print()
        
        print("=" * 80)
    
    def _load_checkpoint_data(self) -> Optional[Dict[str, Any]]:
        """Load all available checkpoint data."""
        checkpoint_dir = Path(self.checkpoint_dir)
        if not checkpoint_dir.exists():
            return None
            
        data = {}
        
        # Load metadata
        metadata_file = checkpoint_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                data["metadata"] = json.load(f)
        
        # Load progress
        progress_file = checkpoint_dir / "progress.json"
        if progress_file.exists():
            with open(progress_file, 'r') as f:
                data["progress"] = json.load(f)
        
        # Load completed pairs
        completed_pairs_file = checkpoint_dir / "completed_pairs.pkl"
        if completed_pairs_file.exists():
            with open(completed_pairs_file, 'rb') as f:
                data["completed_pairs"] = pickle.load(f)
        
        # Load results
        results_file = checkpoint_dir / "results.json"
        if results_file.exists():
            with open(results_file, 'r') as f:
                data["results"] = json.load(f)
        
        # Get backup file timestamps
        backup_files = list(checkpoint_dir.glob("backup_*.csv"))
        if backup_files:
            backup_times = []
            for backup_file in sorted(backup_files):
                # Extract timestamp from filename: backup_20250628_170119.csv
                filename = backup_file.name
                try:
                    timestamp_str = filename.split('_')[1] + '_' + filename.split('_')[2].split('.')[0]
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    backup_times.append(timestamp)
                except:
                    pass
            data["backup_timestamps"] = backup_times
        
        return data if data else None
    
    def _calculate_basic_metrics(self, checkpoint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate basic progress metrics."""
        metadata = checkpoint_data.get("metadata", {})
        progress = checkpoint_data.get("progress", {})
        completed_pairs = checkpoint_data.get("completed_pairs", set())
        
        total_results = metadata.get("total_results") or progress.get("total_results", 0)
        completed_combinations = len(completed_pairs) if isinstance(completed_pairs, set) else metadata.get("completed_pairs", 0)
        
        progress_percent = (completed_combinations / self.target_combinations) * 100
        avg_results_per_combination = total_results / max(completed_combinations, 1)
        
        return {
            "total_results": total_results,
            "completed_combinations": completed_combinations,
            "target_combinations": self.target_combinations,
            "remaining_combinations": self.target_combinations - completed_combinations,
            "progress_percent": progress_percent,
            "avg_results_per_combination": avg_results_per_combination
        }
    
    def _calculate_timing_metrics(self, checkpoint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate timing-related metrics."""
        metadata = checkpoint_data.get("metadata", {})
        backup_timestamps = checkpoint_data.get("backup_timestamps", [])
        
        # Get start and end times
        start_time = None
        last_checkpoint_time = None
        
        if backup_timestamps:
            start_time = min(backup_timestamps)
            last_checkpoint_time = max(backup_timestamps)
        
        # Calculate elapsed time
        elapsed_time = None
        if start_time and last_checkpoint_time:
            elapsed_time = last_checkpoint_time - start_time
        
        return {
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S") if start_time else "Unknown",
            "last_checkpoint_time": last_checkpoint_time.strftime("%Y-%m-%d %H:%M:%S") if last_checkpoint_time else "Unknown",
            "elapsed_time": str(elapsed_time) if elapsed_time else "Unknown",
            "elapsed_seconds": elapsed_time.total_seconds() if elapsed_time else 0,
            "backup_timestamps": backup_timestamps
        }
    
    def _calculate_performance_metrics(self, checkpoint_data: Dict[str, Any], timing_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics."""
        basic_metrics = self._calculate_basic_metrics(checkpoint_data)
        elapsed_seconds = timing_metrics["elapsed_seconds"]
        
        if elapsed_seconds <= 0:
            return {
                "combinations_per_hour": 0,
                "results_per_hour": 0,
                "avg_seconds_per_combination": 0,
                "recent_rate_description": "No data available"
            }
        
        combinations_per_hour = (basic_metrics["completed_combinations"] / elapsed_seconds) * 3600
        results_per_hour = (basic_metrics["total_results"] / elapsed_seconds) * 3600
        avg_seconds_per_combination = elapsed_seconds / max(basic_metrics["completed_combinations"], 1)
        
        # Calculate recent rate
        recent_rate_desc = self._get_recent_rate_description(checkpoint_data, timing_metrics)
        
        return {
            "combinations_per_hour": combinations_per_hour,
            "results_per_hour": results_per_hour,
            "avg_seconds_per_combination": avg_seconds_per_combination,
            "recent_rate_description": recent_rate_desc
        }
    
    def _get_recent_rate_description(self, checkpoint_data: Dict[str, Any], timing_metrics: Dict[str, Any]) -> str:
        """Analyze recent performance to describe current rate."""
        backup_timestamps = timing_metrics.get("backup_timestamps", [])
        
        if len(backup_timestamps) < 2:
            return "Insufficient data for recent rate analysis"
        
        # Look at last few checkpoints to determine recent rate
        recent_timestamps = backup_timestamps[-3:] if len(backup_timestamps) >= 3 else backup_timestamps
        
        if len(recent_timestamps) >= 2:
            time_diff = (recent_timestamps[-1] - recent_timestamps[0]).total_seconds()
            if time_diff > 0:
                # Estimate results in recent period (assuming 100 results per checkpoint)
                checkpoint_interval = checkpoint_data.get("progress", {}).get("checkpoint_interval", 100)
                recent_results = len(recent_timestamps) * checkpoint_interval
                recent_rate = (recent_results / time_diff) * 3600  # per hour
                
                if recent_rate > 2000:
                    return "Very fast (excellent performance)"
                elif recent_rate > 1000:
                    return "Fast (good performance)"
                elif recent_rate > 500:
                    return "Moderate (acceptable performance)"
                else:
                    return "Slow (may need optimization)"
        
        return "Unable to determine recent rate"
    
    def _calculate_time_estimates(self, basic_metrics: Dict[str, Any], timing_metrics: Dict[str, Any], performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate time estimates based on current performance."""
        remaining_combinations = basic_metrics["remaining_combinations"]
        combinations_per_hour = performance_metrics["combinations_per_hour"]
        
        if combinations_per_hour <= 0 or remaining_combinations <= 0:
            return {
                "estimated_completion_time": None,
                "time_remaining": "Cannot estimate",
                "confidence_level": "No data",
                "estimation_method": "No performance data available"
            }
        
        # Calculate estimates
        hours_remaining = remaining_combinations / combinations_per_hour
        completion_time = datetime.now() + timedelta(hours=hours_remaining)
        
        # Determine confidence level
        elapsed_hours = timing_metrics["elapsed_seconds"] / 3600
        if elapsed_hours >= 2:
            confidence = "High (based on >2 hours of data)"
        elif elapsed_hours >= 1:
            confidence = "Medium (based on >1 hour of data)"
        else:
            confidence = "Low (limited data available)"
        
        # Format time remaining
        if hours_remaining < 1:
            time_remaining = f"{int(hours_remaining * 60)} minutes"
        elif hours_remaining < 24:
            time_remaining = f"{hours_remaining:.1f} hours"
        else:
            days = int(hours_remaining // 24)
            remaining_hours = hours_remaining % 24
            time_remaining = f"{days} days, {remaining_hours:.1f} hours"
        
        return {
            "estimated_completion_time": completion_time.strftime("%Y-%m-%d %H:%M:%S"),
            "time_remaining": time_remaining,
            "confidence_level": confidence,
            "estimation_method": f"Linear projection based on {combinations_per_hour:.1f} combinations/hour"
        }
    
    def _analyze_progress_patterns(self, checkpoint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in the progress data."""
        backup_timestamps = checkpoint_data.get("backup_timestamps", [])
        progress = checkpoint_data.get("progress", {})
        
        total_checkpoints = len(backup_timestamps)
        avg_checkpoint_interval = progress.get("checkpoint_interval", 100)
        
        # Analyze data growth pattern
        data_growth_pattern = "Steady growth"
        if total_checkpoints >= 3:
            # Calculate intervals between checkpoints
            intervals = []
            for i in range(1, len(backup_timestamps)):
                interval = (backup_timestamps[i] - backup_timestamps[i-1]).total_seconds()
                intervals.append(interval)
            
            if intervals:
                avg_interval = statistics.mean(intervals)
                recent_interval = intervals[-1] if intervals else avg_interval
                
                if recent_interval < avg_interval * 0.8:
                    data_growth_pattern = "Accelerating (getting faster)"
                elif recent_interval > avg_interval * 1.2:
                    data_growth_pattern = "Slowing down"
                else:
                    data_growth_pattern = "Steady growth"
        
        return {
            "total_checkpoints": total_checkpoints,
            "avg_checkpoint_interval": avg_checkpoint_interval,
            "data_growth_pattern": data_growth_pattern
        }
    
    def _generate_recommendations(self, basic_metrics: Dict[str, Any], performance_metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on current progress."""
        recommendations = []
        
        # Performance-based recommendations
        combinations_per_hour = performance_metrics["combinations_per_hour"]
        
        if combinations_per_hour < 100:
            recommendations.append("Performance is slow - consider reducing delay times or checking system resources")
        elif combinations_per_hour > 500:
            recommendations.append("Excellent performance! Current settings are optimal")
        
        # Progress-based recommendations
        progress_percent = basic_metrics["progress_percent"]
        
        if progress_percent > 50:
            recommendations.append("Over halfway complete! Consider enabling Excel backups for final results")
        elif progress_percent < 10:
            recommendations.append("Early stages - monitor performance for first few hours to optimize settings")
        
        # Data quality recommendations
        avg_results = basic_metrics["avg_results_per_combination"]
        if avg_results < 1.2:
            recommendations.append("Low results per combination - some routes may have limited options")
        elif avg_results > 2.0:
            recommendations.append("High results per combination - excellent data coverage")
        
        return recommendations
    
    def _create_no_progress_report(self) -> Dict[str, Any]:
        """Create a report when no progress data is available."""
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "NO_DATA",
            "message": "No checkpoint data found. Process may not have started or checkpoint directory is empty.",
            "basic_metrics": {
                "total_results": 0,
                "completed_combinations": 0,
                "target_combinations": self.target_combinations,
                "remaining_combinations": self.target_combinations,
                "progress_percent": 0.0,
                "avg_results_per_combination": 0.0
            },
            "timing_metrics": {
                "start_time": "Unknown",
                "last_checkpoint_time": "Unknown",
                "elapsed_time": "Unknown",
                "elapsed_seconds": 0,
                "backup_timestamps": []
            },
            "performance_metrics": {
                "combinations_per_hour": 0,
                "results_per_hour": 0,
                "avg_seconds_per_combination": 0,
                "recent_rate_description": "No data available"
            },
            "time_estimates": {
                "estimated_completion_time": None,
                "time_remaining": "Cannot estimate",
                "confidence_level": "No data",
                "estimation_method": "No performance data available"
            },
            "progress_patterns": {
                "total_checkpoints": 0,
                "avg_checkpoint_interval": 100,
                "data_growth_pattern": "No data available"
            },
            "recommendations": [
                "No checkpoint data found - make sure to start the shipping matrix runner first",
                "Run: python app/shipping_matrix_runner.py --parallel --realtime-checkpoint"
            ]
        }


def get_progress_report(checkpoint_dir: str = "checkpoints") -> Dict[str, Any]:
    """
    Convenience function to get a progress report.
    
    Args:
        checkpoint_dir: Directory containing checkpoint files
        
    Returns:
        Detailed progress report dictionary
    """
    reporter = ProgressReporter(checkpoint_dir)
    return reporter.get_detailed_progress_report()


def print_progress_report(checkpoint_dir: str = "checkpoints") -> None:
    """
    Convenience function to print a formatted progress report.
    
    Args:
        checkpoint_dir: Directory containing checkpoint files
    """
    reporter = ProgressReporter(checkpoint_dir)
    reporter.print_progress_report()


if __name__ == "__main__":
    # Example usage
    print_progress_report() 