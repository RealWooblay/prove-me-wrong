import React, { useState, useEffect } from 'react';
import marketService, { MarketResponse } from '../services/marketService';
import config from '../config/config';
import { encodeFunctionData, parseEther, getAddress, keccak256, toBytes, toHex, parseUnits } from 'viem';
import { createPublicClient, http } from 'viem'
import { flareTestnet } from 'viem/chains'

export const publicClient = createPublicClient({
    chain: flareTestnet,
    transport: http()
})

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

// Modern styling constants
const styles = {
    container: {
        display: 'inline-block',
        verticalAlign: 'middle',
        background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(148, 163, 184, 0.1)',
        borderRadius: '16px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.05)',
        padding: '16px',
        margin: '0 6px',
        minWidth: '280px',
        maxWidth: '360px',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        color: '#f8fafc',
        position: 'relative' as const,
        overflow: 'hidden',
    },
    containerBefore: {
        content: '""',
        position: 'absolute' as const,
        top: 0,
        left: 0,
        right: 0,
        height: '1px',
        background: 'linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.3), transparent)',
    },
    title: {
        fontSize: '16px',
        fontWeight: '700',
        textAlign: 'center' as const,
        marginBottom: '12px',
        wordBreak: 'break-word' as const,
        lineHeight: '1.3',
        color: '#f1f5f9',
        letterSpacing: '-0.025em',
    },
    betInputContainer: {
        marginBottom: '16px',
        textAlign: 'center' as const,
    },
    betInputLabel: {
        fontSize: '12px',
        fontWeight: '600',
        color: '#94a3b8',
        marginBottom: '8px',
        textTransform: 'uppercase' as const,
        letterSpacing: '0.05em',
    },
    betInput: {
        width: '100px',
        padding: '8px 12px',
        borderRadius: '8px',
        border: '1px solid rgba(148, 163, 184, 0.2)',
        background: 'rgba(30, 41, 59, 0.5)',
        color: '#f8fafc',
        fontSize: '13px',
        fontWeight: '600',
        textAlign: 'center' as const,
        outline: 'none',
        transition: 'all 0.2s ease',
        backdropFilter: 'blur(10px)',
    },
    betInputFocus: {
        borderColor: '#3b82f6',
        boxShadow: '0 0 0 3px rgba(59, 130, 246, 0.1)',
        background: 'rgba(30, 41, 59, 0.8)',
    },
    betCalculator: {
        marginBottom: '16px',
        padding: '12px',
        borderRadius: '10px',
        background: 'rgba(30, 41, 59, 0.3)',
        border: '1px solid rgba(148, 163, 184, 0.1)',
        backdropFilter: 'blur(10px)',
    },
    betCalculatorTitle: {
        fontSize: '12px',
        fontWeight: '600',
        color: '#94a3b8',
        marginBottom: '8px',
        textTransform: 'uppercase' as const,
        letterSpacing: '0.05em',
        textAlign: 'center' as const,
    },
    betCalculatorRow: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '6px',
        fontSize: '13px',
    },
    betCalculatorLabel: {
        color: '#cbd5e1',
        fontWeight: '500',
    },
    betCalculatorValue: {
        color: '#f8fafc',
        fontWeight: '600',
    },
    yesWinnings: {
        color: '#10b981',
    },
    noWinnings: {
        color: '#ef4444',
    },
    votingSection: {
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
        marginBottom: '16px',
    },
    voteOption: {
        display: 'flex',
        flexDirection: 'column' as const,
        alignItems: 'center',
        gap: '8px',
    },
    probabilityDisplay: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '4px',
        fontSize: '16px',
        fontWeight: '700',
        padding: '6px 12px',
        borderRadius: '8px',
        background: 'rgba(30, 41, 59, 0.3)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(148, 163, 184, 0.1)',
    },
    yesProbability: {
        color: '#10b981',
    },
    noProbability: {
        color: '#ef4444',
    },
    voteButton: {
        width: '100%',
        padding: '10px 16px',
        borderRadius: '10px',
        border: 'none',
        fontSize: '14px',
        fontWeight: '700',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        textTransform: 'uppercase' as const,
        letterSpacing: '0.05em',
        position: 'relative' as const,
        overflow: 'hidden',
    },
    yesButton: {
        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        color: '#ffffff',
        boxShadow: '0 4px 14px 0 rgba(16, 185, 129, 0.3)',
    },
    yesButtonHover: {
        transform: 'translateY(-2px)',
        boxShadow: '0 8px 25px 0 rgba(16, 185, 129, 0.4)',
    },
    noButton: {
        background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
        color: '#ffffff',
        boxShadow: '0 4px 14px 0 rgba(239, 68, 68, 0.3)',
    },
    noButtonHover: {
        transform: 'translateY(-2px)',
        boxShadow: '0 8px 25px 0 rgba(239, 68, 68, 0.4)',
    },
    disabledButton: {
        opacity: 0.5,
        cursor: 'not-allowed',
        transform: 'none !important',
    },
    walletSection: {
        marginTop: '12px',
    },
    connectedWallet: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px',
        borderRadius: '8px',
        background: 'rgba(16, 185, 129, 0.1)',
        border: '1px solid rgba(16, 185, 129, 0.2)',
        marginBottom: '8px',
    },
    walletInfo: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        fontSize: '14px',
        fontWeight: '600',
    },
    walletAddress: {
        color: '#10b981',
        fontFamily: 'monospace',
    },
    disconnectButton: {
        padding: '6px 10px',
        borderRadius: '8px',
        border: 'none',
        background: 'rgba(239, 68, 68, 0.1)',
        color: '#ef4444',
        cursor: 'pointer',
        fontSize: '12px',
        fontWeight: '600',
        transition: 'all 0.2s ease',
    },
    connectButton: {
        width: '100%',
        padding: '10px 16px',
        borderRadius: '8px',
        border: 'none',
        background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
        color: '#ffffff',
        fontSize: '13px',
        fontWeight: '600',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '6px',
    },
    statusMessage: {
        fontSize: '11px',
        textAlign: 'center' as const,
        marginTop: '8px',
        padding: '6px 10px',
        borderRadius: '6px',
        background: 'rgba(148, 163, 184, 0.1)',
        color: '#94a3b8',
        fontWeight: '500',
    },
    loadingContainer: {
        textAlign: 'center' as const,
        padding: '24px 16px',
    },
    loadingSpinner: {
        width: '32px',
        height: '32px',
        border: '2px solid rgba(148, 163, 184, 0.2)',
        borderTop: '2px solid #3b82f6',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        margin: '0 auto 12px',
    },
    errorContainer: {
        textAlign: 'center' as const,
        padding: '16px',
        background: 'rgba(239, 68, 68, 0.1)',
        border: '1px solid rgba(239, 68, 68, 0.2)',
        borderRadius: '8px',
    },
    errorIcon: {
        fontSize: '24px',
        marginBottom: '8px',
    },
    errorTitle: {
        fontSize: '14px',
        fontWeight: '700',
        color: '#ef4444',
        marginBottom: '6px',
    },
    errorMessage: {
        fontSize: '12px',
        color: '#94a3b8',
    },
};

