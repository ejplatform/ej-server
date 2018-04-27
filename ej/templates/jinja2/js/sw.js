'use strict';

// Start workbox
importScripts('https://storage.googleapis.com/workbox-cdn/releases/3.0.0/workbox-sw.js');
var log = console.log;

/**
 * Initialize service workers
 */

function registerAllRoutes(workbox) {
    log('[sw] Starting service worker');

    // Cache javascript
    workbox.routing.registerRoute(
        new RegExp('.*\.js'),
        // workbox.strategies.cacheFirst()
        workbox.strategies.networkFirst()
    );

    // Css can be safely hot-reloaded on page
    workbox.routing.registerRoute(
        new RegExp('.*\.css'),
        workbox.strategies.staleWhileRevalidate()
    );

    // Static large immutable binary assets
    workbox.routing.registerRoute(
        new RegExp('.*\.(?:png|jpg|jpeg|svg|gif)'),
        workbox.strategies.cacheFirst({
            plugins: [
                new workbox.expiration.Plugin({
                    maxEntries: 50,
                    maxAgeSeconds: 7 * 24 * 60 * 60 // a week
                })
            ]
        })
    );

    // Inner urls. We classify in a case-by-case basis
    var urlpatterns = [
        new RegExp('/?'),
        new RegExp('/conversations/.*/?')
    ];
    for (var i=0; i < urlpatterns.length; i++) {
        workbox.routing.registerRoute(
            urlpatterns[i],
            workbox.strategies.networkFirst()
        )
    }


    log('[sw] all routes registered!');
}

registerAllRoutes(workbox);
