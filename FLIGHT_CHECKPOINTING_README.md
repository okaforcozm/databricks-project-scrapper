# Flight Matrix Checkpointing System

Comprehensive checkpointing system for flight matrix scraping with **10-minute interval saves**, **resume capability**, and **centralized aggregation**.

## 🚀 Features

- **🔄 10-Minute Checkpoint Intervals**: Each worker process saves progress every 10 minutes
- **📋 Task Combination Tracking**: Remembers which city/passenger combinations have been searched
- **⚡ Resume Capability**: Automatically resume from any checkpoint 
- **💾 Graceful Shutdown**: Ctrl+C saves all progress before exiting
- **🔄 Centralized Aggregation**: Maintains single source of truth in `centralized_flight_data.json`
- **🛡️ Fault Tolerance**: Never lose progress, even on system crashes
- **📊 Progress Tracking**: Detailed statistics and resume summaries

## 📁 File Structure

```
flight_checkpoints/               # Checkpoint directory
├── completed_tasks.pkl          # Tracks completed task combinations
├── progress.json               # Progress metadata
├── metadata.json              # Session information
├── worker_states.json         # Worker state tracking
├── worker_1_checkpoint_*.json # Worker checkpoint files
├── worker_2_checkpoint_*.json
└── final_summary_*.json       # Final completion summary

flight_matrix_results/            # Results directory (legacy + aggregation)
├── single_result_*.json        # Individual flight results
├── batch_*.json               # Batch results
└── from_checkpoint_*.json     # Copied checkpoint data

centralized_flight_data.json     # Single source of truth (auto-updated)
```

## 🚀 Usage

### Basic Commands

```bash
# Standard run with checkpointing (default)
python run_full_flight_matrix.py

# Resume from existing checkpoint
python run_full_flight_matrix.py --resume

# Start completely fresh (clear all checkpoints)
python run_full_flight_matrix.py --fresh-start

# Custom worker configuration
python run_full_flight_matrix.py --max-workers 8 --tasks-per-worker 50

# Check existing checkpoint status
python run_full_flight_matrix.py --check-only
```

### Advanced Usage

```bash
# Force auto-resume without prompts
python run_full_flight_matrix.py --resume --force-yes

# Run with specific configuration
python run_full_flight_matrix.py \
  --max-workers 6 \
  --tasks-per-worker 75 \
  --resume

# Start fresh with custom settings
python run_full_flight_matrix.py \
  --fresh-start \
  --max-workers 4 \
  --tasks-per-worker 100
```

## 📊 Checkpointing Details

### Task Combination Tracking

Each task is identified by a unique signature:
```
{origin_city}|{destination_city}|{departure_date}|{passenger_type}|{adults}|{children}|{infants}
```

Examples:
- `NYC|LAX|2025-06-25|Single|1|0|0`
- `LONDON|PARIS|2025-06-26|Couple|2|0|0`
- `TOKYO|NYC|2025-06-27|Couple+2|2|2|0`

### Checkpoint Intervals

- **Worker Checkpoints**: Every 10 minutes per worker process
- **Immediate Saves**: After each individual flight result
- **Centralized Aggregation**: Triggered after every checkpoint
- **Final Checkpoint**: On completion or graceful shutdown

### Resume Logic

1. System checks for existing checkpoints in `flight_checkpoints/`
2. Loads completed task combinations from `completed_tasks.pkl`
3. Filters out already-processed tasks from the full task list
4. Continues processing only remaining tasks
5. Maintains all existing progress and data

## 🔄 Centralized Aggregation

The system maintains a **single source of truth** at `centralized_flight_data.json`:

```json
{
  "aggregation_timestamp": "2025-06-23 05:10:57",
  "total_quotes": 17535,
  "data_sources": {
    "batch_progress": {"count": 119},
    "existing_centralized": {"count": 2}
  },
  "statistics": {
    "providers": {"kiwi": 9610, "booking.com": 7925},
    "unique_routes": 531,
    "passenger_types": {...},
    "regional_coverage": 35,
    "price_statistics": {...}
  },
  "flight_quotes": [...]
}
```

Auto-aggregation is triggered:
- After every worker checkpoint (10-minute intervals)
- On graceful shutdown
- During resume operations
- On final completion

## 🛡️ Error Handling & Recovery

### Graceful Shutdown (Ctrl+C)

```bash
🛑 Received SIGINT (Ctrl+C). Initiating graceful shutdown...
💾 Saving current progress...
🔄 Saving final checkpoint...
✅ Final checkpoint saved
📋 To resume this computation later:
   python run_full_flight_matrix.py --resume
   (Checkpoint data saved in: flight_checkpoints)
👋 Shutdown complete. Exiting...
```

### System Crash Recovery

