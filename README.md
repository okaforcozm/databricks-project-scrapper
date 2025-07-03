# Databricks Mobility Agent

A comprehensive mobility data collection and analysis platform that processes shipping routes, flight data, and transportation analytics across global networks with multiple data providers and automated screenshot capture.

## 🌍 Overview

This platform provides enterprise-grade data collection capabilities for:
- **Multi-Provider Shipping Analysis**: Searates and Freightos shipping rate computation
- **Flight Price Intelligence**: Kiwi and Booking.com flight data aggregation
- **Screenshot Automation**: Automated webpage capture with S3 cloud storage
- **Real-time API Services**: FastAPI application with Redis caching
- **Transportation Analytics**: Comprehensive mobility data analysis and visualization

## 🚀 Quick Start

```bash
# Install dependencies
pip install aiohttp playwright pydantic bson boto3 fastapi redis
playwright install chromium

# Start Redis (required for FastAPI)
redis-server

# Start FastAPI application
python app/main.py

# Test shipping matrix system (Searates)
python test_shipping_matrix.py

# Test flight checkpointing system  
python test_flight_checkpointing.py

# Run shipping matrix computation (parallel processing recommended)
python app/shipping_matrix_runner.py --parallel --city-percentage 0.1

# Run Freightos matrix computation
python app/freightos_matrix_runner.py --parallel --location-percentage 0.1

# Run flight matrix with checkpointing
python run_full_flight_matrix.py --resume
```

## 🏗️ Core Systems Architecture

### 🚢 Shipping Matrix Systems
**See: [SHIPPING_MATRIX_README.md](./SHIPPING_MATRIX_README.md)**

#### **Searates Matrix System** (`shipping_matrix_runner.py`)
- Computes shipping rates between **85 cities** worldwide using Searates API
- **14,280 combinations** (85 × 84 × 2 container types: ST20, ST40)
- **Parallel processing** with multiprocessing support (2-8x faster)
- **Automatic checkpointing** every 50 results with resume capability
- **Screenshot automation** with S3 upload for rate verification

#### **Freightos Matrix System** (`freightos_matrix_runner.py`)
- Alternative shipping provider using Freightos API
- **96 global locations** with comprehensive route coverage
- **Multiple container types**: container20, container40, container40hc, container45
- **Enhanced error handling** with circuit breaker patterns
- **Parallel processing** with intelligent work distribution

### ✈️ Flight Data Collection
**See: [FLIGHT_CHECKPOINTING_README.md](./FLIGHT_CHECKPOINTING_README.md)**

#### **Flight Search Providers** (`providers/`)
- **Kiwi Provider** (`kiwi_provider.py`, `kiwi_utils.py`): Flight search via Kiwi.com API
- **Booking.com Provider** (`booking_provider.py`, `booking_utils.py`): Flight search via Booking.com
- **Unified Search Interface** (`flight_search.py`): Aggregates results from multiple providers
- **Airlines Database** (`airlines.json`): 7,347 airline records for validation

#### **Matrix Flight Scraper** (`matrix_flight_scraper.py`)
- **10-minute checkpoint intervals** with automatic saves
- **Multi-worker parallel processing** with fault tolerance
- **Passenger configurations**: Single, couple, family combinations
- **Rate limiting** with provider-specific throttling
- **Circuit breaker patterns** for API reliability
- **Task combination tracking** for precise resume capability

### 🖼️ Screenshot Automation (`tasks.py`)
- **Playwright-based** browser automation with stealth mode
- **S3 cloud storage** integration for screenshot persistence
- **Concurrent limiting** with semaphore control (max 3 simultaneous)
- **Smart cookie handling** with provider-specific strategies
- **User agent rotation** for anti-detection
- **Error recovery** with graceful degradation

### 🚀 FastAPI Application (`main.py`)
- **Redis integration** for high-performance caching
- **RESTful endpoints** for city, airport, and flight data management
- **Background task processing** for async operations
- **Health monitoring** with Redis connectivity checks
- **Bulk data operations** for efficient city/airport management

## 📊 Data Processing Infrastructure

### **Utility Systems** (`utils/`)
- **`helpers.py`** (146KB): Core computation logic for shipping matrices with API handling
- **`model.py`**: Pydantic data models using `bson.ObjectId` for MongoDB compatibility
- **`checkpoint_manager.py`**: Shipping matrix checkpoint system with fault tolerance
- **`flight_checkpoint_manager.py`**: Flight-specific checkpointing with 10-minute intervals
- **`flight_data_aggregator.py`**: Centralized flight data aggregation and statistics
- **`progress_reporter.py`**: Real-time progress tracking and reporting
- **`city_point_dict.py`**: 85 city mappings for Searates API
- **`freightos_locations.py`**: 96 location mappings for Freightos API
- **`city_regional_mapping.py`**: Regional classification for 180+ cities

