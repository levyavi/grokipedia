// Background service worker for checking if Grokipedia pages exist
const GROKIPEDIA_BASE_URL = 'https://grokipedia.com';

// Cache for checked links to avoid redundant requests
const linkCache = new Map();
const CACHE_DURATION = 1000 * 60 * 60; // 1 hour cache

const NOT_FOUND_MARKERS = [
  "Article not found",
  "This page doesn't exist... yet"
];

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

    // Use GET so we can detect soft-404 pages that still return 200
    const response = await fetch(grokipediaUrl, {
      method: 'GET',
      signal: controller.signal,
      redirect: 'follow'
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      linkCache.set(grokipediaUrl, { exists: false, timestamp: Date.now() });
      return false;
    }

    // If redirected to a non-article path, consider it not found
    const finalUrl = response.url || grokipediaUrl;
    if (!finalUrl.includes('/page/')) {
      linkCache.set(grokipediaUrl, { exists: false, timestamp: Date.now() });
      return false;
    }

    // Read a small portion of the body to detect soft 404 markers
    const text = (await response.text()).slice(0, 8000);
    const soft404 = NOT_FOUND_MARKERS.some(marker => text.includes(marker));
    const exists = !soft404;

    linkCache.set(grokipediaUrl, { exists, timestamp: Date.now() });
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
      console.error('[Grokipedia Background] Error in checkGrokipedia:', error);
      sendResponse({ exists: false });
    });
    
    // Return true to indicate we will send a response asynchronously
    return true;
  }
  
  // Return false if action not handled
  return false;
});
