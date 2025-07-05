// inpage-proxy.js - runs in the page context, NOT the content-script
window.addEventListener('message', async (e) => {
    if (e.source !== window || e.data?.type !== 'CS_REQUEST') return;
    try {
        const result = await window.ethereum.request(e.data.payload);
        window.postMessage({ type: 'CS_RESPONSE', id: e.data.id, result }, '*');
    } catch (err) {
        window.postMessage({ type: 'CS_RESPONSE', id: e.data.id, error: err.message }, '*');
    }
}); 