// Add CSS animations
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .modern-card {
        animation: fadeIn 0.3s ease-out;
    }
    
    .vote-button:hover:not(:disabled) {
        transform: translateY(-2px);
    }
    
    .vote-button:active:not(:disabled) {
        transform: translateY(0);
    }
`;
document.head.appendChild(styleSheet);

export function App({ marketId, title }: { marketId: string; title: string }) {
    const [status, setStatus] = useState('');
    const [account, setAccount] = useState<string | null>(null);
    const [yesProb, setYesProb] = useState(50);
    const [noProb, setNoProb] = useState(50);
    const [isValidMarket, setIsValidMarket] = useState<boolean | null>(null); // null = loading/unknown
    const [isLoading, setIsLoading] = useState(true);
    const [marketData, setMarketData] = useState<MarketResponse | null>(null);
    const [betAmount, setBetAmount] = useState('100'); // Default bet amount in USDT
    const [inputFocused, setInputFocused] = useState(false);

    // Calculate potential winnings
    const calculateWinnings = (betAmount: string, probability: number) => {
        const bet = parseFloat(betAmount);
        if (isNaN(bet) || bet <= 0 || probability <= 0 || probability >= 100) {
            return 0;
        }
        // If you bet on an outcome with X% probability, you get paid (100/X) * your bet
        return (100 / probability) * bet;
    };

    const yesWinnings = calculateWinnings(betAmount, yesProb);
    const noWinnings = calculateWinnings(betAmount, noProb);

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
                const data = await marketService.getOnChainData(marketId);
                if (!data) {
                    setStatus('Market not found on-chain');
                    return;
                }

                setYesProb(Number(data.noPrice) / 10 ** 16);
                setNoProb(Number(data.yesPrice) / 10 ** 16);
                console.log(`[App] Initial probabilities set - YES: ${data.yesPrice}%, NO: ${data.noPrice}%`);
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

            const data = await marketService.getOnChainData(marketId);
            if (!data) {
                setStatus('Market not found on-chain');
                return;
            }

            setYesProb(Number(data.noPrice) / 10 ** 16);
            setNoProb(Number(data.yesPrice) / 10 ** 16);
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

    async function vote(choice: 'YES' | 'NO') {
        if (!account) {
            setStatus('Please connect your wallet first');
            return;
        }
        if (!isValidMarket) {
            setStatus('Cannot vote on invalid market');
            return;
        }
        if (!marketData || !marketData.market) {
            setStatus('Market not found');
            return;
        }
        const market = marketData.market;

        const onchainData = await marketService.getOnChainData(market.id);
        console.log(`[App] Onchain data:`, onchainData);

        await marketService.resolveMarket(market.id);

        // Validate bet amount
        const betAmountNum = parseFloat(betAmount);
        if (isNaN(betAmountNum) || betAmountNum <= 0) {
            setStatus('Please enter a valid bet amount');
            return;
        }
        if (betAmountNum < 0.001) {
            setStatus('Minimum bet amount is 0.001 USDT');
            return;
        }

        try {
            setStatus('Approving spending...');

            const hashedMarketId = keccak256(toBytes(market.id));

            const x = await publicClient.readContract({
                address: getAddress(config.ADDRESSES.PMW),
                abi: [{
                    "inputs": [
                        {
                            "internalType": "bytes32",
                            "name": "marketId",
                            "type": "bytes32"
                        }
                    ],
                    "name": "getMarket",
                    "outputs": [
                        {
                            "internalType": "address",
                            "name": "",
                            "type": "address"
                        },
                        {
                            "internalType": "address",
                            "name": "",
                            "type": "address"
                        },
                        {
                            "internalType": "uint256",
                            "name": "",
                            "type": "uint256"
                        },
                        {
                            "internalType": "uint256",
                            "name": "",
                            "type": "uint256"
                        },
                        {
                            "internalType": "address",
                            "name": "",
                            "type": "address"
                        },
                        {
                            "internalType": "uint256",
                            "name": "",
                            "type": "uint256"
                        }
                    ],
                    "stateMutability": "view",
                    "type": "function"
                }],
                functionName: "getMarket",
                args: [hashedMarketId]
            });
            console.warn(x)

            // Convert bet amount to wei
            const betAmountWei = parseUnits(betAmount, 6);

            const approveData = encodeFunctionData({
                abi: [{
                    name: 'approve',
                    type: 'function',
                    inputs: [
                        { name: 'spender', type: 'address' },
                        { name: 'amount', type: 'uint256' }
                    ],
                    outputs: [{ name: '', type: 'bool' }],
                    stateMutability: 'nonpayable'
                }],
                functionName: 'approve',
                args: [getAddress(config.ADDRESSES.PMW), betAmountWei]
            });

            const approveTx = await providerRequest({
                method: "eth_sendTransaction",
                params: [{
                    from: account,
                    to: getAddress(config.ADDRESSES.USDT),
                    data: approveData,
                    gas: "0x186a0", // 100000 gas limit for approve
                    gasPrice: "0x9184e72a000", // 10000000000000 wei
                }]
            });

            await publicClient.waitForTransactionReceipt({ hash: approveTx as `0x${string}` });

            setStatus('Minting tokens...');

            const mintData = encodeFunctionData({
                abi: [{
                    name: 'mint',
                    type: 'function',
                    inputs: [
                        { name: 'marketId', type: 'bytes32' },
                        { name: 'amount', type: 'uint256' },
                        { name: 'outcome', type: 'bool' }
                    ],
                    outputs: [],
                    stateMutability: 'nonpayable'
                }],
                functionName: 'mint',
                args: ["0xc9462894569783d32ee536da4d97b1fe9d832a9afe46cf76169ff5ee46f0e457", betAmountWei, choice === 'YES']
            });

            const mintTx = await providerRequest({
                method: "eth_sendTransaction",
                params: [{
                    from: account,
                    to: getAddress(config.ADDRESSES.PMW),
                    data: mintData,
                    gas: "0x7A120", // 500000 gas limit for mint
                    gasPrice: "0x9184e72a000", // 10000000000000 wei
                }]
            });

            await publicClient.waitForTransactionReceipt({ hash: mintTx as `0x${string}` });

            setStatus(`You voted ${choice}! Transaction submitted.`);
        } catch (error) {
            console.error('Error voting:', error);
            setStatus('Vote failed. Please try again.');
        }
    }

    // Show loading state
    if (isLoading || isValidMarket === null) {
        return (
            <div style={{ ...styles.container, ...styles.loadingContainer }} className="modern-card">
                <div style={styles.title}>{title}</div>
                <div style={styles.loadingSpinner}></div>
                <div style={styles.statusMessage}>Validating market...</div>
            </div>
        );
    }

    // Show invalid market state
    if (isValidMarket === false) {
        return (
            <div style={{ ...styles.container, ...styles.errorContainer }} className="modern-card">
                <div style={styles.title}>❌ {title}</div>
                <div style={styles.errorTitle}>Invalid Market</div>
                <div style={styles.errorMessage}>
                    {marketData?.error || 'This market does not meet validation criteria'}
                </div>
            </div>
        );
    }

    return (
        <div style={styles.container} className="modern-card">
            <div style={styles.title}>{title}</div>

            {/* Bet Amount Input */}
            <div style={styles.betInputContainer}>
                <div style={styles.betInputLabel}>Bet Amount (USDT)</div>
                <input
                    type="number"
                    value={betAmount}
                    onChange={(e) => setBetAmount(e.target.value)}
                    onFocus={() => setInputFocused(true)}
                    onBlur={() => setInputFocused(false)}
                    min="0.001"
                    step="0.001"
                    style={{
                        ...styles.betInput,
                        ...(inputFocused ? styles.betInputFocus : {})
                    }}
                    placeholder="100"
                />
            </div>

            {/* Bet Calculator */}
            <div style={styles.betCalculator}>
                <div style={styles.betCalculatorTitle}>Potential Winnings</div>
                <div style={styles.betCalculatorRow}>
                    <span style={styles.betCalculatorLabel}>Bet on YES:</span>
                    <span style={{ ...styles.betCalculatorValue, ...styles.yesWinnings }}>
                        {yesWinnings > 0 ? `${yesWinnings.toFixed(2)} USDT` : 'N/A'}
                    </span>
                </div>
                <div style={styles.betCalculatorRow}>
                    <span style={styles.betCalculatorLabel}>Bet on NO:</span>
                    <span style={{ ...styles.betCalculatorValue, ...styles.noWinnings }}>
                        {noWinnings > 0 ? `${noWinnings.toFixed(2)} USDT` : 'N/A'}
                    </span>
                </div>
            </div>

            {/* Voting Section */}
            <div style={styles.votingSection}>
                <div style={styles.voteOption}>
                    <button
                        style={{
                            ...styles.voteButton,
                            ...styles.yesButton,
                            ...(!account ? styles.disabledButton : {})
                        }}
                        onClick={() => vote('YES')}
                        disabled={!account}
                        className="vote-button"
                    >
                        YES ({yesProb}%)
                    </button>
                </div>

                <div style={styles.voteOption}>
                    <button
                        style={{
                            ...styles.voteButton,
                            ...styles.noButton,
                            ...(!account ? styles.disabledButton : {})
                        }}
                        onClick={() => vote('NO')}
                        disabled={!account}
                        className="vote-button"
                    >
                        NO ({noProb}%)
                    </button>
                </div>
            </div>

            {/* Wallet Connection */}
            <div style={styles.walletSection}>
                {!account && (
                    <button style={styles.connectButton} onClick={connectWallet}>
                        🔗 Connect Wallet
                    </button>
                )}

                {/* Status Message */}
                {status && (
                    <div style={styles.statusMessage}>
                        {status}
                    </div>
                )}
            </div>
        </div>
    );
}
