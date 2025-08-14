/**
 * Fix internal links to open in the same tab
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get all links
    const links = document.querySelectorAll('a');
    
    links.forEach(function(link) {
        const href = link.getAttribute('href');
        
        if (href) {
            // Internal links (same domain, relative paths, anchors)
            if (href.startsWith('#') ||           // Anchor links
                href.startsWith('/') ||           // Absolute paths
                href.startsWith('./') ||          // Relative paths
                href.startsWith('../') ||         // Parent directory paths
                href.endsWith('.html') ||         // HTML files
                (!href.startsWith('http') && !href.startsWith('mailto:') && !href.startsWith('tel:'))) {
                
                // Remove any existing target attribute
                link.removeAttribute('target');
                
                // Ensure it opens in the same tab
                link.setAttribute('target', '_self');
            }
            // External links (http/https but not localhost)
            else if (href.startsWith('http') && 
                     !href.includes('localhost') && 
                     !href.includes('127.0.0.1')) {
                
                // Open external links in new tab
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
            }
        }
    });
    
    // Also handle dynamically added links
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    const newLinks = node.querySelectorAll ? node.querySelectorAll('a') : [];
                    newLinks.forEach(function(link) {
                        const href = link.getAttribute('href');
                        if (href && !href.startsWith('http')) {
                            link.removeAttribute('target');
                            link.setAttribute('target', '_self');
                        }
                    });
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

// Also handle clicks on the sidebar and navigation
document.addEventListener('click', function(event) {
    const target = event.target;
    
    // Check if the clicked element is a link or inside a link
    const link = target.closest('a');
    
    if (link) {
        const href = link.getAttribute('href');
        
        // Force internal links to open in same tab
        if (href && 
            (href.startsWith('#') || 
             href.startsWith('/') || 
             href.startsWith('./') || 
             href.startsWith('../') || 
             href.endsWith('.html') ||
             (!href.startsWith('http') && !href.startsWith('mailto:')))) {
            
            link.setAttribute('target', '_self');
        }
    }
});