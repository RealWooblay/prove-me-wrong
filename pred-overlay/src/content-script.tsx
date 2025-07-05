import React from 'react';
import { createRoot } from 'react-dom/client';
import config from './config/config';

console.log('[PredictionOverlay] content script loaded…');

// Inject the in-page proxy script to handle wallet requests
const script = document.createElement('script');
script.src = (window.chrome as any).runtime.getURL('inpage-proxy.js');
(document.head || document.documentElement).appendChild(script);

// Configurable domain constant
const MARKET_DOMAIN = config.MARKET_DOMAIN;
const MARKET_LINK_REGEX = new RegExp(
    '(?:https?://)?' + MARKET_DOMAIN.replace('.', '\\.') + '/m/([\\w-]+)',
    'i'
);

// Extract market slug from any Twitter link element
function extractSlug(link: HTMLAnchorElement): string | null {
    // Try multiple sources for the URL
    const urlSources = [
        link.href, // Full URL
        link.getAttribute('data-expanded-url'), // Twitter's expanded URL
        link.getAttribute('title'), // Title attribute
        link.getAttribute('href'), // Href attribute
        link.innerText // Visible text
    ];

    for (const source of urlSources) {
        if (!source) continue;

        // Try the configured domain regex first
        let m = source.match(MARKET_LINK_REGEX);
        if (m) {
            console.log(`[PredictionOverlay] Extracted slug "${m[1]}" from source: ${source}`);
            return m[1];
        }

        // Fallback: try to extract from any URL that contains /m/
        const fallbackMatch = source.match(/\/m\/([\\w-]+)/);
        if (fallbackMatch) {
            console.log(`[PredictionOverlay] Extracted slug "${fallbackMatch[1]}" from fallback: ${source}`);
            return fallbackMatch[1];
        }
    }

    console.log(`[PredictionOverlay] Failed to extract slug from link:`, link);
    return null;
}



// Extract Twitter username from the tweet
function getTwitterUsername(anchor: HTMLAnchorElement): string | null {
    // Strategy 1: Look for username in the tweet container
    const container = anchor.closest('article') || anchor.closest('[data-testid="tweet"]');
    if (!container) return null;

    // Look for username in various places
    const usernameSelectors = [
        'a[href^="/"]', // Links that start with / (relative URLs)
        '[data-testid="User-Name"] a', // Twitter's user name element
        'a[href*="/status/"]', // Status links (extract username from path)
        'a[href*="/i/status/"]' // New Twitter status links
    ];

    for (const selector of usernameSelectors) {
        const elements = container.querySelectorAll(selector);
        for (const element of elements) {
            const href = (element as HTMLAnchorElement).href || element.getAttribute('href') || '';

            // Extract username from various URL patterns
            const patterns = [
                /^https?:\/\/(?:www\.)?(?:twitter\.com|x\.com)\/([^\/]+)/, // @username
                /^\/([^\/]+)/, // /username
                /^\/([^\/]+)\/status\//, // /username/status/
                /^\/([^\/]+)\/i\/status\// // /username/i/status/
            ];

            for (const pattern of patterns) {
                const match = href.match(pattern);
                if (match && match[1] && !match[1].includes('status') && match[1].length > 0) {
                    return match[1].toLowerCase(); // Normalize to lowercase
                }
            }
        }
    }

    // Strategy 2: Look for username in text content
    const textContent = container.textContent || '';
    const usernameMatch = textContent.match(/@([a-zA-Z0-9_]+)/);
    if (usernameMatch) {
        return usernameMatch[1].toLowerCase();
    }

    return null;
}

// Extract tweet ID as fallback
function getTweetId(anchor: HTMLAnchorElement): string | null {
    // Look for tweet ID in data attributes
    const container = anchor.closest('article') || anchor.closest('[data-testid="tweet"]');
    if (container) {
        const tweetId = container.getAttribute('data-tweet-id');
        if (tweetId) {
            return tweetId;
        }
    }

    // Look for status links
    const statusLink = anchor.closest('article')?.querySelector('a[href*="/status/"]') as HTMLAnchorElement;
    if (statusLink) {
        const href = statusLink.href || statusLink.getAttribute('href') || '';
        const tweetIdMatch = href.match(/\/status\/(\d+)/);
        if (tweetIdMatch) {
            return tweetIdMatch[1];
        }
    }

    return null;
}



