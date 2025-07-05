# Prove Me Wrong μAgent System

A decentralized μAgent architecture for market prediction and resolution using fetch.ai's uagents framework.

## 🏗️ Architecture

The system consists of **3 independent μAgents** that communicate with each other:

### 1. **Market Generator Agent** (Port 8000)
- **Purpose**: Analyzes market prompts and validates them
- **Functionality**: 
  - Preserves ALL existing `analyze_market_prompt()` logic
  - Validates market feasibility and calculates probabilities
  - Uses ASI API for market analysis
- **Endpoints**:
  - `POST /analyze-market` - Analyze market prompt
  - `GET /health` - Health check

### 2. **Market Resolver Agent** (Port 8001)
- **Purpose**: Scrapes web and determines market outcomes
- **Functionality**:
  - Preserves ALL existing `resolve_market()` logic
  - Web scraping for evidence collection
  - Outcome determination (YES/NO/INSUFFICIENT_EVIDENCE)
- **Endpoints**:
  - `POST /resolve-market` - Resolve market outcome
  - `GET /resolutions/{market_id}/outcome` - Get market outcome
  - `GET /health` - Health check

### 3. **Market Coordinator Agent** (Port 8002)
- **Purpose**: Manages database and coordinates between agents
- **Functionality**:
  - Database operations (create, read, update markets)
  - Blockchain deployment coordination
  - Inter-agent communication
- **Endpoints**:
  - `POST /create-market` - Create new market
  - `GET /markets` - List all markets
  - `GET /health` - Health check

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Virtual environment

### Installation

1. **Navigate to the agents directory:**
   ```bash
   cd ai/agents
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv uagents_env
   source uagents_env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install uagents fastapi sqlalchemy psycopg2-binary web3 eth-account beautifulsoup4 aiohttp requests schedule
   ```

4. **Start all agents:**
   ```bash
   python start_agents.py
   ```

### Testing the System

1. **Health Checks:**
   ```bash
   curl http://localhost:8000/health  # Generator Agent
   curl http://localhost:8001/health  # Resolver Agent
   curl http://localhost:8002/health  # Coordinator Agent
   ```

2. **Analyze Market:**
   ```bash
   curl -X POST "http://localhost:8000/analyze-market" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Will Bitcoin reach $100k by end of 2026?"}'
   ```

3. **Create Market:**
   ```bash
   curl -X POST "http://localhost:8002/create-market" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Will Ethereum reach $10k by end of 2026?"}'
   ```

4. **Resolve Market:**
   ```bash
   curl -X POST "http://localhost:8001/resolve-market" \
     -H "Content-Type: application/json" \
     -d '{
       "market_id": "your-market-id",
       "prompt": "Will Bitcoin reach $100k by end of 2026?",
       "reliable_sources": ["Reuters", "Bloomberg"]
     }'
   ```

## 🔧 Configuration

### Environment Variables

Set these environment variables for full functionality:

```bash
export RPC_URL="https://flare-testnet.public.blastapi.io"
export ADMIN_PRIVATE_KEY="your_private_key_here"
export PMW_ADDRESS="0xC0Ab40367C36c9Aa246F2F3063C564d4C08cf9C1"
export PMW_POOL_ADDRESS="0x4800757469dC1C8Fa5F981930DC641Be377467c2"
export CHAIN_ID="114"
export ASI_API_KEY="your_asi_api_key"
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
```

### Agent Configuration

Each agent has its own configuration in the respective files:
- `GENERATOR_AGENT_SEED` - Unique seed for agent identity
- `RESOLVER_AGENT_SEED` - Unique seed for agent identity  
- `COORDINATOR_AGENT_SEED` - Unique seed for agent identity

## 📊 Agent Communication

The agents communicate using uagents protocols:

1. **Market Creation Flow:**
   ```
   Client → Coordinator Agent → Generator Agent → Database → Blockchain
   ```

2. **Market Resolution Flow:**
   ```
   Client → Resolver Agent → Web Scraping → Database Update
   ```

3. **Inter-Agent Messages:**
   - `MarketAnalysisRequest` / `MarketAnalysisResponse`
   - `MarketResolutionRequest` / `MarketResolutionResponse`
   - `MarketCreationRequest` / `MarketCreationResponse`

## 🐳 Docker Deployment

Build and run with Docker:

```bash
cd ai/agents
docker build -t prove-me-wrong-agents .
docker run -p 8000:8000 -p 8001:8001 -p 8002:8002 prove-me-wrong-agents
```

## 🔍 Monitoring

### Logs
Each agent logs to stdout with structured logging:
- `🔍` - Request received
- `✅` - Success
- `❌` - Error
- `💾` - Database operation
- `🌐` - HTTP request

### Health Monitoring
All agents provide health endpoints that return:
- Agent status
- Agent address (uagents address)
- Service uptime

## 🛠️ Development

### Adding New Agents
1. Create new agent file following the pattern
2. Import `Agent, Context, Protocol` from uagents
3. Define message models with Pydantic
4. Create protocol class with message handlers
5. Add to `start_agents.py`

### Modifying Existing Logic
- **DO NOT** modify the core business logic functions
- **DO** wrap them in agent infrastructure
- **PRESERVE** all validation rules and API calls
- **MAINTAIN** identical JSON input/output structures

## 🔒 Security

- Agents use uagents' built-in security features
- Each agent has a unique cryptographic identity
- Communication is encrypted and authenticated
- Database connections use environment variables

## 📈 Scaling

The μAgent architecture allows for:
- **Horizontal scaling** - Run multiple instances of each agent
- **Load balancing** - Distribute requests across agent instances
- **Fault tolerance** - Agents can restart independently
- **Geographic distribution** - Deploy agents in different regions

## 🎯 Key Features

✅ **Preserves ALL existing logic** - No changes to core functions  
✅ **Identical API endpoints** - Same JSON structure as before  
✅ **Database integration** - Full SQLAlchemy support  
✅ **Blockchain deployment** - On-chain market creation  
✅ **Web scraping** - Evidence collection and resolution  
✅ **Health monitoring** - Agent status and uptime  
✅ **Error handling** - Graceful failure and recovery  
✅ **Logging** - Comprehensive structured logging  

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Port Conflicts**: Check if ports 8000, 8001, 8002 are available
3. **Database Errors**: Verify DATABASE_URL is set correctly
4. **Blockchain Errors**: Check RPC_URL and private key configuration

### Debug Mode
Run agents individually for debugging:
```bash
python market_generator_agent.py
python market_resolver_agent.py  
python market_coordinator_agent.py
```

## 📝 License

This project maintains the same license as the original Prove Me Wrong system. 