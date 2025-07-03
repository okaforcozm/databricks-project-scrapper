#!/usr/bin/env python3
"""
Checkpoint Status Checker

This utility checks the status of existing checkpoints and provides
information about resuming interrupted computations.
"""

import argparse
import json
import pickle
from pathlib import Path
from datetime import datetime
from app.utils.checkpoint_manager import CheckpointManager


def check_checkpoint_status(checkpoint_dir: str = "checkpoints"):
    """
    Check and display checkpoint status.
    
    Args:
        checkpoint_dir: Directory containing checkpoint files
    """
    print("🔍 CHECKPOINT STATUS CHECKER")
    print("=" * 50)
    
    checkpoint_path = Path(checkpoint_dir)
    
    if not checkpoint_path.exists():
        print(f"❌ Checkpoint directory '{checkpoint_dir}' does not exist")
        print("   No previous runs found.")
        return
    
    # Check for checkpoint files
    results_file = checkpoint_path / "results.json"
    progress_file = checkpoint_path / "progress.json"
    metadata_file = checkpoint_path / "metadata.json"
    completed_pairs_file = checkpoint_path / "completed_pairs.pkl"
    
    print(f"📁 Checkpoint directory: {checkpoint_path.absolute()}")
    print()
    
    # Check each file
    files_found = []
    
    if results_file.exists():
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
            files_found.append(f"✅ Results file: {len(results)} results")
        except Exception as e:
            files_found.append(f"❌ Results file: Error reading ({e})")
    else:
        files_found.append("❌ Results file: Not found")
    
    if progress_file.exists():
        try:
            with open(progress_file, 'r') as f:
                progress = json.load(f)
            files_found.append(f"✅ Progress file: {progress}")
        except Exception as e:
            files_found.append(f"❌ Progress file: Error reading ({e})")
    else:
        files_found.append("❌ Progress file: Not found")
    
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            files_found.append(f"✅ Metadata file: {metadata}")
        except Exception as e:
            files_found.append(f"❌ Metadata file: Error reading ({e})")
    else:
        files_found.append("❌ Metadata file: Not found")
    
    if completed_pairs_file.exists():
        try:
            with open(completed_pairs_file, 'rb') as f:
                completed_pairs = pickle.load(f)
            files_found.append(f"✅ Completed pairs: {len(completed_pairs)} pairs")
        except Exception as e:
            files_found.append(f"❌ Completed pairs: Error reading ({e})")
    else:
        files_found.append("❌ Completed pairs: Not found")
    
    # Display file status
    print("📋 Checkpoint Files:")
    for file_status in files_found:
        print(f"   {file_status}")
    print()
    
    # Check for backup files
    backup_files = list(checkpoint_path.glob("backup_*.csv"))
    if backup_files:
        print(f"💾 Backup Files: {len(backup_files)} found")
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for i, backup_file in enumerate(backup_files[:3]):  # Show latest 3
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            print(f"   {i+1}. {backup_file.name} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")
        if len(backup_files) > 3:
            print(f"   ... and {len(backup_files) - 3} more")
    else:
        print("💾 Backup Files: None found")
    print()
    
    # Provide resumption guidance
    if results_file.exists() and completed_pairs_file.exists():
        print("🚀 RESUMPTION GUIDANCE:")
        print("   ✅ Valid checkpoint found - you can resume processing")
        print("   📝 To resume:")
        print("      python app/shipping_matrix_runner.py --parallel --city-percentage 1.0")
        print("   📝 To start fresh (ignore checkpoint):")
        print("      python app/shipping_matrix_runner.py --parallel --city-percentage 1.0 --no-resume")
        print("   📝 To use different checkpoint directory:")
        print("      python app/shipping_matrix_runner.py --parallel --checkpoint-dir my_checkpoints")
    else:
        print("🆕 NO VALID CHECKPOINT:")
        print("   No resumable checkpoint found - will start fresh")
        print("   📝 To start new computation:")
        print("      python app/shipping_matrix_runner.py --parallel --city-percentage 1.0")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check checkpoint status for shipping matrix computation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--checkpoint-dir",
        default="checkpoints",
        help="Directory containing checkpoint files (default: checkpoints)"
    )
    
    args = parser.parse_args()
    
    check_checkpoint_status(args.checkpoint_dir)


if __name__ == "__main__":
    main() 