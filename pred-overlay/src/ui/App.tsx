import React, { useState, useEffect } from 'react';
import marketService, { MarketResponse } from '../services/marketService';
import config from '../config/config';

// Proxy request function to communicate with the main page context
function providerRequest(payload: { method: string; params?: any[] }) {
    return new Promise((resolve, reject) => {
        const id = crypto.randomUUID();
        window.postMessage({ type: 'CS_REQUEST', id, payload }, '*');

        function handler(e: MessageEvent) {
            if (e.data?.type !== 'CS_RESPONSE' || e.data.id !== id) return;
            window.removeEventListener('message', handler);
            e.data.error ? reject(new Error(e.data.error)) : resolve(e.data.result);
        }
        window.addEventListener('message', handler);
    });
}

const connectBtnStyle: React.CSSProperties = {
    padding: '0.5em 1.6em',
    borderRadius: '2em',
    background: '#10b981',
    color: '#fff',
    fontWeight: 600,
    fontSize: '.95em',
    border: 'none',
    cursor: 'pointer',
    boxShadow: '0 1px 4px #0002',
};

export function App({ marketId, title }: { marketId: string; title: string }) {
    const [status, setStatus] = useState('');
    const [account, setAccount] = useState<string | null>(null);
    const [yesProb, setYesProb] = useState(50);
    const [noProb, setNoProb] = useState(50);
    const [isValidMarket, setIsValidMarket] = useState<boolean | null>(null); // null = loading/unknown
    const [isLoading, setIsLoading] = useState(true);
    const [marketData, setMarketData] = useState<MarketResponse | null>(null);

    // Check wallet connection on mount and listen for changes
    useEffect(() => {
        // Check initial connection
        checkWalletConnection();

        // Listen for wallet state changes from the page
        const handleWalletChange = (e: MessageEvent) => {
            if (e.source !== window) return;

            // Handle account changes
            if (e.data?.type === 'WALLET_ACCOUNTS_CHANGED') {
                if (e.data.accounts && e.data.accounts.length > 0) {
                    setAccount(e.data.accounts[0]);
                    setStatus('Wallet connected!');
                } else {
                    setAccount(null);
                    setStatus('Wallet disconnected');
                }
            }

            // Handle connection state changes
            if (e.data?.type === 'WALLET_CONNECTED') {
                checkWalletConnection();
            }

            if (e.data?.type === 'WALLET_DISCONNECTED') {
                setAccount(null);
                setStatus('Wallet disconnected');
            }
        };

        window.addEventListener('message', handleWalletChange);
        return () => window.removeEventListener('message', handleWalletChange);
    }, []);

    // Load market data and probabilities
    useEffect(() => {
        // Initial validation - only happens once
        validateMarketOnce();

        // Set up interval to refresh only probabilities (not validation)
        const interval = setInterval(updateProbabilities, config.REFRESH_INTERVAL);

        return () => clearInterval(interval);
    }, [marketId]);

    // Validate market once (cached after first call)
    async function validateMarketOnce() {
        try {
            setIsLoading(true);
            console.log(`[App] Validating market once for ID: ${marketId}`);

            const validation = await marketService.validateMarket(title, marketId);
            setMarketData(validation);

            if (validation.success && validation.market) {
                setIsValidMarket(true);
                setStatus('Market validated');

                // Get initial probabilities immediately after validation
                console.log(`[App] Getting initial probabilities for market ID: ${marketId}`);
                const probabilities = await marketService.getMarketProbabilities(marketId);
                setYesProb(probabilities.yesProb);
                setNoProb(probabilities.noProb);
                console.log(`[App] Initial probabilities set - YES: ${probabilities.yesProb}%, NO: ${probabilities.noProb}%`);

            } else {
                if (validation.error && validation.error.includes('Cannot connect to AI generator')) {
                    setIsValidMarket(true);
                    setYesProb(0);
                    setNoProb(0);
                    setStatus('AI generator offline - showing fallback data');
                } else {
                    setIsValidMarket(false);
                    setYesProb(0);
                    setNoProb(0);
                    setStatus(validation.error || 'Invalid market');
                }
            }
        } catch (error) {
            console.error('Error validating market:', error);
            setStatus('Error validating market');
        } finally {
            setIsLoading(false);
        }
    }

    // Update probabilities only (no validation)
    async function updateProbabilities() {
        if (!isValidMarket) return; // Don't update if market is invalid

        try {
            console.log(`[App] Updating probabilities for market ID: ${marketId}`);

            const probabilities = await marketService.getMarketProbabilities(marketId);
            setYesProb(probabilities.yesProb);
            setNoProb(probabilities.noProb);

            if (probabilities.isValid) {
                setStatus('Market active - probabilities updated');
            } else {
                setStatus('Market validated but not found on-chain');
            }
        } catch (error) {
            console.error('Error updating probabilities:', error);
            // Don't change status on probability update errors
        }
    }

    async function checkWalletConnection() {
        try {
            const accounts = await providerRequest({ method: 'eth_accounts' }) as string[];
            if (accounts && accounts.length > 0) {
                setAccount(accounts[0]);
                setStatus('Wallet connected!');
            } else {
                setAccount(null);
                setStatus('');
            }
        } catch (err) {
            setAccount(null);
            setStatus('');
        }
    }

    async function connectWallet() {
        try {
            setStatus('Connecting to wallet...');
            const accounts = await providerRequest({ method: 'eth_requestAccounts' }) as string[];
            if (accounts && accounts.length) {
                setAccount(accounts[0]);
                setStatus('Wallet connected!');
            } else {
                setStatus('No accounts found');
            }
        } catch (err: any) {
            setStatus(err.message || 'Wallet connection failed.');
        }
    }

    async function disconnectWallet() {
        try {
            setStatus('Disconnecting wallet...');
            // Try to revoke permissions - this is the standard way to disconnect
            await providerRequest({
                method: 'wallet_revokePermissions',
                params: [{ eth_accounts: {} }]
            });
            setAccount(null);
            setStatus('Wallet disconnected');
        } catch (err: any) {
            // If revoke fails, just clear the local state
            // This is common as not all wallets support revoke
            setAccount(null);
            setStatus('Wallet disconnected');
        }
    }

    function shortAddr(addr: string) {
        return `${addr.slice(0, 6)}…${addr.slice(-4)}`;
    }

    function vote(choice: 'YES' | 'NO') {
        if (!account) {
            setStatus('Please connect your wallet first');
            return;
        }
        if (!isValidMarket) {
            setStatus('Cannot vote on invalid market');
            return;
        }
        setStatus(`You voted ${choice}!`);
    }

    // Show loading state
    if (isLoading || isValidMarket === null) {
        return (
            <span style={{
                display: 'inline-block',
                verticalAlign: 'middle',
                background: 'rgba(15,23,42,0.97)',
                color: '#fff',
                borderRadius: '1rem',
                boxShadow: '0 2px 8px #000a',
                padding: '0.5em 1em',
                margin: '0 0.25em',
                zIndex: 1,
            }}>
                <div style={{ fontWeight: 700, fontSize: '1.05rem', textAlign: 'center', marginBottom: '.4em', wordBreak: 'break-word' }}>
                    {title}
                </div>
                <div style={{ textAlign: 'center', padding: '1em' }}>
                    <div style={{ fontSize: '0.9em', opacity: 0.8 }}>Validating market...</div>
                </div>
            </span>
        );
    }

    // Show invalid market state
    if (isValidMarket === false) {
        return (
            <span style={{
                display: 'inline-block',
                verticalAlign: 'middle',
                background: 'rgba(239,68,68,0.97)',
                color: '#fff',
                borderRadius: '1rem',
                boxShadow: '0 2px 8px #000a',
                padding: '0.5em 1em',
                margin: '0 0.25em',
                zIndex: 1,
            }}>
                <div style={{ fontWeight: 700, fontSize: '1.05rem', textAlign: 'center', marginBottom: '.4em', wordBreak: 'break-word' }}>
                    {title}
                </div>
                <div style={{ textAlign: 'center', padding: '0.5em' }}>
                    <div style={{ fontSize: '1em', fontWeight: 600, marginBottom: '0.5em' }}>❌ Invalid Market</div>
                    <div style={{ fontSize: '0.9em', opacity: 0.8 }}>
                        {marketData?.error || 'This market does not meet validation criteria'}
                    </div>
                </div>
            </span>
        );
    }

    return (
        <span style={{
            display: 'inline-block',
            verticalAlign: 'middle',
            background: 'rgba(15,23,42,0.97)',
            color: '#fff',
            borderRadius: '1rem',
            boxShadow: '0 2px 8px #000a',
            padding: '0.5em 1em',
            margin: '0 0.25em',
            zIndex: 1,
        }}>
            <div style={{ fontWeight: 700, fontSize: '1.05rem', textAlign: 'center', marginBottom: '.4em', wordBreak: 'break-word' }}>
                {title}
            </div>
            <div style={{ display: 'flex', gap: '1.2em', alignItems: 'flex-end', justifyContent: 'center' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <div style={{ fontSize: '1rem', fontWeight: 600, color: '#38bdf8', marginBottom: '.2em' }}>{yesProb}%</div>
                    <button
                        style={{
                            padding: '0.5em 1.5em',
                            borderRadius: '2em',
                            background: '#3b82f6',
                            color: '#fff',
                            fontWeight: 600,
                            fontSize: '1em',
                            border: 'none',
                            cursor: 'pointer',
                            boxShadow: '0 1px 4px #0002',
                            opacity: account ? 1 : 0.4,
                        }}
                        onClick={() => vote('YES')}
                        disabled={!account}
                    >
                        YES
                    </button>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <div style={{ fontSize: '1rem', fontWeight: 600, color: '#f87171', marginBottom: '.2em' }}>{noProb}%</div>
                    <button
                        style={{
                            padding: '0.5em 1.5em',
                            borderRadius: '2em',
                            background: '#ef4444',
                            color: '#fff',
                            fontWeight: 600,
                            fontSize: '1em',
                            border: 'none',
                            cursor: 'pointer',
                            boxShadow: '0 1px 4px #0002',
                            opacity: account ? 1 : 0.4,
                        }}
                        onClick={() => vote('NO')}
                        disabled={!account}
                    >
                        NO
                    </button>
                </div>
            </div>
            <div style={{ marginTop: '.6em', textAlign: 'center' }}>
                {account ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5em' }}>
                        <span style={{ fontSize: '.95em', opacity: 0.9 }}>
                            🔗 {shortAddr(account)}
                        </span>
                        <button
                            onClick={disconnectWallet}
                            style={{
                                padding: '0.2em 0.4em',
                                borderRadius: '0.3em',
                                background: '#ef4444',
                                color: '#fff',
                                fontWeight: 600,
                                fontSize: '0.7em',
                                border: 'none',
                                cursor: 'pointer',
                            }}
                            title="Disconnect wallet"
                        >
                            ×
                        </button>
                    </div>
                ) : (
                    <button style={connectBtnStyle} onClick={connectWallet}>
                        Connect Wallet
                    </button>
                )}
                <div style={{ fontSize: '.9em', marginTop: '.3em', opacity: 0.8 }}>
                    {status || (account ? 'Choose YES or NO to vote.' : 'Connect your wallet to vote.')}
                </div>
            </div>
        </span>
    );
}
