# Prove Me Wrong μAgent System - Deployment Guide

## 🎯 **Single Instance Deployment**

You only need **ONE Railway instance** for the entire μAgent system. The system includes:

- ✅ **Generator functions** (analyze_market_prompt)
- ✅ **Resolver functions** (resolve_market) 
- ✅ **Blockchain deployment** (deploy_market)
- ✅ **Database operations** (SQLAlchemy)
- ✅ **All 3 μAgents** running on different ports

## 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    Railway Container                        │
├─────────────────────────────────────────────────────────────┤
│  Port 8000: Market Generator Agent                          │
│  ├── Calls analyze_market_prompt() from generator/server.py │
│  └── HTTP: POST /analyze-market                             │
├─────────────────────────────────────────────────────────────┤
│  Port 8001: Market Resolver Agent                           │
│  ├── Calls resolve_market() from resolver/server.py         │
│  └── HTTP: POST /resolve-market                             │
├─────────────────────────────────────────────────────────────┤
│  Port 8002: Market Coordinator Agent                        │
│  ├── Calls deploy_market() from generator/server.py         │
│  ├── Database operations (SQLAlchemy)                       │
│  └── HTTP: POST /create-market                              │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Deployment Steps**

### 1. **Prepare for Deployment**

```bash
cd ai/
chmod +x deploy-uagents-railway.sh
```

### 2. **Deploy to Railway**

```bash
./deploy-uagents-railway.sh
```

This script will:
- ✅ Install Railway CLI if needed
- ✅ Login to Railway
- ✅ Link to your project
- ✅ Set environment variables
- ✅ Deploy using Dockerfile.uagents
- ✅ Test all endpoints

### 3. **Manual Deployment (Alternative)**

```bash
# Login to Railway
railway login

# Link to project
railway link

# Set environment variables
railway variables set RPC_URL="https://flare-testnet.public.blastapi.io"
railway variables set ADMIN_PRIVATE_KEY="your_private_key"
railway variables set PMW_ADDRESS="0xC0Ab40367C36c9Aa246F2F3063C564d4C08cf9C1"
railway variables set PMW_POOL_ADDRESS="0x4800757469dC1C8Fa5F981930DC641Be377467c2"
railway variables set CHAIN_ID="114"
railway variables set ASI_API_KEY="your_asi_api_key"
railway variables set DATABASE_URL="postgresql://postgres:password@localhost:5432/prove_me_wrong"

# Deploy
railway up
```

## 🌐 **Public Endpoints**

After deployment, you'll get public URLs like:
- `https://your-app.up.railway.app:8000` - Generator Agent
- `https://your-app.up.railway.app:8001` - Resolver Agent  
- `https://your-app.up.railway.app:8002` - Coordinator Agent

### **API Endpoints**

```bash
# Health Checks
curl https://your-app.up.railway.app:8000/health
curl https://your-app.up.railway.app:8001/health
curl https://your-app.up.railway.app:8002/health

# Market Analysis
curl -X POST "https://your-app.up.railway.app:8000/analyze-market" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Will Bitcoin reach $100k by end of 2026?"}'

# Market Creation
curl -X POST "https://your-app.up.railway.app:8002/create-market" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Will Ethereum reach $10k by end of 2026?"}'

# Market Resolution
curl -X POST "https://your-app.up.railway.app:8001/resolve-market" \
  -H "Content-Type: application/json" \
  -d '{
    "market_id": "test-market-123",
    "prompt": "Will Bitcoin reach $100k by end of 2026?",
    "reliable_sources": ["Reuters", "Bloomberg"]
  }'
```

## 🤝 **Agent Communication**

### **True μAgent Communication (Both Local and Railway)**
Agents communicate via uagents protocols:
- Coordinator Agent → Generator Agent (via uagents protocol)
- Coordinator Agent → Resolver Agent (via uagents protocol)
- Generator Agent → Coordinator Agent (via uagents protocol)
- Resolver Agent → Coordinator Agent (via uagents protocol)

### **HTTP Endpoints (For External Access)**
HTTP endpoints are available for external clients:
- `POST /analyze-market` - Direct access to generator
- `POST /resolve-market` - Direct access to resolver
- `POST /create-market` - Full workflow via coordinator