### **Advanced Features**
- **Fault-tolerant checkpointing**: Never lose progress on system crashes
- **Multi-provider aggregation**: Combine data from multiple APIs
- **Rate limiting intelligence**: Provider-specific throttling strategies
- **Exponential backoff**: Robust retry mechanisms with jitter
- **Circuit breaker patterns**: Automatic failure detection and recovery
- **Parallel processing**: Multi-core CPU utilization for maximum performance

## 🔧 Core Technologies

- **Python 3.8+** with asyncio for concurrent processing
- **FastAPI** for high-performance API endpoints with OpenAPI documentation
- **Redis** for caching and session management
- **Playwright** for browser automation and screenshot capture
- **Pydantic** for data validation and serialization
- **MongoDB BSON** for ObjectId handling and database compatibility
- **AWS S3** for cloud storage of screenshots and large datasets
- **Multiprocessing** for CPU-intensive parallel computation
- **React + TypeScript** for frontend dashboard interfaces

## 📊 Data Output & Analytics

### **Shipping Data Output**
- **Searates**: 14,280+ shipping combinations between global cities
- **Freightos**: 9,120+ combinations (96 × 95 locations)
- **Rate information**: Price, currency, shipping time, carrier details
- **Screenshots**: Automated capture of logistics explorer pages
- **Metadata**: Provider info, scraping timestamps, shipment IDs

### **Flight Data Output**
- **Multi-provider aggregation**: Kiwi.com + Booking.com results
- **Passenger configurations**: Single, couple, family with children/infants
- **Route coverage**: Global city pairs with comprehensive price statistics
- **Screenshot verification**: Automated booking page captures
- **Checkpointed progress**: Fault-tolerant data collection with resume capability

### **API Data Management**
- **City database**: Bulk insertion and management via FastAPI
- **Airport mappings**: City-to-airport code relationships
- **Flight tracking**: Real-time price monitoring with Redis caching
- **Health monitoring**: System status and connectivity checks

## 🚀 Performance & Scaling

### **Shipping Matrix Performance**
- **Searates Sequential**: 12-16 hours for full computation
- **Searates Parallel**: 2-6 hours (depending on CPU cores)
- **Freightos Sequential**: 8-12 hours for full computation  
- **Freightos Parallel**: 1-4 hours with intelligent batching
- **Rate limiting**: Configurable delays (1-7 seconds) between API calls
- **Memory efficient**: Streaming processing with incremental saves

### **Flight Processing Performance**
- **Checkpointing**: 10-minute intervals prevent data loss
- **Multi-worker**: Parallel processing across worker processes
- **Provider throttling**: Kiwi (20 RPM), Booking.com (15 RPM)
- **Resume capability**: Continue from any interruption point
- **Centralized aggregation**: Single source of truth maintenance
- **Screenshot efficiency**: 3 concurrent captures per worker

### **API Performance**
- **Redis caching**: Sub-millisecond data retrieval
- **Async processing**: Non-blocking background tasks
- **Bulk operations**: Efficient city/airport data management
- **Health monitoring**: Real-time system status tracking

## 🛠️ Development & Testing

### **Test Suite**
```bash
# Core functionality tests
python test_shipping_matrix.py          # Searates shipping system
python test_freightos_checkpoints/      # Freightos checkpoint system
python test_flight_checkpointing.py     # Flight checkpoint system
python test_parallel_shipping.py        # Performance comparison

# System component tests
python test_enhanced_system.py          # Overall system integration
python test_matrix_scraper.py          # Flight matrix scraper
python app/test.py                      # Internal test suite
```

### **Configuration & Environment**
```bash
# Required environment variables
AWS_ACCESS_KEY_ID=your_s3_key
AWS_SECRET_ACCESS_KEY=your_s3_secret  
AWS_REGION=eu-west-2
REDIS_URL=redis://localhost:6379
SEARATES_BEARER_TOKEN=your_searates_token
FREIGHTOS_API_KEY=your_freightos_key

# Custom checkpoint settings
export FLIGHT_CHECKPOINT_INTERVAL="5"  # minutes
export FLIGHT_AUTO_RESUME="true"
export SHIPPING_CHECKPOINT_DIR="custom_checkpoints"
```

## 📈 Usage Examples

### **Shipping Matrix Operations**
```bash
# Searates shipping matrix (recommended)
python app/shipping_matrix_runner.py --parallel --city-percentage 0.01

# Freightos shipping matrix  
python app/freightos_matrix_runner.py --parallel --location-percentage 0.1

# Resume interrupted computations
python app/shipping_matrix_runner.py --parallel --city-percentage 1.0
python app/freightos_matrix_runner.py --parallel --location-percentage 1.0
```

