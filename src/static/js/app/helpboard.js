/**
 * helpboard.js — Alpine factory for /helpboard
 *
 * Requires window.LP.lang (UI language code).
 * Extracted from helpboard.html on 2026-04-18.
 */

function helpBoard() {
    return {
        formatDate(dateStr) {
            if (!dateStr) return '';
            try {
                const d = new Date(dateStr);
                if (isNaN(d.getTime())) return '';
                const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
                const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
                const day = d.getDate();
                const suffix = day === 1 || day === 21 || day === 31 ? 'st' : day === 2 || day === 22 ? 'nd' : day === 3 || day === 23 ? 'rd' : 'th';
                let h = d.getUTCHours(), m = d.getUTCMinutes();
                const ampm = h >= 12 ? 'pm' : 'am';
                h = h % 12 || 12;
                const time = m > 0 ? h + ':' + String(m).padStart(2,'0') + ampm : h + ampm;
                return days[d.getUTCDay()] + ', ' + months[d.getUTCMonth()] + ' ' + day + suffix + ' ' + d.getUTCFullYear() + ', ' + time + ' UTC';
            } catch (e) { return ''; }
        },

        // List view state
        posts: [],
        summary: { total: 0, open: 0, needs: 0, offers: 0, resolved: 0 },
        filter: { type: '', category: '', status: '', q: '', sort: 'newest' },
        page: { total: 0, limit: 12, offset: 0, hasMore: false },
        loading: true,
        loadingMore: false,

        // Detail view state
        activePost: null,
        replies: [],
        isPostAuthor: false,
        userId: null,
        replyingTo: null,
        threadReplyBody: '',
        newReplyBody: '',
        replyFileSelected: null,
        submittingReply: false,
        uploadError: '',
        editMode: false,
        editTitle: '',
        editBody: '',

        // Create modal state
        showCreate: false,
        submitting: false,
        error: '',
        createFiles: [],
        aiDraftInput: '',
        aiDrafting: false,
        aiDraftResult: null,
        aiDraftError: '',
        newPost: {
            help_type: 'need',
            title: '',
            body: '',
            category: 'power_tools',
            urgency: 'normal',
            neighborhood: '',
            content_language: (window.LP && window.LP.lang) || 'en'
        },

        async init() {
            await Promise.all([this.loadPosts(), this.loadSummary()]);
            this.loading = false;
            this.$nextTick(() => { if (window.BHTranslate) BHTranslate.autoTranslatePage(); });
        },

        // ── List methods ──

        _buildParams() {
            var params = new URLSearchParams();
            if (this.filter.type) params.set('help_type', this.filter.type);
            if (this.filter.category) params.set('category', this.filter.category);
            if (this.filter.status) params.set('status_filter', this.filter.status);
            if (this.filter.q.trim()) params.set('q', this.filter.q.trim());
            if (this.filter.sort) params.set('sort', this.filter.sort);
            params.set('limit', this.page.limit);
            params.set('offset', this.page.offset);
            return params;
        },
        async loadPosts() {
            var params = this._buildParams();
            var resp = await fetch('/api/v1/helpboard/posts?' + params.toString());
            if (resp.ok) {
                var data = await resp.json();
                this.posts = data.items;
                this.page.total = data.total;
                this.page.hasMore = data.has_more;
            }
        },
        async loadMore() {
            this.loadingMore = true;
            this.page.offset += this.page.limit;
            var params = this._buildParams();
            var resp = await fetch('/api/v1/helpboard/posts?' + params.toString());
            if (resp.ok) {
                var data = await resp.json();
                this.posts = this.posts.concat(data.items);
                this.page.total = data.total;
                this.page.hasMore = data.has_more;
            }
            this.loadingMore = false;
        },
        resetAndLoad() {
            this.page.offset = 0;
            this.loadPosts().then(() => this.$nextTick(() => { if (window.BHTranslate) BHTranslate.autoTranslatePage(); }));
        },
        async loadSummary() {
            var resp = await fetch('/api/v1/helpboard/summary');
            if (resp.ok) this.summary = await resp.json();
        },

        // ── AI Draft ──

        async generateDraft() {
            if (!this.aiDraftInput.trim()) return;
            this.aiDrafting = true;
            this.aiDraftResult = null;
            this.aiDraftError = '';
            try {
                var resp = await fetch('/api/v1/helpboard/draft', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        description: this.aiDraftInput,
                        help_type: this.newPost.help_type,
                        language: this.newPost.content_language
                    })
                });
                if (resp.status === 401) {
                    this.aiDraftError = 'Not logged in -- please log in and try again';
                    return;
                }
                if (resp.ok) {
                    var data = await resp.json();
                    this.aiDraftResult = data;
                    // Fill in the form
                    if (data.title) this.newPost.title = data.title;
                    if (data.body) this.newPost.body = data.body;
                    if (data.category) this.newPost.category = data.category;
                    if (data.urgency) this.newPost.urgency = data.urgency;
                } else {
                    var errText = '';
                    try { errText = await resp.text(); } catch(x) {}
                    this.aiDraftError = 'AI draft failed (HTTP ' + resp.status + ') -- ' + (errText || 'try again or write manually');
                }
            } catch(e) {
                this.aiDraftError = 'AI draft timed out -- try again or write manually';
            }
            this.aiDrafting = false;
        },

        // ── Edit post ──

        startEdit() {
            this.editMode = true;
            this.editTitle = this.activePost.title;
            this.editBody = this.activePost.body || '';
        },
        async saveEdit() {
            var payload = {};
            if (this.editTitle !== this.activePost.title) payload.title = this.editTitle;
            if (this.editBody !== (this.activePost.body || '')) payload.body = this.editBody;
            if (Object.keys(payload).length === 0) { this.editMode = false; return; }
            var resp = await fetch('/api/v1/helpboard/posts/' + this.activePost.id, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (resp.ok) {
                var updated = await resp.json();
                this.activePost = updated;
                this.editMode = false;
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Post updated!' } }));
            }
        },

        // ── Create post ──

        addCreateFiles(event) {
            var files = Array.from(event.target.files);
            for (var f of files) {
                if (f.size > 10 * 1024 * 1024) {
                    this.error = f.name + ' is too large (max 10MB)';
                    return;
                }
                this.createFiles.push(f);
            }
            event.target.value = '';
        },
        async submitPost() {
            this.submitting = true;
            this.error = '';
            try {
                var resp = await fetch('/api/v1/helpboard/posts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        help_type: this.newPost.help_type,
                        title: this.newPost.title,
                        body: this.newPost.body || null,
                        category: this.newPost.category,
                        urgency: this.newPost.urgency,
                        neighborhood: this.newPost.neighborhood || null,
                        content_language: this.newPost.content_language
                    })
                });
                if (resp.status === 401) { window.location.href = '/login'; return; }
                if (!resp.ok) {
                    var err = await resp.json();
                    this.error = err.detail || 'Failed to create post';
                    this.submitting = false;
                    return;
                }
                var post = await resp.json();

                // Upload attached files
                for (var f of this.createFiles) {
                    var fd = new FormData();
                    fd.append('file', f);
                    await fetch('/api/v1/helpboard/posts/' + post.id + '/media', {
                        method: 'POST', body: fd
                    });
                }

                this.showCreate = false;
                this.createFiles = [];
                this.newPost = { help_type: 'need', title: '', body: '', category: 'power_tools', urgency: 'normal', neighborhood: '', content_language: (window.LP && window.LP.lang) || 'en' };
                this.page.offset = 0;
                await Promise.all([this.loadPosts(), this.loadSummary()]);
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Post created!' } }));
            } catch(e) {
                this.error = 'Network error';
            }
            this.submitting = false;
        },

        // ── Post detail ──

        async openPost(postId) {
            var resp = await fetch('/api/v1/helpboard/posts/' + postId);
            if (!resp.ok) return;
            this.activePost = await resp.json();
            this.isPostAuthor = false;
            // Check if current user is author
            try {
                var me = await fetch('/api/v1/users/me');
                if (me.ok) {
                    var user = await me.json();
                    this.userId = user.id;
                    this.isPostAuthor = user.id === this.activePost.author_id;
                }
            } catch(e) {}
            await this.loadReplies();
        },
        closePost() {
            this.activePost = null;
            this.replies = [];
            this.replyingTo = null;
            this.threadReplyBody = '';
            this.newReplyBody = '';
            this.replyFileSelected = null;
        },
        async loadReplies() {
            if (!this.activePost) return;
            var resp = await fetch('/api/v1/helpboard/posts/' + this.activePost.id + '/replies');
            if (resp.ok) this.replies = await resp.json();
        },

        // ── Upvote ──

        async toggleUpvote() {
            if (!this.activePost) return;
            var resp = await fetch('/api/v1/helpboard/posts/' + this.activePost.id + '/upvote', { method: 'POST' });
            if (resp.status === 401) { window.location.href = '/login'; return; }
            if (resp.ok) {
                var data = await resp.json();
                this.activePost.upvote_count = data.upvote_count;
                this.activePost.user_upvoted = data.action === 'upvoted';
            }
        },

        // ── Resolve ──

        async resolvePost(helperId, thankYouNote) {
            if (!this.activePost) return;
            var body = helperId ? { resolved_by_id: helperId } : {};
            var resp = await fetch('/api/v1/helpboard/posts/' + this.activePost.id + '/resolve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (resp.ok) {
                // Post thank-you note as a reply if provided
                if (thankYouNote && thankYouNote.trim()) {
                    await fetch('/api/v1/helpboard/posts/' + this.activePost.id + '/replies', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ body: thankYouNote.trim() })
                    });
                }
                await this.openPost(this.activePost.id);
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Post resolved! Thank you for using the Help Board.' } }));
            }
        },
        async deleteReply(replyId) {
            if (!confirm('Delete this reply?')) return;
            var resp = await fetch('/api/v1/helpboard/replies/' + replyId, { method: 'DELETE' });
            if (resp.ok) {
                await this.loadReplies();
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'info', message: 'Reply deleted' } }));
            }
        },

        // ── Reply ──

        async submitReply(parentReplyId) {
            var body = parentReplyId ? this.threadReplyBody : this.newReplyBody;
            if (!body.trim()) return;
            this.submittingReply = true;
            try {
                var payload = { body: body };
                if (parentReplyId) payload.parent_reply_id = parentReplyId;
                var resp = await fetch('/api/v1/helpboard/posts/' + this.activePost.id + '/replies', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (resp.status === 401) { window.location.href = '/login'; return; }
                if (resp.ok) {
                    var reply = await resp.json();
                    // Upload reply attachment if present and this is a top-level reply
                    if (!parentReplyId && this.replyFileSelected) {
                        var fd = new FormData();
                        fd.append('file', this.replyFileSelected);
                        await fetch('/api/v1/helpboard/replies/' + reply.id + '/media', {
                            method: 'POST', body: fd
                        });
                        this.replyFileSelected = null;
                        if (this.$refs.replyFileInput) this.$refs.replyFileInput.value = '';
                    }
                    // Reload replies
                    await this.loadReplies();
                    this.activePost.reply_count++;
                    if (parentReplyId) {
                        this.threadReplyBody = '';
                        this.replyingTo = null;
                    } else {
                        this.newReplyBody = '';
                    }
                }
            } catch(e) {}
            this.submittingReply = false;
        },

        // ── Media upload ──

        async deleteMedia(mediaId) {
            if (!confirm('Remove this attachment?')) return;
            var resp = await fetch('/api/v1/helpboard/media/' + mediaId, { method: 'DELETE' });
            if (resp.ok || resp.status === 204) {
                this.activePost.media = (this.activePost.media || []).filter(m => m.id !== mediaId);
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Attachment removed' } }));
            } else {
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Failed to delete' } }));
            }
        },
        async uploadPostMedia(event) {
            this.uploadError = '';
            var file = event.target.files[0];
            if (!file) return;
            if (file.size > 10 * 1024 * 1024) {
                this.uploadError = 'File too large (max 10MB)';
                return;
            }
            var fd = new FormData();
            fd.append('file', file);
            var resp = await fetch('/api/v1/helpboard/posts/' + this.activePost.id + '/media', {
                method: 'POST', body: fd
            });
            if (resp.ok) {
                var media = await resp.json();
                if (!this.activePost.media) this.activePost.media = [];
                this.activePost.media.push(media);
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Media uploaded!' } }));
            } else {
                var err = await resp.json().catch(() => ({}));
                this.uploadError = err.detail || 'Upload failed';
            }
            event.target.value = '';
        }
    };
}
