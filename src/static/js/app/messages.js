/**
 * messages.js — Alpine.js for /messages page
 *
 * No Jinja dependencies — pure client logic.
 * Extracted from messages.html on 2026-04-18.
 */

function formatMsgTime(iso) {
    if (!iso) return '';
    var d = new Date(iso);
    var days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    var months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    var day = days[d.getUTCDay()];
    var month = months[d.getUTCMonth()];
    var date = d.getUTCDate();
    var year = d.getUTCFullYear();
    var hours = d.getUTCHours();
    var minutes = d.getUTCMinutes();
    var ampm = hours >= 12 ? 'pm' : 'am';
    var h12 = hours % 12 || 12;
    var min = minutes < 10 ? '0' + minutes : minutes;
    return day + ', ' + month + ' ' + date + ', ' + year + ' ' + h12 + ':' + min + ampm + ' UTC';
}

function messagesApp() {
    return {
        threads: [],
        messages: [],
        loaded: false,
        activeThread: null,
        activeThreadName: '',
        activeThreadAvatar: null,
        activeRentalId: null,
        activeOrderContext: null,
        newMessage: '',
        sending: false,
        myUserId: '',
        pollTimer: null,

        // New Message search
        showNewMessage: false,
        searchQuery: '',
        searchResults: [],
        searchLoading: false,

        // Edit/delete
        openMenuId: null,
        editingMsgId: null,
        editBody: '',

        async init() {
            // Get my user ID
            try {
                var resp = await fetch('/api/v1/users/me');
                if (resp.ok) { var d = await resp.json(); this.myUserId = d.id; }
            } catch(e) {}

            await this.loadThreads();
            this.loaded = true;

            // Check URL params
            var params = new URLSearchParams(window.location.search);
            var rentalId = params.get('rental');
            var toUser = params.get('to');

            if (rentalId && toUser) {
                // Open order-specific thread
                this.activeRentalId = rentalId;
                await this.openThread(toUser);
                await this.loadOrderContext(rentalId);
            } else if (toUser) {
                await this.openThread(toUser);
            }

            // Pre-fill message with item context
            var about = params.get('about');
            if (about && !this.newMessage) {
                this.newMessage = 'Hi, I\'m interested in: ' + about;
            }

            // Poll for new messages every 10s
            this.pollTimer = setInterval(() => {
                this.loadThreads();
                if (this.activeThread) {
                    if (this.activeRentalId) {
                        this.loadOrderMessages(this.activeRentalId);
                    } else {
                        this.loadMessages(this.activeThread);
                    }
                }
            }, 10000);
        },

        async loadOrderContext(rentalId) {
            try {
                var resp = await fetch('/api/v1/rentals/' + rentalId);
                if (resp.ok) {
                    var rental = await resp.json();
                    this.activeOrderContext = {
                        status: rental.status,
                        listing_type: rental.listing_type || 'order',
                        item_name: rental.item_name || rental.listing_name || null,
                        start_date: rental.requested_start,
                        end_date: rental.requested_end,
                    };
                }
            } catch(e) {}
        },

        async loadOrderMessages(rentalId) {
            try {
                var resp = await fetch('/api/v1/messages/order/' + rentalId);
                if (resp.ok) {
                    this.messages = await resp.json();
                    this.$nextTick(() => {
                        var el = document.getElementById('msg-scroll');
                        if (el) el.scrollTop = el.scrollHeight;
                    });
                }
            } catch(e) {
                // Fallback to user-to-user thread
                if (this.activeThread) await this.loadMessages(this.activeThread);
            }
        },

        async loadThreads() {
            try {
                var resp = await fetch('/api/v1/messages/threads');
                if (resp.ok) this.threads = await resp.json();
            } catch(e) {}
        },

        async selectThread(thread) {
            this.activeThread = thread.other_user_id;
            this.activeThreadName = thread.other_user_name;
            this.activeThreadAvatar = thread.other_user_avatar || null;
            this.activeRentalId = thread.rental_id || null;
            this.activeOrderContext = null;
            if (this.activeRentalId) {
                await this.loadOrderMessages(this.activeRentalId);
                await this.loadOrderContext(this.activeRentalId);
            } else {
                await this.loadMessages(thread.other_user_id);
            }
            thread.unread_count = 0;
        },

        async openThread(userId) {
            this.activeThread = userId;
            await this.loadMessages(userId);
            // Find thread name + avatar from existing threads
            var t = this.threads.find(function(t) { return t.other_user_id === userId; });
            if (t) {
                this.activeThreadName = t.other_user_name;
                this.activeThreadAvatar = t.other_user_avatar || null;
            } else {
                // New conversation -- fetch recipient info
                try {
                    var resp = await fetch('/api/v1/users/' + userId);
                    if (resp.ok) {
                        var u = await resp.json();
                        this.activeThreadName = u.display_name || u.username || 'User';
                        this.activeThreadAvatar = u.avatar_url || null;
                    }
                } catch(e) {}
            }
        },

        async loadMessages(userId) {
            try {
                var resp = await fetch('/api/v1/messages/thread/' + userId);
                if (resp.ok) {
                    this.messages = await resp.json();
                    this.$nextTick(() => {
                        var el = document.getElementById('msg-scroll');
                        if (el) el.scrollTop = el.scrollHeight;
                    });
                }
            } catch(e) {}
        },

        async sendMessage() {
            if (!this.newMessage.trim() || !this.activeThread) return;
            this.sending = true;
            try {
                var payload = {
                    recipient_id: this.activeThread,
                    body: this.newMessage.trim()
                };
                if (this.activeRentalId) payload.rental_id = this.activeRentalId;
                var resp = await fetch('/api/v1/messages', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (resp.ok) {
                    var msg = await resp.json();
                    this.messages.push(msg);
                    this.newMessage = '';
                    // Refresh thread list so new conversation appears in sidebar
                    await this.loadThreads();
                    this.$nextTick(() => {
                        var el = document.getElementById('msg-scroll');
                        if (el) el.scrollTop = el.scrollHeight;
                    });
                }
            } catch(e) {}
            this.sending = false;
        },

        // ── New Message: member search ──

        async searchMembers() {
            if (this.searchQuery.length < 2) {
                this.searchResults = [];
                return;
            }
            this.searchLoading = true;
            try {
                var resp = await fetch('/api/v1/users?q=' + encodeURIComponent(this.searchQuery) + '&limit=6');
                if (resp.ok) {
                    var data = await resp.json();
                    // Filter out self
                    var self = this;
                    this.searchResults = data.items.filter(function(m) { return m.id !== self.myUserId; });
                }
            } catch(e) {}
            this.searchLoading = false;
        },

        startNewThread(member) {
            this.showNewMessage = false;
            this.searchQuery = '';
            this.searchResults = [];
            this.activeThread = member.id;
            this.activeThreadName = member.display_name;
            this.activeThreadAvatar = member.avatar_url || null;
            this.loadMessages(member.id);
        },

        // ── Edit / Delete ──

        toggleMenu(msgId) {
            this.openMenuId = this.openMenuId === msgId ? null : msgId;
        },

        startEdit(msg) {
            this.openMenuId = null;
            this.editingMsgId = msg.id;
            this.editBody = msg.body;
        },

        cancelEdit() {
            this.editingMsgId = null;
            this.editBody = '';
        },

        async saveEdit(msgId) {
            if (!this.editBody.trim()) return;
            try {
                var resp = await fetch('/api/v1/messages/' + msgId, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ body: this.editBody.trim() })
                });
                if (resp.ok) {
                    var updated = await resp.json();
                    var idx = this.messages.findIndex(function(m) { return m.id === msgId; });
                    if (idx >= 0) {
                        this.messages[idx].body = updated.body;
                        this.messages[idx].edited_at = updated.edited_at;
                    }
                } else {
                    var err = await resp.json().catch(function() { return {}; });
                    alert(err.detail || 'Could not edit message');
                }
            } catch(e) {}
            this.editingMsgId = null;
            this.editBody = '';
        },

        async deleteMessage(msgId) {
            if (!confirm('Delete this message?')) return;
            this.openMenuId = null;
            try {
                var resp = await fetch('/api/v1/messages/' + msgId, { method: 'DELETE' });
                if (resp.ok) {
                    this.messages = this.messages.filter(function(m) { return m.id !== msgId; });
                    await this.loadThreads();
                } else {
                    var err = await resp.json().catch(function() { return {}; });
                    alert(err.detail || 'Could not delete message');
                }
            } catch(e) {}
        },

        destroy() {
            if (this.pollTimer) clearInterval(this.pollTimer);
        }
    };
}