### **Inter-Agent Messages**

```python
# Market Analysis Request
{
  "prompt": "Will Bitcoin reach $100k?",
  "request_id": "uuid-123"
}

# Market Analysis Response  
{
  "request_id": "uuid-123",
  "validation": {
    "is_valid": true,
    "confidence": 0.85,
    "yes_probability": 0.65,
    "no_probability": 0.35
  },
  "success": true
}

# Market Resolution Request
{
  "market_id": "market-123",
  "prompt": "Will Bitcoin reach $100k?",
  "reliable_sources": ["Reuters", "Bloomberg"],
  "request_id": "uuid-456"
}

# Market Resolution Response
{
  "request_id": "uuid-456",
  "market_id": "market-123",
  "outcome": "YES",
  "confidence": 0.9,
  "evidence": ["Bitcoin reached $100k on Dec 15, 2026"],
  "success": true
}
```

## 🔧 **Environment Variables**

Required for full functionality:

```bash
RPC_URL="https://flare-testnet.public.blastapi.io"
ADMIN_PRIVATE_KEY="your_private_key_here"
PMW_ADDRESS="0xC0Ab40367C36c9Aa246F2F3063C564d4C08cf9C1"
PMW_POOL_ADDRESS="0x4800757469dC1C8Fa5F981930DC641Be377467c2"
CHAIN_ID="114"
ASI_API_KEY="your_asi_api_key"
DATABASE_URL="postgresql://user:pass@localhost/dbname"
```

## 📊 **Monitoring**

### **Railway Logs**
```bash
railway logs --tail
```

### **Health Monitoring**
```bash
# Check all agents
curl https://your-app.up.railway.app:8000/health
curl https://your-app.up.railway.app:8001/health
curl https://your-app.up.railway.app:8002/health
```

### **Database Monitoring**
```bash
# List all markets
curl https://your-app.up.railway.app:8002/markets
```

## 🔄 **Migration from Original System**

### **Browser Extension Update**
Update your browser extension to use the new endpoints:

```javascript
// Old endpoints
const GENERATOR_URL = "https://old-app.up.railway.app/generator/generate";
const RESOLVER_URL = "https://old-app.up.railway.app/resolver/resolve";

// New endpoints
const GENERATOR_URL = "https://new-app.up.railway.app:8000/analyze-market";
const RESOLVER_URL = "https://new-app.up.railway.app:8001/resolve-market";
const COORDINATOR_URL = "https://new-app.up.railway.app:8002/create-market";
```

### **Testing Migration**
```bash
# Test old system
curl https://old-app.up.railway.app/generator/generate

# Test new system  
curl -X POST "https://new-app.up.railway.app:8000/analyze-market" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Will Bitcoin reach $100k?"}'
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Port Conflicts**: Railway may not support multiple ports
   - **Solution**: Use a reverse proxy or single endpoint

2. **Import Errors**: Module not found
   - **Solution**: Check Dockerfile.uagents includes all files

3. **Database Connection**: Connection refused
   - **Solution**: Verify DATABASE_URL is correct

4. **Blockchain Deployment**: RPC connection failed
   - **Solution**: Check RPC_URL and private key

### **Debug Commands**
```bash
# Check Railway status
railway status

# View logs
railway logs

# Restart deployment
railway up

# Check environment variables
railway variables
```

## 🎯 **Key Benefits**

✅ **True μAgent Communication** - Uses uagents protocols for inter-agent messaging  
✅ **Single Deployment** - One Railway instance for everything  
✅ **Same Logic** - All existing functions preserved  
✅ **Public Endpoints** - Accessible from anywhere  
✅ **Scalable** - Can run multiple instances  
✅ **Fault Tolerant** - Agents restart independently  
✅ **Future Ready** - Ready for blockchain integration  
✅ **Prize Money Ready** - Proper μAgent system for competitions  

## 📝 **Next Steps**

1. **Deploy to Railway** using the provided script
2. **Test all endpoints** to ensure functionality
3. **Update browser extension** to use new endpoints
4. **Monitor logs** for any issues
5. **Scale as needed** by running multiple instances 