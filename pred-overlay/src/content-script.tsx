import React from 'react';
import { createRoot } from 'react-dom/client';

console.log('[PredictionOverlay] content script loaded…');

// Inject the in-page proxy script to handle wallet requests
const script = document.createElement('script');
script.src = chrome.runtime.getURL('inpage-proxy.js');
(document.head || document.documentElement).appendChild(script);

// Configurable domain constant
const MARKET_DOMAIN = 'your.app'; // <-- change to your real domain!
const MARKET_LINK_REGEX = new RegExp(
    '(?:https?://)?' + MARKET_DOMAIN.replace('.', '\\.') + '/m/([\\w-]+)',
    'i'
);

// Extract market slug from any Twitter link element
function extractSlug(link: HTMLAnchorElement): string | null {
    const expanded =
        link.getAttribute('data-expanded-url') ||
        link.getAttribute('title') ||
        link.getAttribute('href') ||
        '';
    let m = expanded.match(MARKET_LINK_REGEX);
    if (m) return m[1];
    // Fallback: check visible text (flattened)
    m = (link.innerText || '').match(MARKET_LINK_REGEX);
    if (m) return m[1];
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
    if (anchor.dataset.overlayInjected === 'yes') return;

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
    style.href = chrome.runtime.getURL('overlay.css');
    shadow.appendChild(style);
    import('./ui/App').then(({ App }) => {
        createRoot(mount).render(
            <React.StrictMode>
                <App marketId={marketId} title={title} />
            </React.StrictMode>
        );
    });
    host.dataset.overlayInjected = 'yes';
}

function scanTweets() {
    document.querySelectorAll<HTMLElement>('article').forEach(article => {
        article.querySelectorAll<HTMLAnchorElement>('a').forEach(anchor => {
            // Skip if we've already handled this link
            if (anchor.dataset.overlayInjected === 'yes') return;

            const slug = extractSlug(anchor);
            if (!slug) return;

            injectOverlay(anchor, slug);
        });
    });
}

const observer = new MutationObserver(scanTweets);
observer.observe(document.body, { childList: true, subtree: true });
scanTweets();