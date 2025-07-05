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
    marketId: string;
    yesProbability: number;
    noProbability: number;
    totalVolume: number;
    yesVolume: number;
    noVolume: number;
    isActive: boolean;
    isResolved: boolean;
    outcome?: 'YES' | 'NO';
}

import config from '../config/config';

// AI Generator API configuration
const AI_GENERATOR_URL = config.AI_GENERATOR_URL;

export class MarketService {
    private static instance: MarketService;
    private marketCache: Map<string, MarketResponse> = new Map(); // AI validation results
    private titleToMarketCache: Map<string, string> = new Map(); // Cache title to marketId
    private invalidMarketCache: Map<string, MarketResponse> = new Map(); // Cache invalid markets
    private onChainCache: Map<string, OnChainMarketData> = new Map(); // On-chain data cache

    static getInstance(): MarketService {
        if (!MarketService.instance) {
            MarketService.instance = new MarketService();
        }
        return MarketService.instance;
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

            this.getCacheStats();
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
            this.getCacheStats();
            return result;
        }
    }

    /**
     * Get real-time market probabilities from on-chain data
     * This is called frequently to update the UI with current probabilities
     * Later this will read from actual smart contracts
     */
    async getMarketProbabilities(marketId: string): Promise<{ yesProb: number; noProb: number; isValid: boolean }> {
        console.log(`[MarketService] Getting on-chain probabilities for market ID: ${marketId}`);

        const onChainData = await this.getOnChainData(marketId);

        if (!onChainData || !onChainData.isActive) {
            console.log(`[MarketService] No active on-chain data for market ID: ${marketId}`);
            return { yesProb: 0, noProb: 0, isValid: false };
        }

        console.log(`[MarketService] On-chain probabilities - YES: ${onChainData.yesProbability}%, NO: ${onChainData.noProbability}%`);
        return {
            yesProb: onChainData.yesProbability,
            noProb: onChainData.noProbability,
            isValid: true
        };
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
                return {
                    marketId,
                    yesProbability: 0,
                    noProbability: 0,
                    totalVolume: 0,
                    yesVolume: 0,
                    noVolume: 0,
                    isActive: false,
                    isResolved: false
                };
            }

            // Valid market - simulate real-time probabilities
            const baseYesProb = marketData.validation.yes_probability * 100;
            const baseNoProb = marketData.validation.no_probability * 100;

            // Add some volatility to simulate trading
            const volatility = 5; // ±5%
            const yesProb = Math.max(0, Math.min(100, baseYesProb + (Math.random() - 0.5) * volatility));
            const noProb = Math.max(0, Math.min(100, baseNoProb + (Math.random() - 0.5) * volatility));

            // Normalize to 100%
            const total = yesProb + noProb;
            const normalizedYes = (yesProb / total) * 100;
            const normalizedNo = (noProb / total) * 100;

            const onChainData: OnChainMarketData = {
                marketId,
                yesProbability: Math.round(normalizedYes * 10) / 10, // Round to 1 decimal
                noProbability: Math.round(normalizedNo * 10) / 10,
                totalVolume: Math.floor(Math.random() * 10000) + 1000, // Random volume
                yesVolume: Math.floor(Math.random() * 5000) + 500,
                noVolume: Math.floor(Math.random() * 5000) + 500,
                isActive: true,
                isResolved: false
            };

            // Cache the on-chain data
            this.onChainCache.set(marketId, onChainData);
            console.log(`[MarketService] Cached on-chain data for market ID: ${marketId}`);

            return onChainData;
        } catch (error) {
            console.error('[MarketService] Error reading on-chain data:', error);
            return null;
        }
    }

    /**
     * Get market data from cache or AI generator
     */
    async getMarketData(marketId: string): Promise<MarketData | null> {
        // Check cache first
        if (this.marketCache.has(marketId)) {
            const cached = this.marketCache.get(marketId)!;
            return cached.success && cached.market ? cached.market : null;
        }

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
                const marketData: MarketData = response.data;
                const marketResponse: MarketResponse = {
                    success: true,
                    market: marketData
                };
                this.marketCache.set(marketId, marketResponse);
                return marketData;
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
        return onChainData?.isActive || false;
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
    }

    /**
     * Get market outcome (true, false, or undefined)
     */
    async getMarketOutcome(marketId: string): Promise<{ outcome: 'true' | 'false' | 'undefined'; status: string }> {
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
                return { outcome: 'undefined', status: 'error' };
            }
        } catch (error) {
            console.error('Error getting market outcome:', error);
            return { outcome: 'undefined', status: 'error' };
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