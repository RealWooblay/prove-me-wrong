#!/usr/bin/env python3
"""
Startup script for the Prove Me Wrong μAgent system
"""

import asyncio
import subprocess
import sys
import os
import time
import signal
import logging
from typing import List

# Load environment variables from .env file if it exists
import os
from pathlib import Path

env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    print("✅ Loaded environment variables from .env file")
else:
    print("⚠️ No .env file found. Create one with your API keys for local testing.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentManager:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.agents = [
            {
                "name": "Market Generator Agent",
                "script": "market_generator_agent.py",
                "port": 8000
            },
            {
                "name": "Market Resolver Agent", 
                "script": "market_resolver_agent.py",
                "port": 8001
            },
            {
                "name": "Market Coordinator Agent",
                "script": "market_coordinator_agent.py", 
                "port": 8002
            }
        ]
    
    def start_agent(self, agent_info: dict) -> subprocess.Popen:
        """Start a single agent"""
        script_path = os.path.join(os.path.dirname(__file__), agent_info["script"])
        
        logger.info(f"🚀 Starting {agent_info['name']} on port {agent_info['port']}...")
        
        # Start the agent process
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        self.processes.append(process)
        logger.info(f"✅ {agent_info['name']} started (PID: {process.pid})")
        
        return process
    
    def start_all_agents(self):
        """Start all agents"""
        logger.info("🎯 Starting Prove Me Wrong μAgent System...")
        
        for agent_info in self.agents:
            try:
                self.start_agent(agent_info)
                # Small delay between starts
                time.sleep(2)
            except Exception as e:
                logger.error(f"❌ Failed to start {agent_info['name']}: {e}")
                self.shutdown()
                sys.exit(1)
        
        logger.info("🎉 All agents started successfully!")
        logger.info("📊 Agent Status:")
        logger.info("   - Market Generator Agent: http://localhost:8000")
        logger.info("   - Market Resolver Agent: http://localhost:8001") 
        logger.info("   - Market Coordinator Agent: http://localhost:8002")
        logger.info("")
        logger.info("🔍 Health Check Endpoints:")
        logger.info("   - GET http://localhost:8000/health")
        logger.info("   - GET http://localhost:8001/health")
        logger.info("   - GET http://localhost:8002/health")
        logger.info("")
        logger.info("📝 API Endpoints:")
        logger.info("   - POST http://localhost:8000/analyze-market")
        logger.info("   - POST http://localhost:8001/resolve-market")
        logger.info("   - POST http://localhost:8002/create-market")
        logger.info("")
        logger.info("Press Ctrl+C to stop all agents")
    
    def shutdown(self):
        """Shutdown all agents gracefully"""
        logger.info("🛑 Shutting down μAgent system...")
        
        for i, process in enumerate(self.processes):
            if process.poll() is None:  # Process is still running
                logger.info(f"🛑 Stopping {self.agents[i]['name']} (PID: {process.pid})...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                    logger.info(f"✅ {self.agents[i]['name']} stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ Force killing {self.agents[i]['name']} (PID: {process.pid})...")
                    process.kill()
                    process.wait()
                    logger.info(f"✅ {self.agents[i]['name']} force stopped")
        
        logger.info("🎯 All agents stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"📡 Received signal {signum}")
    if hasattr(signal_handler, 'manager'):
        signal_handler.manager.shutdown()
    sys.exit(0)

def main():
    """Main function"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start agent manager
    manager = AgentManager()
    signal_handler.manager = manager  # Store reference for signal handler
    
    try:
        manager.start_all_agents()
        
        # Keep the main process alive
        while True:
            time.sleep(1)
            
            # Check if any agent has died
            for i, process in enumerate(manager.processes):
                if process.poll() is not None:
                    logger.error(f"❌ {manager.agents[i]['name']} has died unexpectedly")
                    manager.shutdown()
                    sys.exit(1)
                    
    except KeyboardInterrupt:
        logger.info("📡 Received keyboard interrupt")
        manager.shutdown()
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        manager.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    main() 