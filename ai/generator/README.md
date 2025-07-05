# Market Generator Agent

An AI-powered prediction market generator that uses ASI-1 Mini to analyze market prompts, scrape web sources, validate market feasibility, and estimate probabilities.

## Features

- **Web Scraping**: Automatically searches and scrapes relevant web sources for market validation
- **ASI-1 Mini Integration**: Uses ASI-1 Mini for intelligent analysis and probability estimation
- **Market Validation**: Validates market feasibility based on multiple criteria
- **Probability Estimation**: Provides YES/NO probability estimates based on scraped data
- **Docker Support**: Containerized for easy deployment

## Prerequisites

1. **ASI-1 Mini API Key**: Get your API key from [ASI-1 Mini](https://superintelligence.io/products/asi1-mini/)
2. **Docker**: For containerized deployment
3. **Python 3.11+**: For local development

## Quick Start

### 1. Set Environment Variables

```bash
export ASI_API_KEY="your_asi_api_key_here"
```

### 2. Build and Run with Docker

```bash
# Build the image
docker build -t market-generator .

# Run the container
docker run -p 8000:8000 -e ASI_API_KEY=$ASI_API_KEY market-generator
```

### 3. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Generate a market
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Tesla stock price will be above $250 on December 31, 2024",
    "max_search_results": 5
  }'
```

## API Endpoints

### POST /generate

Generate a prediction market based on a prompt.

**Request Body:**
```json
{
  "prompt": "string (required) - The market prompt to analyze",
  "tweet_url": "string (optional) - Additional context from a tweet",
  "max_search_results": "integer (optional) - Maximum search results to analyze (default: 5)"
}
```

**Response:**
```json
{
  "success": true,
  "market": {
    "title": "Will Tesla stock price will be above $250 on December 31, 2024?",
    "description": "Prediction market based on analysis of 3 sources...",
    "closeTimeISO": "2024-12-31T23:59:59",
    "outcomes": ["YES", "NO"],
    "initialProb": 0.65,
    "validation": {
      "is_valid": true,
      "confidence": 0.85,
      "reasoning": "Market is valid because...",
      "sources": ["source1", "source2"],
      "yes_probability": 0.65,
      "no_probability": 0.35
    },
    "sources_analyzed": ["source1", "source2"]
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "asi_api_configured": true,
  "model": "asi1-mini"
}
```

### GET /

API information endpoint.

## Market Validation Criteria

The agent validates markets based on the following criteria:

1. **Binary Outcome**: Is the outcome clearly defined as YES/NO?
2. **Resolution Date**: Is there a clear date when the outcome will be determined?
3. **Reliable Sources**: Are there credible sources to verify the outcome?
4. **Not Resolved**: Is the market not already resolved?
5. **Credible Data**: Is the probability estimate based on credible data?

## How It Works

1. **Web Search**: Uses ASI-1 Mini to search for relevant information about the market topic
2. **Content Scraping**: Scrapes content from the top search results
3. **Probability Analysis**: Uses ASI-1 Mini to analyze the scraped content and estimate probabilities
4. **Market Validation**: Validates the market based on multiple criteria
5. **Market Generation**: Creates the final market data if validation passes

## Configuration

### Environment Variables

- `ASI_API_KEY`: Your ASI-1 Mini API key (required)
- `PYTHONUNBUFFERED`: Set to "1" for unbuffered Python output

### Docker Configuration

The service is configured to run on port 8000 with the following resource limits:
- Memory: 512Mi
- CPU: 0.5 cores

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### Testing

```bash
# Run the test script
python test_generator.py
```

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
- No relevant sources found
- Market validation failed
- API rate limiting
- Network connectivity issues

## Blockchain Integration

The market generator now includes direct blockchain integration with the ProveMeWrong smart contract. Markets can be automatically deployed to the blockchain using an admin wallet.

### Blockchain Configuration

Set the following environment variables for blockchain integration:

```bash
# Ethereum RPC URL (e.g., Infura, Alchemy)
export RPC_URL="https://sepolia.infura.io/v3/YOUR-PROJECT-ID"

# Deployed ProveMeWrong contract address
export CONTRACT_ADDRESS="0x..."

# Admin wallet private key (without 0x prefix)
export ADMIN_PRIVATE_KEY="your_private_key_here"

# Chain ID (11155111 for Sepolia testnet)
export CHAIN_ID="11155111"
```

### Quick Blockchain Setup

Use the provided setup script:

```bash
./deploy_blockchain.sh
```

This will guide you through setting up the required environment variables.

### Blockchain Features

- **Automatic Deployment**: Markets are automatically deployed to the blockchain during generation
- **Health Monitoring**: The health endpoint shows blockchain connection status
- **Error Handling**: Graceful fallback if blockchain deployment fails
- **Deployment Status**: Response includes `blockchain_deployed` field indicating deployment success

### Enhanced API Response

The `/generate` endpoint now includes blockchain deployment status:

```json
{
  "success": true,
  "market": {
    "id": "market-id",
    "title": "Will Bitcoin reach $100,000 by end of 2025?",
    "blockchain_deployed": true,
    "validation": {
      "is_valid": true,
      "yes_probability": 0.65,
      "no_probability": 0.35
    }
  }
}
```

#### Enhanced Health Check

The health endpoint now includes blockchain status:

```json
{
  "status": "healthy",
  "asi_api_configured": true,
  "blockchain_configured": true,
  "blockchain_connected": true,
  "model": "asi1-mini",
  "stored_markets": 5
}
```

### Integration with Smart Contracts

The generated market data is automatically formatted for the ProveMeWrong contract:

- **Market ID**: Unique identifier for the market
- **Request Hash**: Hash of the market prompt for verification
- **Token Names**: YES/NO token names and symbols
- **Initial Prices**: Probability-based initial prices (normalized to sum to 100%)
- **Expiry**: Unix timestamp for market expiration
- **Pool Address**: Liquidity pool for the market

### Security Considerations

- **Private Key Security**: Store admin private keys securely
- **Gas Management**: Ensure admin wallet has sufficient funds for gas fees
- **Network Selection**: Use appropriate testnet/mainnet configuration
- **Access Control**: Limit access to deployment endpoints in production

## Security Considerations

- The container runs as a non-root user
- API keys are passed via environment variables
- Input validation is performed on all requests
- Content scraping has timeout limits
- Rate limiting should be implemented in production

## Troubleshooting

### Common Issues

1. **ASI API Key Not Configured**
   - Ensure the `ASI_API_KEY` environment variable is set
   - Check the health endpoint to verify configuration

2. **No Sources Found**
   - The market topic may be too specific or obscure
   - Try adjusting the `max_search_results` parameter
   - Check if the topic has recent news coverage

3. **Market Validation Fails**
   - Review the validation reasoning in the response
   - Ensure the market has a clear binary outcome
   - Check if there are reliable sources for verification

4. **Docker Build Issues**
   - Ensure you have sufficient disk space
   - Check your internet connection for dependency downloads
   - Verify Docker is running properly

## License

This project is part of the prove-me-wrong prediction market platform.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the ASI-1 Mini documentation
- Test with the provided test script 