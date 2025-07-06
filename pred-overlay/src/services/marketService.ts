// Market service for AI integration and on-chain data reading

// Chrome extension types
declare global {
    interface Window {
        chrome: {
            runtime: {
                sendMessage: (message: any, callback: (response: any) => void) => void;
            };
        };
    }
}

export interface MarketValidation {
    is_valid: boolean;
    confidence: number;
    reasoning: string;
    yes_probability: number;
    no_probability: number;
    reliable_sources: string[];
    resolution_date: string;
    auto_expire: boolean;
}

export interface MarketData {
    id: string;
    title: string;
    description: string;
    prompt: string;
    close_time_iso: string;
    outcomes: string[];
    initial_prob: number;
    validation: MarketValidation;
    created_at: string;
    status: string;
}

export interface MarketResponse {
    success: boolean;
    market?: MarketData;
    error?: string;
}

export interface OnChainMarketData {
    hashedMarketId: string;
    yes: string;
    no: string;
    yesPrice: bigint;
    noPrice: bigint;
    pool: string;
    outcome: bigint;
}

import config from '../config/config';
import { flareTestnet } from 'viem/chains';
import { createPublicClient, createWalletClient, getAddress, http, keccak256, toBytes } from 'viem'
import { privateKeyToAccount } from 'viem/accounts';

export class MarketService {
    private static instance: MarketService;
    private marketCache: Map<string, MarketResponse> = new Map(); // AI validation results
    private titleToMarketCache: Map<string, string> = new Map(); // Cache title to marketId
    private invalidMarketCache: Map<string, MarketResponse> = new Map(); // Cache invalid markets
    private onChainCache: Map<string, OnChainMarketData> = new Map(); // On-chain data cache

    static getInstance(): MarketService {
        if (!MarketService.instance) {
            MarketService.instance = new MarketService();
            console.log('[MarketService] New instance created');
        } else {
            console.log('[MarketService] Using existing instance');
        }
        return MarketService.instance;
    }

    constructor() {
        // Load cache from localStorage on initialization
        this.loadCacheFromStorage();
    }

    private loadCacheFromStorage() {
        try {
            const cached = localStorage.getItem('prediction-market-cache');
            console.log('[MarketService] localStorage raw data:', cached);

            if (cached) {
                const data = JSON.parse(cached);
                console.log('[MarketService] Parsed localStorage data:', data);

                this.marketCache = new Map(Object.entries(data.marketCache || {}));
                this.titleToMarketCache = new Map(Object.entries(data.titleToMarketCache || {}));
                this.invalidMarketCache = new Map(Object.entries(data.invalidMarketCache || {}));
                console.log('[MarketService] Loaded cache from localStorage:', this.getCacheStats());
            } else {
                console.log('[MarketService] No cache found in localStorage');
            }
        } catch (error) {
            console.error('[MarketService] Error loading cache from localStorage:', error);
        }
    }

    private saveCacheToStorage() {
        try {
            const data = {
                marketCache: Object.fromEntries(this.marketCache),
                titleToMarketCache: Object.fromEntries(this.titleToMarketCache),
                invalidMarketCache: Object.fromEntries(this.invalidMarketCache)
            };
            localStorage.setItem('prediction-market-cache', JSON.stringify(data));
        } catch (error) {
            console.error('[MarketService] Error saving cache to localStorage:', error);
        }
    }

