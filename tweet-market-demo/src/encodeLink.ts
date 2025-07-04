import { encodeFunctionData } from "viem";

export function buildMarketLink(opts: {
    contract: `0x${string}`,
    abi: any[],
    id: string,
    yes: boolean,
    chainId?: number
}) {
    const data = encodeFunctionData({
        abi: opts.abi,
        functionName: "vote",
        args: [opts.id, opts.yes]
    });
    const payload = btoa(JSON.stringify({
        to: opts.contract,
        data,
        value: "0",
        chainId: opts.chainId ?? 1
    }));
    return `https://prove-me-wrong-git-main-wooblay-projects.vercel.app/player.html?id=${opts.id}&p=${payload}`;
} 