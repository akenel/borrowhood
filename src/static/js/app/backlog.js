/**
 * backlog.js — Alpine factory for /backlog (dev tool)
 * Requires window.LP.username.
 */

function backlogBoard() {
    return {
        view: 'board',
        summary: { total: 0, pending: 0, in_progress: 0, on_hold: 0, blocked: 0, done: 0, archived: 0 },
        items: [],
        selectedItem: null,
        activities: [],
        showCreateModal: false,
        filterStatus: '',
        filterPriority: '',
        filterType: '',
        filterAssigned: '',
        newItem: { title: '', description: '', item_type: 'dev_task', priority: 'medium', assigned_to: '', tags: '', created_by: window.LP.username },

        get assignees() {
            const names = [...new Set(this.items.map(i => i.assigned_to).filter(Boolean))];
            return names.sort();
        },

        get filteredItems() {
            return this.items.filter(i => {
                if (this.filterStatus && i.status !== this.filterStatus) return false;
                if (this.filterPriority && i.priority !== this.filterPriority) return false;
                if (this.filterType && i.item_type !== this.filterType) return false;
                if (this.filterAssigned === '_unassigned' && i.assigned_to) return false;
                if (this.filterAssigned && this.filterAssigned !== '_unassigned' && i.assigned_to !== this.filterAssigned) return false;
                return true;
            });
        },

        async api(url, options = {}) {
            const r = await fetch(url, { ...options, headers: { 'Content-Type': 'application/json', ...options.headers } });
            if (!r.ok) throw new Error(`API error: ${r.status}`);
            return r.json();
        },

        async loadAll() {
            try {
                const [s, i] = await Promise.all([
                    this.api('/api/v1/backlog/summary'),
                    this.api('/api/v1/backlog/items'),
                ]);
                this.summary = s;
                this.items = i;
            } catch (e) {
                console.error('Failed to load backlog data:', e);
            }
        },

        async openDetail(item) {
            this.selectedItem = item;
            try {
                this.activities = await this.api(`/api/v1/backlog/items/${item.id}/activities`);
            } catch (e) {
                this.activities = [];
            }
        },

        async quickStatus(newStatus) {
            if (!this.selectedItem) return;
            try {
                const actor = window.LP.username;
                const updated = await this.api(`/api/v1/backlog/items/${this.selectedItem.id}`, {
                    method: 'PUT',
                    body: JSON.stringify({ status: newStatus, actor }),
                });
                this.selectedItem = updated;
                await this.loadAll();
                this.activities = await this.api(`/api/v1/backlog/items/${this.selectedItem.id}/activities`);
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: `Status changed to ${newStatus.replace('_', ' ')}` } }));
            } catch (e) {
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Failed to update status' } }));
            }
        },

        async createItem() {
            try {
                await this.api('/api/v1/backlog/items', {
                    method: 'POST',
                    body: JSON.stringify(this.newItem),
                });
                this.showCreateModal = false;
                this.newItem = { title: '', description: '', item_type: 'dev_task', priority: 'medium', assigned_to: '', tags: '', created_by: this.newItem.created_by };
                await this.loadAll();
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Item created!' } }));
            } catch (e) {
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Failed to create item' } }));
            }
        },
    };
}