    /**
     * Validate a market using AI (happens once per market)
     * This determines if the market is valid and gets initial probabilities
     * Later this will be replaced by on-chain validation
     */
    async validateMarket(prompt: string, marketId: string): Promise<MarketResponse> {
        console.log(`[MarketService] validateMarket called with prompt: "${prompt}", marketId: "${marketId}"`);

        // Check cache first - if we've already validated this market, return cached result
        if (this.marketCache.has(marketId)) {
            const cached = this.marketCache.get(marketId)!;
            console.log(`[MarketService] Using cached validation for market ID: ${marketId}`);
            return cached;
        }

        // Check if we've already validated this exact prompt with a different marketId
        if (this.titleToMarketCache.has(prompt)) {
            const cachedId = this.titleToMarketCache.get(prompt)!;
            console.log(`[MarketService] Found existing validation for prompt, using ID: ${cachedId}`);
            if (this.marketCache.has(cachedId)) {
                const cached = this.marketCache.get(cachedId)!;
                // Update the cache to use the new marketId as the key
                this.marketCache.set(marketId, cached);
                this.titleToMarketCache.set(prompt, marketId);
                console.log(`[MarketService] Updated cache to use new marketId: ${marketId}`);
                return cached;
            }
        }

        // Check invalid cache
        if (this.invalidMarketCache.has(prompt)) {
            console.log(`[MarketService] Using cached invalid result for prompt: "${prompt}"`);
            return this.invalidMarketCache.get(prompt)!;
        }

        console.log(`[MarketService] No cache hit, calling AI generator for marketId: ${marketId}`);

        try {
            // Use background script to make the request (avoids content script blocking)
            const response = await new Promise<{ success: boolean; data?: any; error?: string }>((resolve) => {
                window.chrome.runtime.sendMessage({
                    type: 'AI_GENERATOR_REQUEST',
                    payload: {
                        prompt: prompt,
                        market_id: marketId
                    }
                }, (response: { success: boolean; data?: any; error?: string }) => {
                    resolve(response);
                });
            });

            if (!response.success) {
                throw new Error(response.error || 'Background script request failed');
            }

            const data = response.data;
            console.log(`[MarketService] AI generator response:`, data);

            const result: MarketResponse = {
                success: data.success || false,
                market: data.market || undefined,
                error: data.error || undefined
            };

            // Cache the validation result
            if (result.success && result.market) {
                this.marketCache.set(marketId, result);
                this.titleToMarketCache.set(prompt, marketId);
                console.log(`[MarketService] Cached valid market validation with ID: ${marketId}`);
            } else {
                this.invalidMarketCache.set(prompt, result);
                console.log(`[MarketService] Cached invalid market validation for prompt: "${prompt}"`);
            }

            this.saveCacheToStorage(); // Save cache after each validation
            return result;

        } catch (error) {
            console.error('[MarketService] Error calling AI generator:', error);

            // Check if it's a connection error
            const errorMessage = error instanceof Error ? error.message : String(error);
            if (errorMessage.includes('Failed to fetch') || errorMessage.includes('NetworkError') || errorMessage.includes('Cannot connect to AI generator')) {
                console.log(`[MarketService] AI generator connection error, returning fallback response`);
                return {
                    success: false,
                    market: undefined,
                    error: 'Cannot connect to AI generator - showing fallback data'
                };
            }

            const result: MarketResponse = {
                success: false,
                market: undefined,
                error: errorMessage
            };

            // Cache the error result
            this.invalidMarketCache.set(prompt, result);
            this.saveCacheToStorage(); // Save cache after each validation
            return result;
        }
    }

    /**
     * Read on-chain market data (simulated for now)
     * This would connect to the actual smart contract
     * TODO: Replace with actual smart contract calls
     */
    async getOnChainData(marketId: string): Promise<OnChainMarketData | null> {
        // Check on-chain cache first
        if (this.onChainCache.has(marketId)) {
            const cached = this.onChainCache.get(marketId)!;
            console.log(`[MarketService] Using cached on-chain data for market ID: ${marketId}`);
            return cached;
        }

        try {
            // TODO: Replace with actual smart contract calls
            // For now, simulate on-chain data reading based on AI validation
            const marketData = await this.getMarketData(marketId);

            if (!marketData) {
                console.log(`[MarketService] No market data found for on-chain reading: ${marketId}`);
                return null;
            }

            // Simulate on-chain data based on AI validation
            if (!marketData.validation.is_valid) {
                // Invalid market - no on-chain data
                console.log(`[MarketService] Market invalid according to AI, no on-chain data: ${marketId}`);
                return null;
            }

            const publicClient = createPublicClient({
                chain: flareTestnet,
                transport: http()
            });

            const hashedMarketId = keccak256(toBytes(marketId));

            const market = await publicClient.readContract({
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
                functionName: 'getMarket',
                args: [hashedMarketId]
            });

            return {
                hashedMarketId,
                yes: market[0],
                no: market[1],
                yesPrice: market[2],
                noPrice: market[3],
                pool: market[4],
                outcome: market[5]
            };
        } catch (error) {
            console.error('[MarketService] Error reading on-chain data:', error);
            return null;
        }
    }

