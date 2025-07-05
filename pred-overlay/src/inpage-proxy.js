// inpage-proxy.js - runs in the page context, NOT the content-script
window.addEventListener('message', async (e) => {
    if (e.source !== window || e.data?.type !== 'CS_REQUEST') return;
    try {
        const result = await window.ethereum.request(e.data.payload);
        window.postMessage({ type: 'CS_RESPONSE', id: e.data.id, result }, '*');
    } catch (err) {
        window.postMessage({ type: 'CS_RESPONSE', id: e.data.id, error: err.message }, '*');
    }
});

// Listen for wallet events and forward them to content script
if (window.ethereum) {
    // Listen for account changes
    window.ethereum.on('accountsChanged', (accounts) => {
        window.postMessage({
            type: 'WALLET_ACCOUNTS_CHANGED',
            accounts: accounts
        }, '*');
    });

    // Listen for connection state changes
    window.ethereum.on('connect', (connectInfo) => {
        window.postMessage({
            type: 'WALLET_CONNECTED',
            chainId: connectInfo.chainId
        }, '*');
    });

    window.ethereum.on('disconnect', (error) => {
        window.postMessage({
            type: 'WALLET_DISCONNECTED',
            error: error.message
        }, '*');
    });

    // Listen for chain changes
    window.ethereum.on('chainChanged', (chainId) => {
        window.postMessage({
            type: 'WALLET_CHAIN_CHANGED',
            chainId: chainId
        }, '*');
    });
} 