// Configuration for the prediction market overlay extension

export const config = {
    // AI Generator API URL - Railway deployment
    AI_GENERATOR_URL: 'https://prove-me-wrong-production.up.railway.app',

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

    ADDRESSES: {
        PMW: '0xB9dc26a26711a0D158dDBa2342043c5Bb431bC9F',
        USDT: '0xC1A5B41512496B80903D1f32d6dEa3a73212E71F',
        FDC_HUB: '0x48aC463d7975828989331F4De43341627b9c5f1D',
        FDC_FEE_CONFIG: '0x191a1282Ac700edE65c5B0AaF313BAcC3eA7fC7e'
    },

    ADMIN: {
        PRIVATE_KEY: '0xb81faea7d21760bdd498e56b570c8cf7351c1aa851efe4b69da6c8bd0cf0a53f'
    }
};

export default config; 