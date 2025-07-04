// content-script.tsx
import React from 'react';
import { createRoot } from 'react-dom/client';

console.log('[PredictionOverlay] content script loaded…');

// Configurable domain constant
const MARKET_DOMAIN = 'your.app'; // <-- change to your real domain!
const MARKET_LINK_REGEX = new RegExp(`(?:https?://)?${MARKET_DOMAIN.replace('.', '\\.')}\\/m\\/([\\w-]+)`, 'i');

// Extract market slug from any Twitter link element
function extractSlug(link: HTMLAnchorElement): string | null {
    const expanded =
        link.getAttribute('data-expanded-url') ||
        link.getAttribute('title') ||
        link.getAttribute('href') ||
        '';
    const m = expanded.match(MARKET_LINK_REGEX);
    return m ? m[1] : null;
}

// Fallback: scan the whole tweet text
function extractFromArticle(article: HTMLElement): string | null {
    const txt = article.innerText;
    const m = txt.match(MARKET_LINK_REGEX);
    return m ? m[1] : null;
}

function injectOverlay(tweetNode: HTMLElement, marketId: string) {
    console.log('[PredictionOverlay] injectOverlay called for marketId:', marketId, tweetNode);
    if (tweetNode.querySelector('.pred-overlay-root')) return;
    const shadowHost = document.createElement('div');
    shadowHost.className = 'pred-overlay-root';
    tweetNode.appendChild(shadowHost);
    const shadow = shadowHost.attachShadow({ mode: 'open' });
    const mount = document.createElement('div');
    shadow.appendChild(mount);
    const style = document.createElement('link');
    style.rel = 'stylesheet';
    style.href = chrome.runtime.getURL('overlay.css');
    shadow.appendChild(style);
    import('./ui/App').then(({ App }) => {
        createRoot(mount).render(
            <React.StrictMode>
                <App tweet={tweetNode.innerText} marketId={marketId} />
            </React.StrictMode>
        );
    });
}

function scanTweets() {
    document.querySelectorAll<HTMLElement>('article').forEach(article => {
        if (article.dataset.overlayApplied === 'true') return;

        let slug: string | null = null;

        // 1) look at every anchor
        article.querySelectorAll<HTMLAnchorElement>('a').forEach(link => {
            slug = slug || extractSlug(link);
        });

        // 2) fall back to the tweet text
        if (!slug) slug = extractFromArticle(article);

        if (slug) {
            console.log('[PredictionOverlay] injecting for slug', slug);
            injectOverlay(article, slug);
            article.dataset.overlayApplied = 'true';
        }
    });
}

const observer = new MutationObserver(scanTweets);
observer.observe(document.body, { childList: true, subtree: true });
scanTweets();
