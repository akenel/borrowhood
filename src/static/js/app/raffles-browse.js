/**
 * raffles-browse.js — Alpine factory for /raffles page
 *
 * No Jinja dependencies.
 * Extracted from raffles.html on 2026-04-18.
 */

function rafflesApp() {
    return {
        raffles: [],
        filtered: [],
        loading: false,
        filter: 'all',
        search: '',
        sortBy: 'ending_soon',
        async load() {
            this.loading = true;
            try {
                const status = this.filter === 'all' ? 'all' : this.filter;
                const r = await fetch('/api/v1/raffles?status=' + status + '&limit=50');
                if (r.ok) this.raffles = await r.json();
            } catch(e) {}
            this.filterResults();
            this.loading = false;
        },
        filterResults() {
            var q = this.search.toLowerCase().trim();
            var results = this.raffles;
            if (q) {
                results = results.filter(function(r) {
                    return (r.title || '').toLowerCase().indexOf(q) >= 0
                        || (r.organizer_name || '').toLowerCase().indexOf(q) >= 0
                        || (r.description || '').toLowerCase().indexOf(q) >= 0;
                });
            }
            var sort = this.sortBy;
            results = results.slice().sort(function(a, b) {
                if (sort === 'ending_soon') {
                    var ah = a.stats ? a.stats.hours_remaining : 9999;
                    var bh = b.stats ? b.stats.hours_remaining : 9999;
                    if (ah === null) ah = 9999;
                    if (bh === null) bh = 9999;
                    return ah - bh;
                }
                if (sort === 'most_sold') {
                    var as = a.stats ? a.stats.percent_sold : 0;
                    var bs = b.stats ? b.stats.percent_sold : 0;
                    return bs - as;
                }
                if (sort === 'cheapest') return (a.ticket_price || 0) - (b.ticket_price || 0);
                return 0;
            });
            this.filtered = results;
        },
    };
}