### **Flight Data Collection**
```bash
# Standard flight matrix with checkpointing
python run_full_flight_matrix.py

# Resume from checkpoint with custom workers
python run_full_flight_matrix.py --resume --max-workers 6

# Fresh start with custom configuration
python run_full_flight_matrix.py --fresh-start --tasks-per-worker 100
```

### **API Operations**
```bash
# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# Health check
curl http://localhost:8000/health

# Add cities via API
curl -X POST http://localhost:8000/cities \
  -H "Content-Type: application/json" \
  -d '[{"region":"Europe","country_code":"GB","country_name":"United Kingdom","city_name":"London"}]'
```

### **Screenshot System**
```bash
# Direct screenshot testing
python -c "
from app.tasks import scrape_and_screenshot
result = scrape_and_screenshot('https://example.com')
print(result)
"
```

## 🚨 Important Production Notes

1. **API Rate Limits**: All systems respect provider API limits with intelligent throttling
2. **AWS Costs**: S3 storage costs accumulate with screenshot captures (~$0.023/GB/month)
3. **Computational Time**: Full matrix processing takes 2-16 hours depending on system
4. **Data Volume**: Expect 20K+ records for full shipping + flight matrices
5. **Resource Usage**: Monitor CPU/memory during parallel processing operations
6. **Redis Dependency**: FastAPI requires Redis for caching and session management
7. **Browser Dependencies**: Playwright requires Chromium for screenshot automation

## 🐛 Troubleshooting

### **Common Issues**
- **Import errors**: `pip install -r requirements.txt && playwright install chromium`
- **Redis connection**: Verify Redis server is running on localhost:6379
- **AWS permissions**: Check S3 bucket access and IAM policies
- **Browser automation**: Ensure Playwright Chromium installation is complete
- **Checkpoint corruption**: Use `--fresh-start` flags to restart computations

### **System Diagnostics**
```bash
# Check Redis connectivity
redis-cli ping

# Verify AWS S3 access
aws s3 ls s3://your-bucket-name

# Test screenshot system
python -c "from app.tasks import _go; import asyncio; print(asyncio.run(_go('https://google.com')))"

# Monitor checkpoint status
python check_checkpoint.py
python freightos_progress_check.py
```

## 📞 Getting Help

For detailed usage instructions and troubleshooting:
- **Shipping Systems**: [SHIPPING_MATRIX_README.md](./SHIPPING_MATRIX_README.md)
- **Flight Systems**: [FLIGHT_CHECKPOINTING_README.md](./FLIGHT_CHECKPOINTING_README.md)
- **API Documentation**: Visit `/docs` endpoint when FastAPI is running
- **Test Suites**: Run individual test files for component verification

## 🏗️ Project Structure

```
databricks-mobility-agent/
├── app/
│   ├── main.py                        # FastAPI application with Redis
│   ├── shipping_matrix_runner.py      # Searates shipping matrix CLI
│   ├── freightos_matrix_runner.py     # Freightos shipping matrix CLI  
│   ├── matrix_flight_scraper.py       # Flight matrix scraper (53KB)
│   ├── tasks.py                       # Screenshot automation system
│   ├── test.py                        # Internal test suite (26KB)
│   ├── providers/                     # Flight search providers
│   │   ├── flight_search.py          # Unified search interface
│   │   ├── kiwi_provider.py          # Kiwi.com integration
│   │   ├── booking_provider.py       # Booking.com integration  
│   │   ├── airlines.json             # 7,347 airline records
│   │   └── freightos_search.py       # Freightos search integration
│   └── utils/                         # Core utilities
│       ├── helpers.py                # Main computation logic (146KB)
│       ├── model.py                  # Pydantic models with bson.ObjectId
│       ├── checkpoint_manager.py     # Shipping checkpointing
│       ├── flight_checkpoint_manager.py  # Flight checkpointing
│       ├── flight_data_aggregator.py # Flight data aggregation
│       ├── progress_reporter.py      # Progress tracking
│       ├── city_point_dict.py        # 85 Searates cities
│       ├── freightos_locations.py    # 96 Freightos locations
│       └── city_regional_mapping.py  # Regional classifications
├── frontend/                          # React dashboard interfaces
├── flight_checkpoints/                # Flight checkpoint data  
├── freightos_checkpoints/             # Freightos checkpoint data
├── centralized_flight_data.json       # Aggregated flight results
├── shipping_matrix_*.json             # Searates results
├── freightos_matrix_*.json            # Freightos results
└── test_*.py                          # Test suite files
```

---

**Trust Level: High** 🫡 - Production-ready mobility intelligence platform with comprehensive multi-provider data collection, fault-tolerant processing, automated screenshot verification, and enterprise-grade API services. 