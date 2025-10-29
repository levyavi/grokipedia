// Configuration
const GROKIPEDIA_BASE_URL = 'https://grokipedia.com';

// Local cache for checked links (supplements background script cache)
const linkCache = new Map();

// Convert Wikipedia URL to Grokipedia URL
function convertToGrokipediaUrl(wikiUrl) {
  try {
    const url = new URL(wikiUrl);
    // Extract the article path (e.g., /wiki/Article_Name)
    const articlePath = url.pathname;
    
    // Preserve hash if present
    const hash = url.hash;
    
    // Construct Grokipedia URL
    return `${GROKIPEDIA_BASE_URL}${articlePath}${hash}`;
  } catch (e) {
    console.error('Error converting URL:', e);
    return null;
  }
}

// Check if a Grokipedia page exists using background script
async function checkGrokipediaExists(grokipediaUrl) {
  // Check local cache first
  if (linkCache.has(grokipediaUrl)) {
    return linkCache.get(grokipediaUrl);
  }

  try {
    const response = await chrome.runtime.sendMessage({
      action: 'checkGrokipedia',
      grokipediaUrl: grokipediaUrl
    });
    
    const exists = response?.exists || false;
    linkCache.set(grokipediaUrl, exists);
    return exists;
  } catch (error) {
    console.error('Error checking Grokipedia link:', error);
    linkCache.set(grokipediaUrl, false);
    return false;
  }
}

// Extract Wikipedia URL from various link formats (handles Google redirects, etc.)
function extractWikipediaUrl(link) {
  // Check href attribute first
  let href = link.getAttribute('href');
  
  // Handle Google search result redirects: /url?q=https://en.wikipedia.org/...
  // Google uses various formats: /url?q=, /url?url=, /url?sa=t&url=, etc.
  if (href && (href.includes('/url?') || href.includes('&url='))) {
    try {
      // Try to extract from q parameter first (most common)
      const qMatch = href.match(/[?&]q=([^&]*)/);
      if (qMatch) {
        href = decodeURIComponent(qMatch[1]);
      } else {
        // Try url parameter
        const urlMatch = href.match(/[?&]url=([^&]*)/);
        if (urlMatch) {
          href = decodeURIComponent(urlMatch[1]);
        } else {
          // Try parsing as URL
          try {
            const urlObj = new URL(href, window.location.origin);
            const qParam = urlObj.searchParams.get('q');
            const urlParam = urlObj.searchParams.get('url');
            if (qParam) {
              href = decodeURIComponent(qParam);
            } else if (urlParam) {
              href = decodeURIComponent(urlParam);
            }
          } catch (e) {
            // Keep original href if URL parsing fails
          }
        }
      }
    } catch (e) {
      // If decoding fails, try simple regex extraction
      const match = href.match(/[?&](q|url)=([^&]*)/);
      if (match) {
        try {
          href = decodeURIComponent(match[2]);
        } catch (decodeError) {
          // Keep as-is if decode fails
        }
      }
    }
  }
  
  // Check data-href attribute (some sites use this)
  if (!href || !href.includes('wikipedia.org')) {
    const dataHref = link.getAttribute('data-href');
    if (dataHref && dataHref.includes('wikipedia.org')) {
      href = dataHref;
    }
  }
  
  if (!href || !href.includes('wikipedia.org/wiki/')) {
    return null;
  }

  // Create full URL if relative
  try {
    if (href.startsWith('http://') || href.startsWith('https://')) {
      return href;
    }
    return new URL(href, window.location.origin).href;
  } catch (e) {
    console.error('Error creating Wikipedia URL:', e);
    return null;
  }
}

// Process a single Wikipedia link
async function processWikipediaLink(link) {
  // Skip if already processed
  if (link.dataset.grokipediaProcessed === 'true' || link.dataset.grokipediaProcessed === 'processing') {
    return;
  }

  const wikiUrl = extractWikipediaUrl(link);
  if (!wikiUrl) {
    return;
  }

  const grokipediaUrl = convertToGrokipediaUrl(wikiUrl);
  if (!grokipediaUrl) {
    return;
  }

  // Mark as processing to avoid duplicate checks
  link.dataset.grokipediaProcessed = 'processing';
  
  try {
    // Check if Grokipedia page exists
    const exists = await checkGrokipediaExists(grokipediaUrl);
    
    if (exists) {
      // Replace the link - always use direct Grokipedia link (cleaner than redirects)
      link.href = grokipediaUrl;
      link.dataset.grokipediaProcessed = 'true';
      link.dataset.originalWikiUrl = wikiUrl;
      console.log('[Grokipedia] Replaced:', wikiUrl, '->', grokipediaUrl);
    } else {
      // Keep the original link, mark as processed
      link.dataset.grokipediaProcessed = 'true';
    }
  } catch (error) {
    console.error('Error processing Wikipedia link:', error);
    link.dataset.grokipediaProcessed = 'true';
  }
}

// Process all Wikipedia links on the page
function processAllWikipediaLinks() {
  // Find all links - check both href and data-href attributes
  const links = document.querySelectorAll('a:not([data-grokipedia-processed="true"]):not([data-grokipedia-processed="processing"])');
  
  let foundCount = 0;
  links.forEach(link => {
    const href = link.getAttribute('href') || link.getAttribute('data-href') || '';
    // Check if it's a Wikipedia link or Google redirect to Wikipedia
    if (href.includes('wikipedia.org/wiki/') || (href.includes('/url?q=') && href.includes('wikipedia.org'))) {
      foundCount++;
      processWikipediaLink(link);
    }
  });
  
  if (foundCount > 0) {
    console.log(`[Grokipedia] Found ${foundCount} Wikipedia link(s) to process`);
  }
}

// Use MutationObserver to handle dynamically loaded content
const observer = new MutationObserver((mutations) => {
  let shouldProcess = false;
  
  mutations.forEach((mutation) => {
    if (mutation.type === 'childList') {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1) { // Element node
          // Check if the added node or its children contain Wikipedia links
          if (node.tagName === 'A') {
            const href = node.getAttribute('href') || node.getAttribute('data-href') || '';
            if (href.includes('wikipedia.org/wiki/') || (href.includes('/url?q=') && href.includes('wikipedia.org'))) {
              shouldProcess = true;
            }
          } else if (node.querySelectorAll) {
            // Check for links in children
            const childLinks = node.querySelectorAll('a');
            childLinks.forEach(link => {
              const href = link.getAttribute('href') || link.getAttribute('data-href') || '';
              if (href.includes('wikipedia.org/wiki/') || (href.includes('/url?q=') && href.includes('wikipedia.org'))) {
                shouldProcess = true;
              }
            });
          }
        }
      });
    }
  });
  
  if (shouldProcess) {
    // Debounce to avoid excessive processing
    clearTimeout(window.grokipediaProcessTimeout);
    window.grokipediaProcessTimeout = setTimeout(() => {
      processAllWikipediaLinks();
    }, 500);
  }
});

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

function init() {
  // Wait for body to be available
  if (!document.body) {
    // Fallback if body isn't ready yet
    setTimeout(init, 100);
    return;
  }

  console.log('[Grokipedia] Extension initialized on', window.location.hostname);
  
  // Process existing links immediately
  processAllWikipediaLinks();
  
  // Process again after a short delay (for dynamically loaded content)
  setTimeout(() => {
    processAllWikipediaLinks();
  }, 1000);
  
  // Observe DOM changes for dynamically loaded content
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}