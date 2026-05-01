self.addEventListener('install', (e) => {
    console.log('PWA Service Worker installé');
});

self.addEventListener('fetch', (e) => {
    // Nécessaire pour être considéré comme PWA
});
