# Prove Me Wrong AI Services

A microservices architecture for generating and resolving prediction markets using AI.

## Services

- **Generator Service** (`/generator/*`): Creates prediction markets from prompts
- **Resolver Service** (`/resolver/*`): Resolves markets by gathering evidence and determining outcomes
- **Proxy Service**: Routes requests to appropriate services

## API Endpoints

### Health Checks
- `GET /health` - Overall system health
- `GET /generator/health` - Generator service health
- `GET /resolver/health` - Resolver service health

### Market Generation
- `POST /generator/generate` - Create a new prediction market
  ```json
  {
    "prompt": "Will Bitcoin reach $100,000 by the end of 2025?"
  }
  ```

### Market Listing
- `GET /generator/markets` - List all markets

### Market Resolution
- `POST /resolver/resolve` - Manually resolve a market
  ```json
  {
    "market_id": "market-uuid-here"
  }
  ```

### Resolution Listing
- `GET /resolver/resolutions` - List all resolutions

### Outcome Retrieval
- `GET /resolver/resolutions/{market_id}/outcome` - Get outcome for a specific market
  - Returns: `{"outcome": 0}` (False), `{"outcome": 1}` (True), or `{"outcome": 2}` (Insufficient Evidence)

## Environment Variables

- `ASI_API_KEY` - Anthropic API key for AI operations
- `DATABASE_URL` - Database connection string (SQLite or PostgreSQL)
- `GENERATOR_API_URL` - Internal URL for generator service (set by proxy)

## Deployment

### Local Development
```bash
# Start all services
./start.sh

# Or start individually
uvicorn generator.server:app --host 0.0.0.0 --port 8000
uvicorn resolver.server:app --host 0.0.0.0 --port 8001
uvicorn proxy:app --host 0.0.0.0 --port 8080
```

### Railway Deployment
```bash
# Deploy to Railway
./deploy-railway.sh

# Or manually
railway login
railway link
railway up
```

## Database

The system uses SQLAlchemy with support for both SQLite (local) and PostgreSQL (production). Tables are automatically created on startup.

## Background Tasks

The resolver service runs periodic background resolution tasks to automatically update market outcomes based on new evidence.

## Testing

Run the test suite:
```bash
python3 test_deployment.py
```

## Architecture

- **Generator**: Creates markets using AI validation
- **Resolver**: Scrapes news sources and uses AI to determine outcomes
- **Proxy**: Routes requests and handles timeouts
- **Database**: Persistent storage for markets and resolutions 