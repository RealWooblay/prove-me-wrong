import React, { useState } from 'react';

export function App({ marketId, title }: { marketId: string; title: string }) {
    const [status, setStatus] = useState('');
    const yesProb = 62;
    const noProb = 38;

    function vote(choice: 'YES' | 'NO') {
        setStatus(`You clicked ${choice}!`);
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
                        }}
                        onClick={() => vote('YES')}
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
                        }}
                        onClick={() => vote('NO')}
                    >
                        NO
                    </button>
                </div>
            </div>
            <div style={{ fontSize: '0.95em', minHeight: '1.2em', opacity: 0.85, textAlign: 'center', marginTop: '.5em' }}>
                {status || 'Choose YES or NO to vote.'}
            </div>
        </span>
    );
}
