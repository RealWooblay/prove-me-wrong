// Background script for handling AI generator requests and wallet interactions

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Background script received message:', request);

    if (request.type === 'AI_GENERATOR_REQUEST') {
        handleAIGeneratorRequest(request, sendResponse);
        return true; // Keep the message channel open for async response
    }

    if (request.type === 'WALLET_REQUEST') {
        handleWalletRequest(request, sendResponse);
        return true; // Keep the message channel open for async response
    }
});

// Handle AI generator requests
async function handleAIGeneratorRequest(request, sendResponse) {
    try {
        console.log('Making AI generator request:', request.payload);

        const { method = 'POST', url = '/generate', ...payload } = request.payload;

        const requestOptions = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        // Add body for POST requests
        if (method === 'POST') {
            requestOptions.body = JSON.stringify(payload);
        }

        const response = await fetch(`https://prove-me-wrong-production.up.railway.app${url}`, requestOptions);

        if (!response.ok) {
            throw new Error(`AI Generator API error: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        console.log('AI generator response:', result);

        sendResponse({ success: true, data: result });
    } catch (error) {
        console.error('Error in AI generator request:', error);
        sendResponse({
            success: false,
            error: error.message || 'Failed to connect to AI generator'
        });
    }
}

// Handle wallet requests (existing functionality)
async function handleWalletRequest(request, sendResponse) {
    try {
        // Get the active tab to access the page's ethereum provider
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab) {
            throw new Error('No active tab found');
        }

        // Execute script in the page context to access ethereum
        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: async (payload) => {
                if (!window.ethereum) {
                    throw new Error('No ethereum provider found');
                }

                try {
                    const result = await window.ethereum.request(payload);
                    return { success: true, result };
                } catch (error) {
                    return { success: false, error: error.message };
                }
            },
            args: [request.payload]
        });

        const result = results[0].result;
        if (result.success) {
            sendResponse({ success: true, result: result.result });
        } else {
            sendResponse({ success: false, error: result.error });
        }
    } catch (error) {
        console.error('Error in wallet request:', error);
        sendResponse({ success: false, error: error.message });
    }
} 