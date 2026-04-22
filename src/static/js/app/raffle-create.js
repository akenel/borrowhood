/**
 * raffle-create.js — Alpine factory for /raffles/create
 *
 * Requires window.LP.t.draftSaved + rafflePublished.
 * Extracted from raffle_create.html on 2026-04-18.
 */

function raffleForm() {
    return {
        items: [],
        itemsLoaded: false,
        form: {
            item_id: '',
            ticket_price: 2.00,
            max_tickets: 10,
            max_tickets_per_user: null,
            draw_date: '',
            draw_type: 'date',
            payment_methods: [],
            payment_instructions: '',
            delivery_method: 'pickup',
        },
        tosAccepted: false,
        saving: false,
        error: null,
        async loadItems() {
            try {
                // Get my user ID first, then only show MY items
                const me = await fetch('/api/v1/users/me');
                if (!me.ok) return;
                const user = await me.json();
                const r = await fetch('/api/v1/items?owner_id=' + user.id + '&limit=100');
                if (r.ok) {
                    const all = await r.json();
                    this.items = all.filter(i => i.owner_id === user.id);
                    // Preselect item from ?item_id=... URL param (coming from /list flow)
                    const preselect = new URLSearchParams(window.location.search).get('item_id');
                    if (preselect && this.items.some(i => i.id === preselect)) {
                        this.form.item_id = preselect;
                    }
                }
            } catch(e) {
            } finally {
                this.itemsLoaded = true;
            }
        },
        async saveDraft() {
            this.saving = true; this.error = null;
            try {
                const body = { ...this.form };
                if (body.draw_date) body.draw_date = new Date(body.draw_date).toISOString();
                if (!body.max_tickets_per_user) delete body.max_tickets_per_user;
                body.title = (this.items.find(i => i.id === body.item_id) || {}).name || 'Raffle';
                const r = await fetch('/api/v1/raffles', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body),
                });
                const d = await r.json();
                if (r.ok) {
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: window.LP.t.draftSaved } }));
                    window.location.href = '/raffles/' + d.id;
                } else {
                    this.error = d.detail || 'Failed to create raffle';
                }
            } catch(e) { this.error = 'Network error'; }
            this.saving = false;
        },
        async publish() {
            this.saving = true; this.error = null;
            try {
                const body = { ...this.form };
                if (body.draw_date) body.draw_date = new Date(body.draw_date).toISOString();
                if (!body.max_tickets_per_user) delete body.max_tickets_per_user;
                body.title = (this.items.find(i => i.id === body.item_id) || {}).name || 'Raffle';
                // Create draft first
                const cr = await fetch('/api/v1/raffles', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body),
                });
                const cd = await cr.json();
                if (!cr.ok) { this.error = cd.detail || 'Failed to create'; this.saving = false; return; }
                // Then publish
                const pr = await fetch('/api/v1/raffles/' + cd.id + '/publish', { method: 'POST' });
                const pd = await pr.json();
                if (pr.ok) {
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: window.LP.t.rafflePublished } }));
                    window.location.href = '/raffles/' + cd.id;
                } else {
                    this.error = pd.detail || 'Created as draft but could not publish';
                    setTimeout(() => { window.location.href = '/raffles/' + cd.id; }, 2000);
                }
            } catch(e) { this.error = 'Network error'; }
            this.saving = false;
        },
    };
}
