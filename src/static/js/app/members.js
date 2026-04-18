/**
 * members.js — Alpine factories for /members directory
 * Requires window.LP.isAuthenticated + window.LP.t.defaultLocationTrapani/favoritesRemoved/favoritesAdded.
 */

function membersFilter() {
    return {
        filtersOpen: false,
        locating: false,
        lat: null,
        lng: null,
        detectLocation() {
            if (!navigator.geolocation) {
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Geolocation not supported' } }));
                return;
            }
            this.locating = true;
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    this.lat = pos.coords.latitude.toFixed(6);
                    this.lng = pos.coords.longitude.toFixed(6);
                    this.locating = false;
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Location detected' } }));
                },
                (err) => {
                    // Fallback to Trapani centro when browser denies geolocation (e.g. HTTP, no domain)
                    this.lat = '38.0174';
                    this.lng = '12.5144';
                    this.locating = false;
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'info', message: window.LP.t.defaultLocationTrapani } }));
                },
                { enableHighAccuracy: true, timeout: 10000 }
            );
        }
    };
}

function membersFavorites() {
    return {
        favoriteIds: new Set(),
        async init() {
            if (window.LP.isAuthenticated) {
            try {
                var resp = await fetch('/api/v1/users/me/favorite-ids');
                if (resp.ok) {
                    var data = await resp.json();
                    this.favoriteIds = new Set(data.ids);
                }
            } catch(e) {}
            }
        },
        isFavorited(userId) {
            return this.favoriteIds.has(String(userId));
        },
        async toggleFavorite(userId) {
            var uid = String(userId);
            if (this.isFavorited(uid)) {
                var resp = await fetch('/api/v1/users/' + uid + '/favorite', { method: 'DELETE' });
                if (resp.ok) {
                    this.favoriteIds.delete(uid);
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'info', message: window.LP.t.favoritesRemoved } }));
                }
            } else {
                var resp = await fetch('/api/v1/users/' + uid + '/favorite', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                if (resp.ok) {
                    this.favoriteIds.add(uid);
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: window.LP.t.favoritesAdded } }));
                }
            }
        }
    };
}