If the system crashes:
1. Restart with `--resume` flag
2. System automatically detects checkpoints
3. Shows resume summary with progress details
4. Continues from last saved state
5. No data loss (all successful results preserved)

### Worker Process Failures

- Individual worker failures don't stop other workers
- Each worker saves independently every 10 minutes
- Failed workers can be restarted automatically
- Checkpoint data preserved across process boundaries

## 📋 Resume Information

When resuming, the system shows:

```bash
📋 RESUME INFORMATION:
   • Completed task combinations: 2,543
   • Worker checkpoint files: 15
   • Total quotes found: 12,847
   • Routes covered: 127
   • Latest checkpoint: 2025-06-23T14:35:22
   • Time since last checkpoint: 0:02:45
```

## 🧪 Testing

Test the checkpointing system:

```bash
# Run comprehensive checkpointing tests
python test_flight_checkpointing.py

# Test specific components
python -c "from app.utils.flight_checkpoint_manager import FlightCheckpointManager; print('✅ Import successful')"
```

## 📊 Monitoring Progress

### Real-time Monitoring

```bash
# Watch checkpoint files being created
watch -n 30 'ls -la flight_checkpoints/worker_*_checkpoint_*.json | tail -5'

# Monitor centralized data updates
watch -n 60 'wc -l centralized_flight_data.json'

# Check latest worker activity
ls -lt flight_checkpoints/worker_*_checkpoint_*.json | head -3
```

### Progress Statistics

```bash
# Count completed task combinations
python -c "
import pickle
with open('flight_checkpoints/completed_tasks.pkl', 'rb') as f:
    tasks = pickle.load(f)
print(f'Completed tasks: {len(tasks)}')
"

# Get centralized data stats
python -c "
import json
with open('centralized_flight_data.json', 'r') as f:
    data = json.load(f)
print(f'Total quotes: {data["total_quotes"]}')
print(f'Last updated: {data["aggregation_timestamp"]}')
"
```

## 🔧 Configuration

### Environment Variables

```bash
# Custom checkpoint directory
export FLIGHT_CHECKPOINT_DIR="/path/to/checkpoints"

# Custom checkpoint interval (minutes)
export FLIGHT_CHECKPOINT_INTERVAL="5"

# Force resume mode
export FLIGHT_AUTO_RESUME="true"
```

### Code Configuration

Modify checkpoint behavior in `app/utils/flight_checkpoint_manager.py`:

```python
# Change checkpoint interval
checkpoint_interval_minutes=5  # Default: 10

# Change checkpoint directory
checkpoint_dir="custom_checkpoints"  # Default: "flight_checkpoints"

# Modify task signature (add more fields for uniqueness)
def create_task_signature(self, task: Dict) -> str:
    # Add custom fields here
    pass
```

## 🚨 Troubleshooting

### Common Issues

**Checkpoint directory not found:**
```bash
mkdir -p flight_checkpoints
chmod 755 flight_checkpoints
```

**Permission errors:**
```bash
sudo chown -R $USER:$USER flight_checkpoints/
chmod -R 644 flight_checkpoints/*.json
chmod -R 644 flight_checkpoints/*.pkl
```

**Corrupted checkpoint files:**
```bash
# Start fresh (backup first)
cp -r flight_checkpoints flight_checkpoints_backup
python run_full_flight_matrix.py --fresh-start
```

**Memory issues:**
```bash
# Reduce workers and tasks per worker
python run_full_flight_matrix.py --max-workers 2 --tasks-per-worker 25
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Recovery Commands

```bash
# Manual aggregation if auto-aggregation fails
python aggregate_flight_data.py --force-refresh

# Check checkpoint integrity
python -c "
import json, os
for f in os.listdir('flight_checkpoints/'):
    if f.endswith('.json'):
        try:
            with open(f'flight_checkpoints/{f}', 'r') as file:
                json.load(file)
            print(f'✅ {f}')
        except:
            print(f'❌ {f}')
"
```

## 🎯 Best Practices

1. **Always use `--resume`** when restarting interrupted computations
2. **Monitor disk space** - checkpoints can accumulate over time
3. **Regular backups** of `flight_checkpoints/` directory
4. **Use `--fresh-start`** only when you want to completely restart
5. **Keep checkpoint directory** until computation is 100% complete
6. **Monitor worker processes** for memory usage
7. **Use appropriate worker counts** based on system resources

## 📞 Support

For issues with the checkpointing system:

1. **Check logs** in terminal output
2. **Verify checkpoint files** exist and are not corrupted
3. **Run test suite**: `python test_flight_checkpointing.py`
4. **Use debug mode** with verbose logging
5. **Check file permissions** on checkpoint directory

---

**Trust Level: High** 🫡 - This checkpointing system is designed for robust, production-ready flight matrix computation with comprehensive fault tolerance and data preservation. 