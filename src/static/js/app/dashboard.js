/**
 * dashboard.js — Alpine.js factories and helpers for /dashboard
 *
 * Requires window.LP to be set by the template before this script loads:
 *   window.LP.lang            — UI language code (en, it, etc.)
 *   window.LP.dbUserId        — Current user DB ID
 *   window.LP.t.telegramLinked, telegramUnlinkConfirm, telegramNotLinked,
 *                accountDeleteBlocked — i18n strings
 *
 * Extracted from dashboard.html on 2026-04-18 to enable browser caching
 * and reduce template size from 3958 to ~3300 lines.
 */

    // Dashboard items Load More

    // History tab with review + re-order support
    function deliveryTimeline(rentalId) {
        return {
            rentalId,
            tracking: null,
            loaded: false,
            async load() {
                try {
                    var resp = await fetch('/api/v1/deliveries/' + this.rentalId);
                    if (resp.ok) {
                        this.tracking = await resp.json();
                    }
                } catch(e) {}
                this.loaded = true;
            },
            async updateStatus(status, description) {
                try {
                    var resp = await fetch('/api/v1/deliveries/' + this.rentalId + '/status', {
                        method: 'PATCH',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({status: status, description: description})
                    });
                    if (resp.ok) {
                        this.tracking = await resp.json();
                        window.dispatchEvent(new CustomEvent('toast', {
                            detail: {type: 'success', message: status === 'confirmed' ? 'Receipt confirmed!' : 'Status updated'}
                        }));
                    } else {
                        var err = await resp.json().catch(function() { return {}; });
                        window.dispatchEvent(new CustomEvent('toast', {
                            detail: {type: 'error', message: err.detail || 'Failed to update'}
                        }));
                    }
                } catch(e) {
                    window.dispatchEvent(new CustomEvent('toast', {detail: {type: 'error', message: 'Network error'}}));
                }
            }
        };
    }

    function daySummary() {
        var today = new Date().toISOString().slice(0, 10);
        return {
            day: today,
            today: today,
            summary: { rentals_count: 0, earnings_eur: 0, hours_worked: 0, invoices_issued: 0, transactions: [] },
            loading: false,
            loadedOnce: false,
            generating: {},
            async load() {
                this.loading = true;
                try {
                    var r = await fetch('/api/v1/invoices/day-summary/' + this.day);
                    if (r.ok) this.summary = await r.json();
                } catch(e) {}
                this.loading = false;
                this.loadedOnce = true;
            },
            shiftDay(delta) {
                var d = new Date(this.day);
                d.setDate(d.getDate() + delta);
                var newDay = d.toISOString().slice(0, 10);
                if (newDay > this.today) return;
                this.day = newDay;
                this.load();
            },
            prettyDate(d) {
                if (!d) return '';
                return new Date(d).toLocaleDateString((window.LP && window.LP.lang) || 'en', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            },
            async generateInvoice(rentalId) {
                this.generating[rentalId] = true;
                try {
                    var r = await fetch('/api/v1/invoices/from-rental/' + rentalId, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({})
                    });
                    if (r.ok || r.status === 201) {
                        var inv = await r.json();
                        window.dispatchEvent(new CustomEvent('toast', {detail: {type:'success', message: 'Invoice ' + inv.invoice_number + ' generated'}}));
                        window.open('/invoices/' + inv.id + '/print', '_blank');
                        this.load();
                    } else {
                        var err = await r.json();
                        window.dispatchEvent(new CustomEvent('toast', {detail: {type:'error', message: err.detail || 'Failed'}}));
                    }
                } catch(e) {
                    window.dispatchEvent(new CustomEvent('toast', {detail: {type:'error', message: 'Network error'}}));
                }
                this.generating[rentalId] = false;
            }
        };
    }

    function invoicesTab() {
        return {
            invoices: [],
            loading: false,
            loadedOnce: false,
            role: 'provider',
            year: new Date().getFullYear(),
            thisYear: new Date().getFullYear(),
            async load() {
                this.loading = true;
                try {
                    var r = await fetch('/api/v1/invoices?role=' + this.role + '&year=' + this.year);
                    if (r.ok) this.invoices = await r.json();
                } catch(e) {}
                this.loading = false;
                this.loadedOnce = true;
            }
        };
    }

    function historyTab() {
        return {
            historyFilter: '',
            ordersOpen: true,
            incomingOpen: true,
            myReviews: {},
            reviewsLoaded: false,
            showReviewModal: false,
            isEdit: false,
            reviewRentalId: '',
            revieweeId: '',
            reviewItemName: '',
            reviewRating: 0,
            reviewTitle: '',
            reviewBody: '',
            rAccuracy: 0,
            rCommunication: 0,
            rValue: 0,
            rTimeliness: 0,
            wouldRecommend: null,
            reviewLocked: false,
            reviewSubmitting: false,
            existingReviewId: null,
            async loadMyReviews() {
                if (this.reviewsLoaded) return;
                try {
                    var resp = await fetch('/api/v1/reviews?reviewer_id=" + (window.LP && window.LP.dbUserId) + "&limit=100');
                    if (resp.ok) {
                        var reviews = await resp.json();
                        reviews.forEach(r => { this.myReviews[r.rental_id] = r; });
                    }
                } catch(e) {}
                this.reviewsLoaded = true;
            },
            openReviewModal(rentalId, revieweeId, itemName, isEdit) {
                this.reviewRentalId = rentalId;
                this.revieweeId = revieweeId;
                this.reviewItemName = itemName;
                this.isEdit = isEdit;
                if (isEdit && this.myReviews[rentalId]) {
                    var existing = this.myReviews[rentalId];
                    this.reviewRating = existing.rating;
                    this.reviewTitle = existing.title || '';
                    this.reviewBody = existing.body || '';
                    this.rAccuracy = existing.rating_accuracy || 0;
                    this.rCommunication = existing.rating_communication || 0;
                    this.rValue = existing.rating_value || 0;
                    this.rTimeliness = existing.rating_timeliness || 0;
                    this.wouldRecommend = existing.would_recommend;
                    this.reviewLocked = !!existing.owner_response;
                    this.existingReviewId = existing.id;
                } else {
                    this.reviewRating = 0;
                    this.reviewTitle = '';
                    this.reviewBody = '';
                    this.rAccuracy = 0;
                    this.rCommunication = 0;
                    this.rValue = 0;
                    this.rTimeliness = 0;
                    this.wouldRecommend = null;
                    this.reviewLocked = false;
                    this.existingReviewId = null;
                }
                this.showReviewModal = true;
            },
            async submitReview() {
                if (this.reviewRating === 0) return;
                this.reviewSubmitting = true;
                try {
                    var method = this.isEdit ? 'PUT' : 'POST';
                    var url = this.isEdit ? '/api/v1/reviews/' + this.existingReviewId : '/api/v1/reviews';
                    var resp = await fetch(url, {
                        method: method,
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            rental_id: this.reviewRentalId,
                            reviewee_id: this.revieweeId,
                            rating: this.reviewRating,
                            title: this.reviewTitle || null,
                            body: this.reviewBody || null,
                            content_language: document.documentElement.lang || 'en',
                            rating_accuracy: this.rAccuracy || null,
                            rating_communication: this.rCommunication || null,
                            rating_value: this.rValue || null,
                            rating_timeliness: this.rTimeliness || null,
                            would_recommend: this.wouldRecommend
                        })
                    });
                    if (resp.ok) {
                        var review = await resp.json();
                        this.myReviews[this.reviewRentalId] = review;
                        this.showReviewModal = false;
                        window.dispatchEvent(new CustomEvent('toast', {
                            detail: { type: 'success', message: this.isEdit ? 'Review updated!' : 'Review submitted!' }
                        }));
                    } else {
                        var err = await resp.json().catch(() => ({}));
                        window.dispatchEvent(new CustomEvent('toast', {
                            detail: { type: 'error', message: err.detail || 'Failed to submit review' }
                        }));
                    }
                } catch(e) {
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Network error' } }));
                }
                this.reviewSubmitting = false;
            }
        };
    }

    // Dashboard favorites (lazy-loaded, members + items with filtering & pagination)
    function dashboardFavorites() {
        return {
            favTab: 'members',
            favMembers: [],
            favItemsList: [],
            favLoading: false,
            favLoaded: false,
            favItemsLoading: false,
            favItemsLoaded: false,
            memberFilter: '',
            itemFilter: '',
            memberPage: 1,
            itemPage: 1,
            memberPageSize: 9,
            itemPageSize: 9,
            get memberBadges() {
                var badges = [...new Set(this.favMembers.map(f => f.favorite_user.badge_tier).filter(Boolean))];
                return badges.sort();
            },
            get filteredMembers() {
                if (!this.memberFilter) return this.favMembers;
                return this.favMembers.filter(f => f.favorite_user.badge_tier === this.memberFilter);
            },
            get paginatedMembers() {
                var start = (this.memberPage - 1) * this.memberPageSize;
                return this.filteredMembers.slice(start, start + this.memberPageSize);
            },
            get itemCategories() {
                var cats = [...new Set(this.favItemsList.map(i => i.category).filter(Boolean))];
                return cats.sort();
            },
            get filteredItems() {
                if (!this.itemFilter) return this.favItemsList;
                return this.favItemsList.filter(i => i.category === this.itemFilter);
            },
            get paginatedItems() {
                var start = (this.itemPage - 1) * this.itemPageSize;
                return this.filteredItems.slice(start, start + this.itemPageSize);
            },
            async loadFavorites() {
                if (this.favLoaded) return;
                this.favLoading = true;
                try {
                    var resp = await fetch('/api/v1/users/me/favorites');
                    if (resp.ok) this.favMembers = await resp.json();
                } catch(e) {}
                this.favLoading = false;
                this.favLoaded = true;
            },
            async loadItemFavorites() {
                if (this.favItemsLoaded) return;
                this.favItemsLoading = true;
                try {
                    var resp = await fetch('/api/v1/items/me/favorites');
                    if (resp.ok) this.favItemsList = await resp.json();
                } catch(e) {}
                this.favItemsLoading = false;
                this.favItemsLoaded = true;
            },
            async removeMemberFavorite(userId, favId) {
                var resp = await fetch('/api/v1/users/' + userId + '/favorite', { method: 'DELETE' });
                if (resp.ok) {
                    this.favMembers = this.favMembers.filter(f => f.id !== favId);
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'info', message: 'Removed from favorites' } }));
                }
            },
            async removeItemFavorite(itemId) {
                var resp = await fetch('/api/v1/items/' + itemId + '/favorite', { method: 'DELETE' });
                if (resp.ok) {
                    this.favItemsList = this.favItemsList.filter(i => i.id !== itemId);
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'info', message: 'Removed from favorites' } }));
                }
            }
        };
    }

    // Lock box component for owners (generate codes + dispute filing)
    function lockboxOwner(rentalId, status) {
        return {
            rentalId,
            status,
            processing: false,
            generating: false,
            codes: null,
            existingCodes: null,
            hasExistingCodes: false,
            locationHint: '',
            instructions: '',
            showDisputeForm: false,
            disputeReason: '',
            disputeDescription: '',
            filingDispute: false,

            async init() {
                if (this.status === 'approved') {
                    await this.checkExistingCodes();
                }
            },

            async updateStatus(newStatus, reason) {
                this.processing = true;
                try {
                    const resp = await fetch(`/api/v1/rentals/${this.rentalId}/status`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ status: newStatus, reason })
                    });
                    if (!resp.ok) { const err = await resp.json(); throw new Error(err.detail); }
                    window.location.reload();
                } catch (err) {
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: err.message } }));
                } finally { this.processing = false; }
            },

            async checkExistingCodes() {
                try {
                    const resp = await fetch(`/api/v1/lockbox/${this.rentalId}`);
                    if (resp.ok) {
                        this.existingCodes = await resp.json();
                        this.hasExistingCodes = true;
                    }
                } catch (e) { /* no codes yet */ }
            },

            async generateCodes() {
                this.generating = true;
                try {
                    const resp = await fetch(`/api/v1/lockbox/${this.rentalId}/generate`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            location_hint: this.locationHint || null,
                            instructions: this.instructions || null
                        })
                    });
                    if (!resp.ok) { const err = await resp.json(); throw new Error(err.detail); }
                    this.codes = await resp.json();
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Access codes generated!' } }));
                } catch (err) {
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: err.message } }));
                } finally { this.generating = false; }
            },

            async fileDispute() {
                this.filingDispute = true;
                try {
                    const resp = await fetch('/api/v1/disputes', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            rental_id: this.rentalId,
                            reason: this.disputeReason,
                            description: this.disputeDescription
                        })
                    });
                    if (!resp.ok) { const err = await resp.json(); throw new Error(err.detail); }
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Dispute filed successfully' } }));
                    setTimeout(() => window.location.reload(), 1500);
                } catch (err) {
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: err.message } }));
                } finally { this.filingDispute = false; }
            }
        };
    }

    // Telegram account linking
    function telegramLink() {
        return {
            linked: false,
            notifyEnabled: true,
            linkUrl: null,
            generating: false,
            toggling: false,
            unlinking: false,
            _pollInterval: null,

            async init() {
                await this.checkStatus();
            },

            async checkStatus() {
                try {
                    const resp = await fetch('/api/v1/telegram/status');
                    if (resp.ok) {
                        const data = await resp.json();
                        this.linked = data.linked;
                        this.notifyEnabled = data.notify_telegram;
                        if (this.linked && this._pollInterval) {
                            clearInterval(this._pollInterval);
                            this._pollInterval = null;
                            this.linkUrl = null;
                            window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: (window.LP && window.LP.t.telegramLinked) || 'Telegram linked' } }));
                        }
                    }
                } catch(e) { /* not logged in or network error */ }
            },

            async generateLink() {
                this.generating = true;
                try {
                    const resp = await fetch('/api/v1/telegram/link', { method: 'POST' });
                    if (!resp.ok) { const err = await resp.json(); throw new Error(err.detail); }
                    const data = await resp.json();
                    this.linkUrl = data.url;
                    // Poll for link completion every 3 seconds
                    this._pollInterval = setInterval(() => this.checkStatus(), 3000);
                    // Stop polling after 10 minutes (link expires)
                    setTimeout(() => {
                        if (this._pollInterval) {
                            clearInterval(this._pollInterval);
                            this._pollInterval = null;
                            if (!this.linked) this.linkUrl = null;
                        }
                    }, 600000);
                } catch (err) {
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: err.message } }));
                } finally { this.generating = false; }
            },

            async toggleNotifications() {
                this.toggling = true;
                try {
                    const resp = await fetch('/api/v1/telegram/toggle', {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ enabled: !this.notifyEnabled })
                    });
                    if (resp.ok) {
                        const data = await resp.json();
                        this.notifyEnabled = data.notify_telegram;
                    }
                } catch(e) {}
                finally { this.toggling = false; }
            },

            unlinkConfirm() {
                if (confirm((window.LP && window.LP.t.telegramUnlinkConfirm) || 'Unlink Telegram?')) {
                    this.doUnlink();
                }
            },

            async doUnlink() {
                this.unlinking = true;
                try {
                    const resp = await fetch('/api/v1/telegram/link', { method: 'DELETE' });
                    if (resp.ok) {
                        this.linked = false;
                        this.linkUrl = null;
                        window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'info', message: (window.LP && window.LP.t.telegramNotLinked) || 'Not linked' } }));
                    }
                } catch(e) {}
                finally { this.unlinking = false; }
            }
        };
    }

    // Account deletion
    function accountDelete() {
        return {
            deleting: false,
            showDeleteModal: false,
            confirmText: '',
            preview: null,
            loadingPreview: false,

            async loadPreview() {
                this.loadingPreview = true;
                try {
                    const resp = await fetch('/api/v1/users/me/delete-preview');
                    if (resp.ok) this.preview = await resp.json();
                } catch(e) {}
                this.loadingPreview = false;
            },

            async doDelete() {
                if (this.confirmText !== 'DELETE') return;
                this.deleting = true;
                try {
                    const resp = await fetch('/api/v1/users/me', { method: 'DELETE' });
                    if (!resp.ok) {
                        const err = await resp.json();
                        window.dispatchEvent(new CustomEvent('toast', {
                            detail: { type: 'error', message: err.detail || (window.LP && window.LP.t.accountDeleteBlocked) || 'Cannot delete' }
                        }));
                        this.deleting = false;
                        return;
                    }
                    // Server clears the httponly cookie in the response.
                    // Redirect to home -- nav will show Log In (no session).
                    window.location.href = '/';
                } catch (err) {
                    window.dispatchEvent(new CustomEvent('toast', {
                        detail: { type: 'error', message: err.message }
                    }));
                    this.deleting = false;
                }
            }
        };
    }

    // Dispute response component for renters
    function disputeRespond(rentalId) {
        return {
            rentalId,
            dispute: null,
            loading: false,
            responseText: '',
            submitting: false,

            async init() {
                await this.loadDispute();
            },

            async loadDispute() {
                this.loading = true;
                try {
                    const resp = await fetch('/api/v1/disputes?limit=1');
                    if (resp.ok) {
                        const disputes = await resp.json();
                        this.dispute = disputes.find(d => d.rental_id === this.rentalId);
                    }
                } catch (e) { /* network error */ }
                finally { this.loading = false; }
            },

            async submitResponse() {
                if (!this.dispute || this.responseText.length < 10) return;
                this.submitting = true;
                try {
                    const resp = await fetch(`/api/v1/disputes/${this.dispute.id}/respond`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ response: this.responseText })
                    });
                    if (!resp.ok) { const err = await resp.json(); throw new Error(err.detail); }
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Response submitted successfully' } }));
                    setTimeout(() => window.location.reload(), 1500);
                } catch (err) {
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: err.message } }));
                } finally { this.submitting = false; }
            }
        };
    }

    // Dispute resolution component for owners
    function disputeResolve(rentalId) {
        return {
            rentalId,
            dispute: null,
            loading: false,
            resolutionType: '',
            resolutionNotes: '',
            resolving: false,

            async init() {
                await this.loadDispute();
            },

            async loadDispute() {
                this.loading = true;
                try {
                    const resp = await fetch('/api/v1/disputes?limit=10');
                    if (resp.ok) {
                        const disputes = await resp.json();
                        this.dispute = disputes.find(d => d.rental_id === this.rentalId);
                    }
                } catch (e) { /* network error */ }
                finally { this.loading = false; }
            },

            async resolveDispute() {
                if (!this.dispute || !this.resolutionType) return;
                this.resolving = true;
                try {
                    const resp = await fetch(`/api/v1/disputes/${this.dispute.id}/resolve`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            resolution: this.resolutionType,
                            resolution_notes: this.resolutionNotes || null
                        })
                    });
                    if (!resp.ok) { const err = await resp.json(); throw new Error(err.detail); }
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Dispute resolved successfully' } }));
                    setTimeout(() => window.location.reload(), 1500);
                } catch (err) {
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: err.message } }));
                } finally { this.resolving = false; }
            }
        };
    }

    // Lock box component for renters (view + verify codes)
    function lockboxRenter(rentalId, status) {
        return {
            rentalId,
            status,
            loading: false,
            codes: null,
            verifying: false,

            async init() {
                if (this.status === 'approved' || this.status === 'picked_up') {
                    await this.fetchCodes();
                }
            },

            async fetchCodes() {
                this.loading = true;
                try {
                    const resp = await fetch(`/api/v1/lockbox/${this.rentalId}`);
                    if (resp.ok) {
                        this.codes = await resp.json();
                    }
                } catch (e) { /* no codes yet */ }
                finally { this.loading = false; }
            },

            async verifyCode(code) {
                if (!code) return;
                this.verifying = true;
                try {
                    const resp = await fetch(`/api/v1/lockbox/${this.rentalId}/verify`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ code })
                    });
                    if (!resp.ok) { const err = await resp.json(); throw new Error(err.detail); }
                    const data = await resp.json();
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: data.message } }));
                    setTimeout(() => window.location.reload(), 1500);
                } catch (err) {
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: err.message } }));
                } finally { this.verifying = false; }
            }
        };
    }
