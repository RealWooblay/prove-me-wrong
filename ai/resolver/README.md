# Market Resolver Agent

An AI-powered prediction market resolver that automatically checks stored markets for outcomes using ASI-1 Mini. The resolver runs on a cron job to continuously monitor markets and resolve them when definitive evidence is found.

## Features

- **Automatic Resolution**: Runs every hour to check all active markets
- **ASI-1 Mini Integration**: Uses ASI-1 Mini for intelligent evidence analysis
- **Auto-Expiration**: Automatically expires markets that pass their close date
- **Evidence Search**: Searches for definitive evidence from reliable sources
- **Local Storage**: Stores resolutions locally without requiring a database
- **Smart Filtering**: Only resolves markets close to their resolution date or with high confidence

## Prerequisites

1. **ASI-1 Mini API Key**: Get your API key from [ASI-1 Mini](https://superintelligence.io/products/asi1-mini/)
2. **Market Generator**: The resolver requires the Market Generator Agent to be running
3. **Docker**: For containerized deployment
4. **Python 3.11+**: For local development

## Quick Start

### 1. Set Environment Variables

```bash
export ASI_API_KEY="your_asi_api_key_here"
export GENERATOR_API_URL="http://localhost:8000"
```

### 2. Build and Run with Docker Compose

```bash
# From the ai directory
docker-compose up --build
```

### 3. Or Run Individually

```bash
# Build the image
docker build -t market-resolver .

# Run the container
docker run -p 8001:8001 \
  -e ASI_API_KEY=$ASI_API_KEY \
  -e GENERATOR_API_URL=http://host.docker.internal:8000 \
  market-resolver
```

### 4. Test the API

```bash
# Health check
curl http://localhost:8001/health

# Resolve all markets
curl -X POST http://localhost:8001/resolve-all

# List resolutions
curl http://localhost:8001/resolutions
```

## API Endpoints

### POST /resolve

Resolve a specific market by ID.

**Request Body:**
```json
{
  "market_id": "string (required) - The market ID to resolve",
  "force_resolve": "boolean (optional) - Force re-resolution (default: false)"
}
```

**Response:**
```json
{
  "success": true,
  "resolution": {
    "market_id": "market_123",
    "outcome": "YES",
    "confidence": 0.85,
    "reasoning": "Definitive evidence found...",
    "evidence_sources": ["Reuters", "Bloomberg"],
    "resolved_at": "2024-01-15T10:30:00",
    "auto_expired": false
  }
}
```

### POST /resolve-all

Resolve all active markets (for cron job use).

**Response:**
```json
{
  "success": true,
  "processed": 5,
  "results": [
    {
      "market_id": "market_123",
      "outcome": "YES",
      "confidence": 0.85
    }
  ]
}
```

### GET /resolutions

List all resolved markets.

**Response:**
```json
{
  "total": 10,
  "resolutions": [
    {
      "market_id": "market_123",
      "outcome": "YES",
      "confidence": 0.85,
      "reasoning": "Evidence found...",
      "evidence_sources": ["Reuters"],
      "resolved_at": "2024-01-15T10:30:00",
      "auto_expired": false
    }
  ]
}
```

### GET /resolutions/{market_id}

Get resolution for a specific market.

### GET /health

Health check endpoint.

## How It Works

### 1. Market Retrieval
The resolver fetches all active markets from the generator API.

### 2. Auto-Expiration Check
Markets that have passed their close date are automatically expired:
- "Before X date" markets are marked as NO if the date passes
- Other markets are expired after 7 days past close date

### 3. Evidence Search
For non-expired markets, the resolver:
- Searches for evidence using ASI-1 Mini
- Focuses on reliable sources specified in the market validation
- Scrapes content from relevant sources

### 4. Outcome Analysis
ASI-1 Mini analyzes the evidence to determine:
- **YES**: Definitive evidence supports the outcome
- **NO**: Definitive evidence against the outcome
- **INSUFFICIENT_EVIDENCE**: Not enough evidence to resolve

### 5. Resolution Storage
Resolved outcomes are stored locally for future reference.

## Resolution Rules

1. **Definitive Evidence**: Only resolve when there's clear evidence from reliable sources
2. **Conservative Approach**: Require high confidence before resolving
3. **Auto-Expiration**: Automatically expire markets that pass their close date
4. **Source Validation**: Only trust sources specified in the market validation
5. **Conflict Handling**: If evidence is conflicting, mark as insufficient evidence

## Auto-Expiration Logic

- **"Before X date" markets**: Automatically resolve as NO if the date passes
- **Regular markets**: Expire after 7 days past close date if not resolved
- **High-profile markets**: May be resolved earlier if evidence is found

## Configuration

### Environment Variables

- `ASI_API_KEY`: Your ASI-1 Mini API key (required)
- `GENERATOR_API_URL`: URL of the generator API (default: http://localhost:8000)
- `PYTHONUNBUFFERED`: Set to "1" for unbuffered Python output

### Docker Configuration

The service is configured to run on port 8001 with the following resource limits:
- Memory: 512Mi
- CPU: 0.5 cores

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Testing

```bash
# Run the test script
python test_resolver.py
```

## Background Tasks

The resolver runs a background task that:
- Executes every hour automatically
- Checks all active markets for resolution
- Handles auto-expiration
- Stores results locally

## Integration with Smart Contracts

The resolver provides resolved outcomes that can be used to:
- Settle prediction markets on-chain
- Distribute winnings to participants
- Update market status in smart contracts

## Error Handling

The API returns structured error responses:

```json
{
  "success": false,
  "error": "Error description"
}
```

Common error scenarios:
- Missing ASI API key
- Generator API unavailable
- Market not found
- Insufficient evidence
- Network connectivity issues

## Monitoring

### Health Checks
- Automatic health checks every 30 seconds
- Monitors ASI API connectivity
- Tracks number of stored resolutions
- Verifies generator API connection

### Logging
- Comprehensive logging for debugging
- Tracks resolution attempts and outcomes
- Logs API errors and network issues
- Records auto-expiration events

## Security Considerations

- The container runs as a non-root user
- API keys are passed via environment variables
- Input validation is performed on all requests
- Content scraping has timeout limits
- Rate limiting should be implemented in production

## Troubleshooting

### Common Issues

1. **Generator API Connection Failed**
   - Ensure the generator is running
   - Check the GENERATOR_API_URL environment variable
   - Verify network connectivity between services

2. **No Markets Found**
   - Create markets using the generator first
   - Check that markets are being stored properly
   - Verify the generator's local storage

3. **Resolutions Not Being Created**
   - Check ASI API key configuration
   - Verify ASI API is accessible
   - Review logs for API errors

4. **Auto-Expiration Not Working**
   - Check system time and timezone
   - Verify close_time_iso format in markets
   - Review auto-expiration logic

## Performance

- Processes markets in batches
- Limits evidence sources to top 3 per market
- Uses async operations for web scraping
- Implements timeout limits for API calls
- Stores data locally for fast access

## License

This project is part of the prove-me-wrong prediction market platform.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the ASI-1 Mini documentation
- Test with the provided test script
- Check container logs for detailed error information 