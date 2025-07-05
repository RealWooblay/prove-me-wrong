// Configuration for the prediction market overlay extension

export const config = {
    // AI Generator API URL - change this to point to your AI generator service
    AI_GENERATOR_URL: 'http://localhost:8000',

    // Market data refresh interval (in milliseconds)
    REFRESH_INTERVAL: 10000, // 10 seconds

    // Market domain for link detection
    MARKET_DOMAIN: 'your.app', // Change this to your actual domain

    // UI Configuration
    UI: {
        // Colors
        colors: {
            primary: '#3b82f6',
            secondary: '#ef4444',
            success: '#10b981',
            warning: '#f59e0b',
            error: '#ef4444',
            background: 'rgba(15,23,42,0.97)',
            invalidBackground: 'rgba(239,68,68,0.97)',
        },

        // Sizes
        borderRadius: '1rem',
        buttonPadding: '0.5em 1.5em',
        modalZIndex: 10000,
    },

    // Wallet Configuration
    WALLET: {
        // Supported wallet types
        supportedWallets: [
            { name: 'MetaMask', icon: '🦊', color: '#f6851b' },
            { name: 'Coinbase Wallet', icon: '🪙', color: '#0052ff' },
            { name: 'WalletConnect', icon: '🔗', color: '#3b99fc' },
            { name: 'Uniswap Wallet', icon: '🦄', color: '#ff007a' },
        ],

        // Auto-connect if only one wallet available
        autoConnectSingle: true,
    },

    // Market Validation
    VALIDATION: {
        // Minimum confidence threshold for market validation
        minConfidence: 0.7,

        // Minimum number of reliable sources required
        minReliableSources: 3,

        // Default market expiration days
        defaultExpirationDays: 30,
    },
};

export default config; 