/**
 * chat.js — Alpine factory for /chat (AI Concierge)
 *
 * Requires window.LP.lang and window.LP.t.loginRequired + genericError.
 * Extracted from chat.html on 2026-04-18.
 */

function chatApp() {
    return {
        messages: [],
        query: '',
        loading: false,

        init() {
            this.$refs.input.focus();
            const params = new URLSearchParams(window.location.search);
            const seed = params.get('q');
            if (seed && seed.trim()) {
                this.sendQuery(seed.trim());
                // Clean the URL so refresh doesn't re-send
                const url = new URL(window.location);
                url.searchParams.delete('q');
                window.history.replaceState({}, '', url);
            }
        },

        async send() {
            const q = this.query.trim();
            if (!q || this.loading) return;
            this.sendQuery(q);
        },

        async sendQuery(q) {
            this.query = '';
            this.messages.push({ role: 'user', text: q });
            this.scrollToBottom();
            this.loading = true;

            try {
                const resp = await fetch('/api/v1/ai/concierge', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: q,
                        language: window.LP.lang
                    }),
                });

                if (!resp.ok) {
                    if (resp.status === 401 || resp.status === 403) {
                        this.messages.push({
                            role: 'bot',
                            text: window.LP.t.loginRequired,
                        });
                    } else {
                        throw new Error('API error');
                    }
                } else {
                    const data = await resp.json();
                    this.messages.push({
                        role: 'bot',
                        text: data.response || data.interpretation || 'No response.',
                        items: data.items || [],
                        members: data.members || [],
                        suggestions: data.suggestions || [],
                        provider: data.ai_provider || '',
                    });
                }
            } catch (e) {
                this.messages.push({
                    role: 'bot',
                    text: window.LP.t.genericError,
                });
            }

            this.loading = false;
            this.scrollToBottom();
            this.$refs.input.focus();
        },

        scrollToBottom() {
            this.$nextTick(() => {
                const el = this.$refs.messages;
                if (el) el.scrollTop = el.scrollHeight;
            });
        }
    };
}
