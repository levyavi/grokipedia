// Background service worker for checking if Grokipedia pages exist
const GROKIPEDIA_BASE_URL = 'https://grokipedia.com';

// Cache for checked links to avoid redundant requests
const linkCache = new Map();
const CACHE_DURATION = 1000 * 60 * 60; // 1 hour cache

// Check if a Grokipedia page exists
async function checkGrokipediaExists(grokipediaUrl) {
  // Check cache first
  const cached = linkCache.get(grokipediaUrl);
  if (cached) {
    const { exists, timestamp } = cached;
    const age = Date.now() - timestamp;
    if (age < CACHE_DURATION) {
      return exists;
    }
    // Cache expired
    linkCache.delete(grokipediaUrl);
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

    const response = await fetch(grokipediaUrl, {
      method: 'HEAD',
      signal: controller.signal,
      redirect: 'follow'
    });

    clearTimeout(timeoutId);
    
    const exists = response.ok && response.status === 200;
    
    // Cache the result
    linkCache.set(grokipediaUrl, {
      exists,
      timestamp: Date.now()
    });
    
    return exists;
  } catch (error) {
    // Network error, timeout, or other issue - assume page doesn't exist
    if (error.name !== 'AbortError') {
      console.error('Error checking Grokipedia link:', error);
    }
    
    linkCache.set(grokipediaUrl, {
      exists: false,
      timestamp: Date.now()
    });
    
    return false;
  }
}

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'checkGrokipedia') {
    const { grokipediaUrl } = request;
    
    // Use async/await pattern
    checkGrokipediaExists(grokipediaUrl).then(exists => {
      sendResponse({ exists });
    }).catch(error => {
      console.error('Error in checkGrokipedia:', error);
      sendResponse({ exists: false });
    });
    
    // Return true to indicate we will send a response asynchronously
    return true;
  }
});