// Extracts the title text that follows the anchor (up to the first line break)
function extractTitleFromAnchor(anchor: HTMLAnchorElement): string {
    let title = '';
    let node = anchor.nextSibling;
    while (node) {
        if (node.nodeType === Node.TEXT_NODE) {
            const txt = (node as Text).textContent || '';
            if (txt.includes('\n')) {
                title += txt.split('\n')[0];
                break;
            }
            title += txt;
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            const el = node as HTMLElement;
            // Only include inline elements
            const inlineTags = ['SPAN', 'B', 'I', 'EM', 'STRONG', 'A', 'SMALL', 'U', 'MARK', 'CODE'];
            if (inlineTags.includes(el.tagName)) {
                const inner = el.innerText || '';
                if (inner.includes('\n')) {
                    title += inner.split('\n')[0];
                    break;
                }
                title += inner;
            } else {
                break; // Stop at block elements
            }
        } else {
            break;
        }
        node = node.nextSibling;
    }
    return title.trim();
}

function injectOverlay(anchor: HTMLAnchorElement, marketId: string) {
    // Check if we've already injected an overlay for this market ID anywhere on the page
    const existingOverlay = document.querySelector(`[data-market-id="${marketId}"]`);
    if (existingOverlay) {
        console.log(`[PredictionOverlay] Overlay already exists for market ID: ${marketId}, skipping injection`);
        return;
    }

    // Check if we've already processed this exact anchor
    if (anchor.dataset.overlayInjected === 'yes') {
        console.log(`[PredictionOverlay] Anchor already processed: ${anchor.href}, skipping`);
        return;
    }

    console.log(`[PredictionOverlay] Injecting overlay for market ID: ${marketId}`);

    // Extract the title from the text node and inline elements after the anchor
    const title = extractTitleFromAnchor(anchor) || 'Prediction Market';

    // Collect all nodes to remove: the anchor and all adjacent inline title nodes
    const nodesToRemove: Node[] = [anchor];
    let node = anchor.nextSibling;
    const inlineTags = ['SPAN', 'B', 'I', 'EM', 'STRONG', 'A', 'SMALL', 'U', 'MARK', 'CODE'];
    let foundLineBreak = false;
    while (node && !foundLineBreak) {
        let shouldRemove = false;
        if (node.nodeType === Node.TEXT_NODE) {
            const txt = (node as Text).textContent || '';
            if (txt.match(/^\\s*$/)) {
                // Remove whitespace-only nodes
                shouldRemove = true;
            } else if (txt.includes('\n')) {
                shouldRemove = true;
                foundLineBreak = true;
            } else {
                shouldRemove = true;
            }
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            const el = node as HTMLElement;
            if (inlineTags.includes(el.tagName)) {
                const inner = el.innerText || '';
                shouldRemove = true;
                if (inner.includes('\n')) foundLineBreak = true;
            } else {
                break;
            }
        } else {
            break;
        }
        if (shouldRemove) {
            nodesToRemove.push(node);
        }
        node = node.nextSibling;
    }

    // Insert overlay host before the first node to remove
    const host = document.createElement('span');
    host.className = 'pred-overlay-root';
    host.setAttribute('data-market-id', marketId); // Add market ID for duplicate detection
    host.style.display = 'inline-block';
    host.style.verticalAlign = 'middle';
    host.style.margin = '0 0.25rem';
    host.style.maxWidth = '100%';
    nodesToRemove[0].parentNode?.insertBefore(host, nodesToRemove[0]);

    // Remove all nodes (link and title)
    nodesToRemove.forEach(n => n.parentNode?.removeChild(n));

    // Shadow DOM
    const shadow = host.attachShadow({ mode: 'open' });
    const mount = document.createElement('div');
    shadow.appendChild(mount);
    const style = document.createElement('link');
    style.rel = 'stylesheet';
    style.href = (window.chrome as any).runtime.getURL('overlay.css');
    shadow.appendChild(style);
    import('./ui/App').then(({ App }) => {
        createRoot(mount).render(
            <React.StrictMode>
                <App marketId={marketId} title={title} />
            </React.StrictMode>
        );
    });

    // Mark both the anchor and the host as processed
    anchor.dataset.overlayInjected = 'yes';
    host.dataset.overlayInjected = 'yes';

    console.log(`[PredictionOverlay] Successfully injected overlay for market ID: ${marketId}`);
}

