'use strict';

/**
 * Initialize service workers
 */

function registerAllRoutes() {
    // Cache javascript
    workbox.routing.registerRoute(
        /.*\.js/,
        workbox.strategies.cacheFirst()
    );

    // Css can be safely hot-reloaded on page
    workbox.routing.registerRoute(
        /.*\.css/,
        workbox.strategies.staleWhileRevalidate()
    );

    // Static immutable binary assets
    workbox.routing.registerRoute(
        /.*\.(?:png|jpg|jpeg|svg|gif)/,
        workbox.strategies.cacheFirst({
            plugins: [
                new workbox.expiration.Plugin({
                    maxEntries: 20,
                    maxAgeSeconds: 7 * 24 * 60 * 60 // a week
                })
            ]
        })
    );

    // Dynamic urls and root page
    workbox.routing.registerRoute(
        function (url) { return url === '/'; },
        workbox.strategies.networkFirst()
    );

    // Dynamic urls and root page
    workbox.routing.registerRoute(
        /[^\/]*\/\w+([-]\w+)*\/?/,
        workbox.strategies.networkFirst()
    );

    // Dynamic urls and root page
    workbox.routing.registerRoute(
        function (url) { console.log(url); },
        workbox.strategies.networkFirst()
    );
}

// Start workbox
importScripts('https://storage.googleapis.com/workbox-cdn/releases/3.0.0/workbox-sw.js');
console.log('Service worker started!');

if (workbox) {
    registerAllRoutes();
} else {
    console.log('ERROR: Workbox didn\'t load');
}

