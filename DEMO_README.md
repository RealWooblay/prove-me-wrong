# 🎬 Prove Me Wrong - Demo Scripts

Welcome to the Prove Me Wrong demo suite! This script tests the actual working endpoints.

## 🚀 Quick Start

Run the Railway demo:
```bash
python3 demo_real.py
```

Run the local μAgents demo:
```bash
python3 demo_agents_simple.py
```

## 📋 What Each Demo Tests

### `demo_real.py` - Railway Endpoints Demo
**Real Endpoints That Work:**
- ✅ AI Generator health check
- ✅ Market Resolver health check  
- ✅ Market listing
- ✅ Market creation (future events only)
- ✅ Market validation rules
- ✅ Market resolution

**What It Shows:**
- 🎯 Actual API responses
- 🔍 Real validation rules in action
- 📊 System analysis of working vs broken endpoints
- 📱 Extension integration points

### `demo_agents_simple.py` - Local μAgents Demo
**What It Tests:**
- ✅ Local μAgent processes
- ✅ Agent communication via μAgent protocol
- ✅ HTTP endpoints for each agent
- ✅ Real-time message monitoring

**What It Shows:**
- 🤖 Real agent processes running locally
- 📡 Agent communication in action
- 🌐 HTTP endpoints for testing
- 📊 Live message monitoring

## 📋 Demo Scripts

### `demo_real.py` - Railway Endpoints Demo
**What it shows:**
- Actual working endpoints
- Real API responses
- Market validation rules
- System analysis
- Extension integration points

**Features:**
- 🎯 Real endpoint testing
- 📊 Actual JSON responses
- 🔍 Validation rule demonstration
- 📈 System health analysis
- 📱 Extension integration testing

### `demo_agents_simple.py` - Local μAgents Demo
**What it shows:**
- Real μAgent processes running locally
- Agent communication via μAgent protocol
- HTTP endpoints for each agent
- Real-time message monitoring

**Features:**
- 🤖 Local agent startup
- 📡 Real-time communication monitoring
- 🌐 HTTP endpoint testing
- 📊 Process management

## 🎯 Demo Scenarios

### Market Creation Flow
1. User submits future prediction question
2. AI Generator validates criteria (future events only)
3. Market is created and stored
4. Market is available for trading

### Market Resolution Flow
1. Time passes, market is active
2. Resolver checks for outcomes
3. Market is resolved if criteria met
4. Results are processed

## 🛠️ Requirements

```bash
pip3 install requests
```

## 🌐 Live System

- **Railway URL:** https://prove-me-wrong-production.up.railway.app
- **Extension:** Chrome extension for market detection

## 📱 Extension Integration

The demo shows how the extension would:
1. Create markets from tweets
2. Get real-time probabilities
3. Check market outcomes
4. Display betting interface

## 🎊 Demo Output

The real demo provides:
- ✅ Actual API responses
- 📊 Real JSON data
- 🔍 Validation rule testing
- 📈 System health analysis
- 📱 Extension endpoint testing

## 🚀 Current Status

The demo confirms:
- ✅ AI Generator service is working
- ✅ Market Resolver service is working
- ✅ Market validation rules are working
- ✅ Market creation (future events) is working
- ⚠️ Some blockchain endpoints need implementation

---

**Ready to see what's actually working? Run `python3 demo_real.py`!** 🎯✨ 