function scanTweets() {
    document.querySelectorAll<HTMLElement>('article').forEach(article => {
        // Debug: log all links in the article
        const allLinks = article.querySelectorAll<HTMLAnchorElement>('a');
        console.log(`[PredictionOverlay] Found ${allLinks.length} total links in article`);
        allLinks.forEach((link, index) => {
            console.log(`[PredictionOverlay] Link ${index}: ${link.href}`);
        });

        // Look for market links including t.co redirects
        const marketLinks = article.querySelectorAll<HTMLAnchorElement>('a[href*="your.app"], a[href*="prove-me-wrong.com"], a[href*="/m/"], a[href*="t.co"]');
        console.log(`[PredictionOverlay] Found ${marketLinks.length} potential market links (including t.co)`);

        marketLinks.forEach(async (anchor) => {
            // Skip if we've already handled this link
            if (anchor.dataset.overlayInjected === 'yes') return;

            // Check if this is a t.co link that might redirect to a market
            let actualUrl = anchor.href;
            if (anchor.href.includes('t.co')) {
                console.log(`[PredictionOverlay] Found t.co link: ${anchor.href}`);
                // For now, let's assume t.co links could be markets and process them
                // In a real implementation, you'd follow the redirect
            }

            // Check if this URL contains market indicators
            const isMarketLink = actualUrl.includes('your.app') ||
                actualUrl.includes('prove-me-wrong.com') ||
                actualUrl.includes('/m/') ||
                actualUrl.includes('t.co'); // Assume t.co could be market links

            if (!isMarketLink) {
                console.log(`[PredictionOverlay] Not a market link: ${actualUrl}`);
                return;
            }

            // Extract the title first
            const title = extractTitleFromAnchor(anchor) || 'Prediction Market';
            if (!title || title === 'Prediction Market') {
                console.log(`[PredictionOverlay] No valid title found for link: ${actualUrl}`);
                return;
            }

            const username = getTwitterUsername(anchor);
            if (!username) {
                console.log(`[PredictionOverlay] No username found for link: ${actualUrl}`);
                return;
            }

            // Generate market ID based on title + username
            const marketId = generateMarketIdFromTitle(title, username);
            console.log(`[PredictionOverlay] Title: "${title}", Username: ${username}, Market ID: ${marketId}`);

            injectOverlay(anchor, marketId);
        });
    });
}

// Generate market ID from title and username
function generateMarketIdFromTitle(title: string, username: string): string {
    // Convert title to a URL-friendly slug
    const titleSlug = title
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '') // Remove special characters
        .replace(/\s+/g, '-') // Replace spaces with hyphens
        .replace(/-+/g, '-') // Replace multiple hyphens with single
        .trim()
        .replace(/^-+|-+$/g, ''); // Remove leading/trailing hyphens

    return `${titleSlug}-by-${username}`;
}

// Prevent multiple initializations
if (document.body.dataset.overlayInitialized === 'yes') {
    console.log('[PredictionOverlay] Overlay system already initialized, skipping');
} else {
    console.log('[PredictionOverlay] Initializing overlay system...');
    document.body.dataset.overlayInitialized = 'yes';

    const observer = new MutationObserver(scanTweets);
    observer.observe(document.body, { childList: true, subtree: true });
    scanTweets();
}