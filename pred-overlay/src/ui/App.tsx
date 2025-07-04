import React, { useState } from 'react';

// Helper to extract the title from the tweet text (removes the market link)
function extractTitle(tweet: string, marketDomain: string) {
    // Remove the first matching market link from the tweet text
    const regex = new RegExp(`(?:https?://)?${marketDomain.replace('.', '\\.')}/m/[\\w-]+`, 'i');
    return tweet.replace(regex, '').trim();
}

export function App({ tweet, marketId }: { tweet: string; marketId: string }) {
    const [status, setStatus] = useState('');
    // Placeholder probabilities
    const yesProb = 62;
    const noProb = 38;
    const MARKET_DOMAIN = 'your.app'; // Keep in sync with content script
    const title = extractTitle(tweet, MARKET_DOMAIN) || 'Prediction Market';

    function vote(choice: 'YES' | 'NO') {
        setStatus(`You clicked ${choice}!`);
    }

    return (
        <div style={{
            width: '100%',
            background: 'rgba(15,23,42,0.97)',
            color: '#fff',
            borderRadius: '1rem',
            boxShadow: '0 4px 24px #000a',
            padding: '1.5rem 1.2rem 1.2rem 1.2rem',
            marginTop: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '1.2rem',
            position: 'relative',
            zIndex: 10,
        }}>
            <div style={{ fontWeight: 700, fontSize: '1.25rem', textAlign: 'center', letterSpacing: '-0.5px', lineHeight: 1.2, marginBottom: '.5rem' }}>
                {title}
            </div>
            <div style={{ display: 'flex', gap: '2.5rem', alignItems: 'flex-end' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#38bdf8', marginBottom: '.3rem' }}>{yesProb}%</div>
                    <button
                        style={{
                            padding: '0.8rem 2.2rem',
                            borderRadius: '2rem',
                            background: '#3b82f6',
                            color: '#fff',
                            fontWeight: 600,
                            fontSize: '1.1rem',
                            border: 'none',
                            cursor: 'pointer',
                            boxShadow: '0 2px 8px #0003',
                            transition: 'transform 0.1s',
                        }}
                        onClick={() => vote('YES')}
                    >
                        YES
                    </button>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f87171', marginBottom: '.3rem' }}>{noProb}%</div>
                    <button
                        style={{
                            padding: '0.8rem 2.2rem',
                            borderRadius: '2rem',
                            background: '#ef4444',
                            color: '#fff',
                            fontWeight: 600,
                            fontSize: '1.1rem',
                            border: 'none',
                            cursor: 'pointer',
                            boxShadow: '0 2px 8px #0003',
                            transition: 'transform 0.1s',
                        }}
                        onClick={() => vote('NO')}
                    >
                        NO
                    </button>
                </div>
            </div>
            <div style={{ fontSize: '1rem', minHeight: '1.5em', opacity: 0.85, textAlign: 'center' }}>
                {status || 'Choose YES or NO to vote.'}
            </div>
        </div>
    );
}
