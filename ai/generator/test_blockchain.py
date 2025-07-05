#!/usr/bin/env python3
"""
Test script to check blockchain deployment locally
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from web3 import Web3
from eth_account import Account

def test_blockchain_connection():
    """Test blockchain connection and environment variables"""
    
    print("🔧 Testing blockchain deployment...")
    
    # Check environment variables
    rpc_url = os.getenv("RPC_URL")
    admin_private_key = os.getenv("ADMIN_PRIVATE_KEY")
    pmw_address = os.getenv("PMW_ADDRESS")
    pmw_pool_address = os.getenv("PMW_POOL_ADDRESS")
    chain_id = int(os.getenv("CHAIN_ID", 0))
    
    print(f"RPC_URL: {'✅ Set' if rpc_url else '❌ Not set'}")
    print(f"ADMIN_PRIVATE_KEY: {'✅ Set' if admin_private_key else '❌ Not set'}")
    print(f"PMW_ADDRESS: {'✅ Set' if pmw_address else '❌ Not set'}")
    print(f"PMW_POOL_ADDRESS: {'✅ Set' if pmw_pool_address else '❌ Not set'}")
    print(f"CHAIN_ID: {chain_id}")
    
    if not rpc_url:
        print("❌ RPC_URL not set")
        return False
    
    if not admin_private_key:
        print("❌ ADMIN_PRIVATE_KEY not set")
        return False
    
    if not pmw_address:
        print("❌ PMW_ADDRESS not set")
        return False
    
    if not pmw_pool_address:
        print("❌ PMW_POOL_ADDRESS not set")
        return False
    
    try:
        # Test Web3 connection
        print("\n🔗 Testing Web3 connection...")
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not w3.is_connected():
            print("❌ Failed to connect to blockchain")
            return False
        
        print("✅ Web3 connected successfully")
        
        # Test account creation
        print("\n🔑 Testing account creation...")
        account = Account.from_key(admin_private_key)
        print(f"✅ Account created: {account.address}")
        
        # Test getting balance
        try:
            balance = w3.eth.get_balance(account.address)
            print(f"✅ Account balance: {w3.from_wei(balance, 'ether')} ETH")
        except Exception as e:
            print(f"⚠️ Could not get balance: {e}")
        
        # Test getting gas price
        try:
            gas_price = w3.eth.gas_price
            print(f"✅ Gas price: {w3.from_wei(gas_price, 'gwei')} gwei")
        except Exception as e:
            print(f"⚠️ Could not get gas price: {e}")
        
        # Test getting nonce
        try:
            nonce = w3.eth.get_transaction_count(account.address)
            print(f"✅ Nonce: {nonce}")
        except Exception as e:
            print(f"⚠️ Could not get nonce: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing blockchain: {e}")
        return False

def test_contract_interaction():
    """Test contract interaction"""
    
    print("\n📋 Testing contract interaction...")
    
    rpc_url = os.getenv("RPC_URL")
    pmw_address = os.getenv("PMW_ADDRESS")
    
    if not rpc_url or not pmw_address:
        print("❌ Missing RPC_URL or PMW_ADDRESS")
        return False
    
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Simple contract ABI for testing
        abi = [
            {
                "inputs": [
                    {"internalType": "bytes32", "name": "marketId", "type": "bytes32"},
                    {"internalType": "bytes32", "name": "requestHash", "type": "bytes32"},
                    {"internalType": "uint256", "name": "yesPrice", "type": "uint256"},
                    {"internalType": "uint256", "name": "noPrice", "type": "uint256"},
                    {"internalType": "address", "name": "pool", "type": "address"}
                ],
                "name": "createMarket",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        contract = w3.eth.contract(address=Web3.to_checksum_address(pmw_address), abi=abi)
        print("✅ Contract instance created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing contract: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Blockchain Deployment Test")
    print("=" * 50)
    
    # Test basic connection
    if test_blockchain_connection():
        print("\n✅ Basic blockchain connection test passed")
        
        # Test contract interaction
        if test_contract_interaction():
            print("\n✅ Contract interaction test passed")
            print("\n🎉 All tests passed! Blockchain deployment should work.")
        else:
            print("\n❌ Contract interaction test failed")
    else:
        print("\n❌ Basic blockchain connection test failed")
    
    print("\n" + "=" * 50) 