    /**
     * Get market data from cache or AI generator
     */
    async getMarketData(marketId: string): Promise<MarketData | null> {
        console.log(`[MarketService] getMarketData called for market ID: ${marketId}`);
        console.log(`[MarketService] Cache stats:`, this.getCacheStats());

        // Check cache first - this should have the market data from validation
        if (this.marketCache.has(marketId)) {
            const cached = this.marketCache.get(marketId)!;
            console.log(`[MarketService] Found market in cache for ID: ${marketId}`);
            if (cached.success && cached.market) {
                return cached.market;
            }
        }

        console.log(`[MarketService] Market not found in cache, trying AI generator for ID: ${marketId}`);

        // Try to fetch from AI generator via background script
        try {
            const response = await new Promise<{ success: boolean; data?: any; error?: string }>((resolve) => {
                window.chrome.runtime.sendMessage({
                    type: 'AI_GENERATOR_REQUEST',
                    payload: {
                        method: 'GET',
                        url: `/markets/${marketId}`
                    }
                }, (response: { success: boolean; data?: any; error?: string }) => {
                    resolve(response);
                });
            });

            if (response.success && response.data) {
                console.log(`[MarketService] Found market via AI generator for ID: ${marketId}`);
                const marketData: MarketData = response.data;
                const marketResponse: MarketResponse = {
                    success: true,
                    market: marketData
                };
                this.marketCache.set(marketId, marketResponse);
                this.saveCacheToStorage(); // Save cache after fetching
                return marketData;
            } else {
                console.log(`[MarketService] Market not found via AI generator for ID: ${marketId}`);
            }
        } catch (error) {
            console.error('Error fetching market data:', error);
        }

        return null;
    }

    /**
     * Check if a market is valid (exists on-chain)
     */
    async isMarketValid(marketId: string): Promise<boolean> {
        const onChainData = await this.getOnChainData(marketId);
        return onChainData !== null;
    }

    /**
     * Clear cache for a specific market
     */
    clearCache(marketId?: string) {
        if (marketId) {
            this.marketCache.delete(marketId);
            this.onChainCache.delete(marketId);
        } else {
            this.marketCache.clear();
            this.onChainCache.clear();
            this.titleToMarketCache.clear();
            this.invalidMarketCache.clear();
        }
        this.saveCacheToStorage(); // Save cache after clearing
    }

    /**
     * Get market outcome (true, false, or undefined)
     */
    async getMarketOutcome(marketId: string): Promise<{ outcome: number; status: string }> {
        try {
            const response = await new Promise<{ success: boolean; data?: any; error?: string }>((resolve) => {
                window.chrome.runtime.sendMessage({
                    type: 'AI_GENERATOR_REQUEST',
                    payload: {
                        method: 'GET',
                        url: `/markets/${marketId}/outcome`
                    }
                }, (response: { success: boolean; data?: any; error?: string }) => {
                    resolve(response);
                });
            });

            if (response.success && response.data) {
                return response.data;
            } else {
                return { outcome: 2, status: 'error' };
            }
        } catch (error) {
            console.error('Error getting market outcome:', error);
            return { outcome: 2, status: 'error' };
        }
    }

