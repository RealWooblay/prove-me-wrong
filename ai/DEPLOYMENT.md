# Deploying Prove Me Wrong AI Services

This guide will help you deploy the AI services (generator and resolver) to Railway for public endpoints.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI**: Install the Railway CLI
   ```bash
   npm install -g @railway/cli
   ```
3. **ASI API Key**: Get an API key from [asi1.ai](https://asi1.ai)

## Quick Deployment

1. **Login to Railway**:
   ```bash
   railway login
   ```

2. **Set your ASI API key** (optional, can be done after deployment):
   ```bash
   export ASI_API_KEY=your_api_key_here
   ```

3. **Deploy**:
   ```bash
   cd ai
   ./deploy-railway.sh
   ```

## Manual Deployment

If you prefer to deploy manually:

1. **Navigate to the AI directory**:
   ```bash
   cd ai
   ```

2. **Initialize Railway project** (if not already done):
   ```bash
   railway init
   ```

3. **Deploy**:
   ```bash
   railway up
   ```

4. **Set environment variables**:
   ```bash
   railway variables set ASI_API_KEY=your_api_key_here
   ```

## Service Architecture

The deployment includes:

- **Generator Service** (`/generator/*`): Creates prediction markets
- **Resolver Service** (`/resolver/*`): Resolves market outcomes
- **Proxy Service** (`/`): Routes requests between services
- **PostgreSQL Database**: Persistent storage for markets and resolutions

## Available Endpoints

### Main API
- `GET /` - API information and available endpoints
- `GET /health` - Health check for all services

### Generator Service
- `POST /generator/generate` - Generate a new prediction market
- `GET /generator/markets` - List all markets
- `GET /generator/markets/active` - List active markets
- `GET /generator/markets/archived` - List archived markets
- `GET /generator/markets/{market_id}` - Get specific market
- `PUT /generator/markets/{market_id}/outcome` - Update market outcome
- `DELETE /generator/markets/{market_id}` - Delete market

### Resolver Service
- `POST /resolver/resolve` - Resolve a market outcome
- `POST /resolver/resolve-all` - Resolve all pending markets
- `GET /resolver/resolutions` - List all resolutions
- `GET /resolver/resolutions/active` - List active resolutions
- `GET /resolver/resolutions/archived` - List archived resolutions
- `GET /resolver/resolutions/{market_id}` - Get specific resolution
- `GET /resolver/resolutions/{market_id}/outcome` - Get market outcome

## Example Usage

### Generate a Market
```bash
curl -X POST "https://your-project.railway.app/generator/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Will Bitcoin reach $100,000 by the end of 2024?"
  }'
```

### Resolve a Market
```bash
curl -X POST "https://your-project.railway.app/resolver/resolve" \
  -H "Content-Type: application/json" \
  -d '{
    "market_id": "market_123"
  }'
```

### Get Market Outcome
```bash
curl "https://your-project.railway.app/resolver/resolutions/market_123/outcome"
```

## Environment Variables

- `ASI_API_KEY`: Your ASI-1 API key (required)
- `DATABASE_URL`: PostgreSQL connection string (automatically set by Railway)
- `PORT`: Port for the proxy service (set by Railway)

## Monitoring

- **View logs**: `railway logs`
- **Check status**: `railway status`
- **Redeploy**: `railway up`

## Troubleshooting

1. **Service not starting**: Check logs with `railway logs`
2. **API key issues**: Verify `ASI_API_KEY` is set correctly
3. **Database connection issues**: Check if `DATABASE_URL` is properly set
4. **Health check failures**: Ensure all services are running properly
5. **Data persistence**: Data is now stored in PostgreSQL and will survive container restarts

## Local Development

To run locally for testing:

```bash
cd ai
docker-compose up --build
```

This will start all services locally on:
- Generator: http://localhost:8000
- Resolver: http://localhost:8001
- Proxy: http://localhost:8000 (same port as generator in local setup) 