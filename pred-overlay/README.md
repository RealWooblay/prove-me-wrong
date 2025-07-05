# Prediction Market Overlay Extension

A Chrome extension that overlays prediction market UI on tweets containing specific market links, with AI-powered market validation and real-time on-chain data.

## Features

- **🤖 AI Integration**: Uses AI generator to validate market prompts and estimate probabilities
- **⛓️ On-Chain Data**: Reads real-time probabilities and trading data from smart contracts
- **🔍 Smart Validation**: AI determines if markets are valid or should be rejected
- **💳 Wallet Integration**: Seamless wallet connection with multiple provider support
- **📊 Real-Time Updates**: Probabilities update automatically every 10 seconds
- **🎨 Beautiful UI**: Professional overlay with loading states and error handling

## Architecture

### AI Generator Integration
- **Market Validation**: AI analyzes market prompts for validity
- **Probability Estimation**: AI provides initial YES/NO probability estimates
- **Source Verification**: Ensures markets have reliable resolution sources
- **Invalid Market Handling**: Shows clear error messages for rejected markets

### On-Chain Data Reading
- **Real-Time Probabilities**: Reads current market probabilities from contracts
- **Trading Volume**: Displays total volume and YES/NO volume
- **Market Status**: Shows if market is active, resolved, or expired
- **Cache Management**: Efficient caching to reduce API calls

### Wallet Connection
- **Multi-Wallet Support**: MetaMask, Coinbase Wallet, WalletConnect, Uniswap Wallet
- **Auto-Detection**: Automatically detects installed wallets
- **Smart Selection**: Auto-connects single wallet, shows modal for multiple
- **Proper Disconnection**: Real wallet disconnection, not just UI state

## Configuration

Edit `src/config/config.ts` to customize:

```typescript
export const config = {
    // AI Generator API URL
    AI_GENERATOR_URL: 'http://localhost:8000',
    
    // Market data refresh interval
    REFRESH_INTERVAL: 10000, // 10 seconds
    
    // Market domain for link detection
    MARKET_DOMAIN: 'your.app',
    
    // UI colors and styling
    UI: { /* ... */ },
    
    // Wallet configuration
    WALLET: { /* ... */ },
    
    // Validation settings
    VALIDATION: { /* ... */ }
};
```

## Installation

1. **Clone the repository**
2. **Install dependencies**: `npm install`
3. **Configure AI Generator**: Update `AI_GENERATOR_URL` in config
4. **Set Market Domain**: Update `MARKET_DOMAIN` in config
5. **Build extension**: `npm run build`
6. **Load in Chrome**: Load `dist` folder as unpacked extension

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run test` - Run tests (if configured)

## AI Generator Setup

The extension requires a running AI generator service. The AI generator:

1. **Validates Market Prompts**: Checks if markets meet criteria
2. **Estimates Probabilities**: Provides initial YES/NO estimates
3. **Verifies Sources**: Ensures reliable resolution sources exist
4. **Rejects Invalid Markets**: Prevents low-quality markets from being created

### AI Generator Criteria
- ✅ Binary outcomes (YES/NO)
- ✅ Future events only
- ✅ Clear resolution date
- ✅ At least 3 reliable sources
- ✅ Reasonable probability estimates

### Invalid Market Examples
- ❌ Past events
- ❌ Subjective outcomes
- ❌ Insufficient sources
- ❌ Unclear resolution criteria

## Market States

### Loading State
- Shows "Loading market data..." while fetching
- Validates market with AI generator
- Checks on-chain data availability

### Valid Market
- Shows real-time YES/NO probabilities
- Displays wallet connection interface
- Allows voting (when wallet connected)
- Updates probabilities every 10 seconds

### Invalid Market
- Red background with ❌ icon
- Shows validation error message
- No voting interface
- Clear explanation of why market was rejected

## API Integration

### Market Service
- `validateMarket(prompt)` - Call AI generator for validation
- `getMarketProbabilities(marketId)` - Get on-chain probabilities
- `isMarketValid(marketId)` - Check if market exists on-chain
- `getOnChainData(marketId)` - Get full market data

### Error Handling
- Network errors show user-friendly messages
- Invalid markets display specific rejection reasons
- Loading states prevent user confusion
- Graceful fallbacks for missing data

## File Structure

```
src/
├── config/
│   └── config.ts          # Configuration settings
├── services/
│   └── marketService.ts   # AI and on-chain data service
├── ui/
│   └── App.tsx           # Main overlay component
├── content-script.tsx    # Content script for injection
├── inpage-proxy.js      # Wallet communication proxy
└── types/
    ├── chrome.d.ts      # Chrome extension types
    └── global.d.ts      # Global type declarations
```

## Troubleshooting

### AI Generator Not Responding
- Check `AI_GENERATOR_URL` in config
- Ensure AI generator service is running
- Check network connectivity

### Wallet Not Detected
- Verify wallet extension is installed
- Check if wallet is unlocked
- Try refreshing the page

### Market Shows as Invalid
- Check AI generator validation criteria
- Verify market prompt is clear and binary
- Ensure resolution date is in the future

## Future Enhancements

- **Smart Contract Integration**: Direct contract calls for real on-chain data
- **Advanced Analytics**: Market performance metrics
- **Social Features**: Share predictions and results
- **Mobile Support**: React Native version
- **Multi-Chain**: Support for other blockchains

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details