    async resolveMarket(marketId: string) {
        try {
            const { outcome } = await this.getMarketOutcome(marketId);
            if (outcome !== 2) {
                const marketData = await this.getMarketData(marketId);
                if (!marketData) {
                    throw new Error('Failed to get market data');
                }

                const abiEncodedRequest = await this.prepareFDCRequest(`${config.AI_GENERATOR_URL}/resolver/resolutions/${marketId}/outcome`);
                if (!abiEncodedRequest) {
                    throw new Error('Failed to prepare FDC request');
                }

                const publicClient = createPublicClient({
                    chain: flareTestnet,
                    transport: http()
                });

                const requestFee = await publicClient.readContract({
                    address: getAddress(config.ADDRESSES.FDC_FEE_CONFIG),
                    abi: [
                        {
                            "inputs": [
                                {
                                    "internalType": "bytes",
                                    "name": "_data",
                                    "type": "bytes"
                                }
                            ],
                            "name": "getRequestFee",
                            "outputs": [
                                {
                                    "internalType": "uint256",
                                    "name": "_fee",
                                    "type": "uint256"
                                }
                            ],
                            "stateMutability": "view",
                            "type": "function"
                        },
                    ],
                    functionName: 'getRequestFee',
                    args: [abiEncodedRequest as `0x${string}`]
                });

                console.log(`[MarketService] Request fee: ${requestFee}`);

                const account = privateKeyToAccount(config.ADMIN.PRIVATE_KEY as `0x${string}`);
                const adminClient = createWalletClient({
                    account,
                    chain: flareTestnet,
                    transport: http()
                });

                const attestationTx = await adminClient.writeContract({
                    address: getAddress(config.ADDRESSES.FDC_HUB),
                    abi: [{
                        "inputs": [
                            {
                                "internalType": "bytes",
                                "name": "_data",
                                "type": "bytes"
                            }
                        ],
                        "name": "requestAttestation",
                        "outputs": [],
                        "stateMutability": "payable",
                        "type": "function"
                    }],
                    functionName: 'requestAttestation',
                    args: [abiEncodedRequest as `0x${string}`],
                    value: requestFee
                });

                const attestationReceipt = await publicClient.waitForTransactionReceipt({
                    hash: attestationTx
                });

                const blockNumber = attestationReceipt.blockNumber;
                const block = await publicClient.getBlock({
                    blockNumber: blockNumber
                });

                const votingRoundId = (BigInt(block.timestamp) - 1658430000n) / 90n;
                console.log(`[MarketService] Voting round ID: ${votingRoundId}`);

                let proof: any | undefined;
                for (let i = 0; i < 10; i++) {
                    proof = await this.getFDCProof(votingRoundId, abiEncodedRequest);
                    if (proof) {
                        break;
                    }
                    await new Promise(resolve => setTimeout(resolve, 15000));
                    console.log(`[MarketService] Waiting for FDC proof... ${i + 1}/10`);
                }
                if (!proof) {
                    throw new Error('Failed to get FDC proof');
                }

                console.log(`[MarketService] FDC proof:`, proof);
            }
        } catch (error) {
            console.error('Error resolving market:', error);
            return { success: false, error: 'Error resolving market' };
        }
    }

    async prepareFDCRequest(url: string): Promise<string | undefined> {
        try {
            console.log(`[MarketService] Preparing FDC request for URL: ${url}`);

            const response = await fetch("https://jq-verifier-test.flare.rocks/JsonApi/prepareRequest", {
                method: "POST",
                headers: {
                    "X-API-KEY": "flare-oxford-2025",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "attestationType": "0x494a736f6e417069000000000000000000000000000000000000000000000000",
                    "sourceId": "0x5745423200000000000000000000000000000000000000000000000000000000",
                    "requestBody": {
                        "url": url,
                        "postprocessJq": ".",
                        "abi_signature": "{\"components\": [{\"internalType\": \"uint256\",\"name\": \"outcome\",\"type\": \"uint256\"}],\"name\": \"task\",\"type\": \"tuple\"}"
                    }
                })
            });

            if (!response.ok) {
                throw new Error('Failed to prepare FDC request');
            }

            const data = await response.json();
            console.log(`[MarketService] FDC request response:`, data);
            if (data.status != "VALID") {
                throw new Error('FDC request returned invalid status');
            }

            const abiEncodedRequest = data.abiEncodedRequest;
            if (!abiEncodedRequest) {
                throw new Error('FDC request returned invalid ABI encoded request');
            }

            return abiEncodedRequest;
        } catch (error) {
            console.error('Error preparing FDC request:', error);
            return undefined;
        }
    }

    async getFDCProof(votingRoundId: bigint, abiEncodedRequest: string): Promise<any | undefined> {
        try {
            const response = await fetch(`https://ctn2-data-availability.flare.network/api/v1/fdc/proof-by-request-round`, {
                method: "POST",
                headers: {
                    "X-API-KEY": "flare-oxford-2025",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "votingRoundId": votingRoundId.toString(),
                    "requestBytes": abiEncodedRequest
                })
            });

            if (!response.ok) {
                throw new Error('Failed to get FDC proof');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error getting FDC proof:', error);
            return undefined;
        }
    }

    /**
     * Get cache statistics for debugging
     */
    getCacheStats() {
        return {
            marketCacheSize: this.marketCache.size,
            titleCacheSize: this.titleToMarketCache.size,
            invalidCacheSize: this.invalidMarketCache.size,
            onChainCacheSize: this.onChainCache.size
        };
    }
}

export default MarketService.getInstance(); 