# Blockchain Integration Setup

This document explains how to set up the blockchain integration for the Market Resolver Agent.

## Overview

The resolver now includes blockchain integration that automatically calls the `resolveMarket` function on the ProveMeWrong smart contract when a market is resolved.

## Environment Variables

Set the following environment variables to enable blockchain integration:

```bash
# Blockchain Configuration
RPC_URL=https://sepolia.infura.io/v3/YOUR-PROJECT-ID
PMW_ADDRESS=0x0000000000000000000000000000000000000000  # Deployed contract address
ADMIN_PRIVATE_KEY=0x0000000000000000000000000000000000000000000000000000000000000000
CHAIN_ID=11155111  # Sepolia testnet
```

### Required Variables

- **RPC_URL**: Your Ethereum RPC endpoint (Infura, Alchemy, etc.)
- **PMW_ADDRESS**: The deployed ProveMeWrong contract address
- **ADMIN_PRIVATE_KEY**: Private key of the account that will call resolveMarket
- **CHAIN_ID**: Network chain ID (11155111 for Sepolia)

## Setup Steps

1. **Deploy the ProveMeWrong Contract**
   ```bash
   cd contracts
   npm install
   npx hardhat deploy --network sepolia
   ```

2. **Get the Contract Address**
   After deployment, note the contract address and set it as `PMW_ADDRESS`.

3. **Set Up Admin Account**
   - Create or use an existing Ethereum account
   - Fund it with test ETH for gas fees
   - Set the private key as `ADMIN_PRIVATE_KEY`

4. **Configure Environment**
   ```bash
   export RPC_URL="https://sepolia.infura.io/v3/YOUR-PROJECT-ID"
   export PMW_ADDRESS="0x...your_contract_address..."
   export ADMIN_PRIVATE_KEY="0x...your_private_key..."
   export CHAIN_ID="11155111"
   ```

## Testing

Run the test script to verify blockchain integration:

```bash
cd ai/resolver
python test_resolver.py
```

The test will check:
- ✅ Blockchain configuration
- ✅ Network connectivity
- ✅ Contract address validity

## How It Works

1. **Market Resolution**: When a market is resolved (YES/NO outcome), the resolver automatically calls `resolveMarket` on the blockchain.

2. **Proof Creation**: The resolver creates a proof structure containing:
   - Request body (API call to get outcome)
   - Response body (outcome data)
   - Signature (placeholder for now)

3. **Transaction**: The admin account signs and sends the transaction to resolve the market.

4. **Verification**: The smart contract verifies the proof and updates the market outcome.

## Troubleshooting

### Common Issues

1. **"Web3 not available"**
   - Check RPC_URL is set correctly
   - Verify network connectivity

2. **"ADMIN_PRIVATE_KEY not configured"**
   - Set the ADMIN_PRIVATE_KEY environment variable
   - Ensure the account has sufficient ETH for gas

3. **"PMW_ADDRESS not configured"**
   - Deploy the contract first
   - Set the correct contract address

4. **Transaction failures**
   - Check gas limits
   - Verify contract address is correct
   - Ensure admin account has sufficient ETH

### Debug Mode

Enable debug logging to see detailed blockchain operations:

```bash
export LOG_LEVEL=DEBUG
```

## Security Notes

- **Never commit private keys** to version control
- Use environment variables or secure key management
- Consider using a dedicated admin account for resolutions
- Monitor gas costs and transaction success rates

## Future Enhancements

- [ ] Add proper signature verification
- [ ] Implement retry logic for failed transactions
- [ ] Add transaction monitoring and alerts
- [ ] Support for multiple networks
- [ ] Gas optimization strategies 