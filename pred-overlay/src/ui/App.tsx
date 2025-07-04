import React, { useState } from 'react';

export function App({ tweet, marketId }: { tweet: string; marketId: string }) {
    const [status, setStatus] = useState('');

    function vote(choice: 'YES' | 'NO') {
        setStatus(`You clicked ${choice}!`);
    }

    return (
        <div className="p-4 bg-slate-900 text-white rounded-xl flex flex-col items-center gap-2 shadow-xl">
            <div className="font-bold text-lg mb-1">Vote on this market</div>
            <div className="text-xs opacity-70 mb-2">Market ID: {marketId}</div>
            <div className="flex gap-2">
                <button className="px-4 py-2 rounded-full bg-blue-500 hover:bg-blue-600" onClick={() => vote('YES')}>YES</button>
                <button className="px-4 py-2 rounded-full bg-red-500 hover:bg-red-600" onClick={() => vote('NO')}>NO</button>
            </div>
            <div className="text-xs mt-2 min-h-[1.5em]">{status || 'Click YES or NO.'}</div>
        </div>
    );
}
