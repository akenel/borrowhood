/**
 * item-detail.js — Alpine factories for /items/{slug}
 *
 * Requires window.LP.item = { slug, name, firstImage, firstPrice,
 *   images, alts, types, listingIds, isOwner } to be set by template
 * before this loads.
 *
 * Extracted from item_detail.html on 2026-04-18.
 */

    // Image gallery component
    function imageGallery() {
        return {
            active: 0,
            zoomOpen: false,
            images: window.LP.item.images,
            alts: window.LP.item.alts,
            types: window.LP.item.types,
            isVideo(idx) { return this.types[idx] && (this.types[idx].includes('VIDEO') || this.types[idx].includes('video')); },
            init() {
                // Keyboard navigation
                this.$el.addEventListener('keydown', (e) => {
                    if (e.key === 'ArrowLeft') this.prev();
                    if (e.key === 'ArrowRight') this.next();
                });
            },
            next() { this.active = (this.active + 1) % this.images.length; },
            prev() { this.active = (this.active - 1 + this.images.length) % this.images.length; }
        };
    }

    // Auction panel component
    function auctionPanel(listingId, startingBid, bidIncrement, currency) {
        return {
            listingId,
            startingBid,
            bidIncrement,
            currency,
            currentPrice: null,
            totalBids: 0,
            auctionEnd: null,
            reserveMet: true,
            ended: false,
            endingSoon: false,
            bidAmount: null,
            bidding: false,
            bidSuccess: false,
            auctionExtended: false,
            minBid: startingBid || 0.01,
            countdown: { days: 0, hours: 0, minutes: 0, seconds: 0 },
            timer: null,

            async init() {
                await this.fetchSummary();
                this.timer = setInterval(() => this.updateCountdown(), 1000);
            },

            async fetchSummary() {
                try {
                    const resp = await fetch(`/api/v1/bids/summary?listing_id=${this.listingId}`);
                    if (resp.ok) {
                        const data = await resp.json();
                        this.totalBids = data.total_bids;
                        this.currentPrice = data.current_price;
                        this.reserveMet = data.reserve_met;
                        if (data.auction_end) {
                            this.auctionEnd = new Date(data.auction_end);
                        }
                        // Calculate minimum bid
                        if (this.currentPrice && this.totalBids > 0) {
                            this.minBid = this.currentPrice + this.bidIncrement;
                        } else {
                            this.minBid = this.startingBid || 0.01;
                        }
                        this.bidAmount = this.minBid;
                    }
                } catch (e) {
                    console.error('Failed to fetch auction summary:', e);
                }
            },

            updateCountdown() {
                if (!this.auctionEnd) return;
                const now = new Date();
                const diff = this.auctionEnd - now;

                if (diff <= 0) {
                    this.ended = true;
                    this.endingSoon = false;
                    this.countdown = { days: 0, hours: 0, minutes: 0, seconds: 0 };
                    if (this.timer) clearInterval(this.timer);
                    return;
                }

                this.endingSoon = diff < 300000; // 5 minutes
                this.countdown = {
                    days: Math.floor(diff / 86400000),
                    hours: Math.floor((diff % 86400000) / 3600000),
                    minutes: Math.floor((diff % 3600000) / 60000),
                    seconds: Math.floor((diff % 60000) / 1000)
                };
            },

            async placeBid() {
                if (!this.bidAmount || this.bidAmount < this.minBid) return;
                this.bidding = true;
                this.bidSuccess = false;
                this.auctionExtended = false;

                try {
                    const resp = await fetch('/api/v1/bids', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            listing_id: this.listingId,
                            amount: this.bidAmount
                        })
                    });

                    if (!resp.ok) {
                        const err = await resp.json();
                        throw new Error(err.detail || 'Bid failed');
                    }

                    const data = await resp.json();
                    this.bidSuccess = true;

                    if (data.auction_extended) {
                        this.auctionExtended = true;
                        this.auctionEnd = new Date(data.new_auction_end);
                    }

                    // Refresh summary
                    await this.fetchSummary();

                    // Auto-hide success message
                    setTimeout(() => {
                        this.bidSuccess = false;
                        this.auctionExtended = false;
                    }, 5000);

                } catch (err) {
                    window.dispatchEvent(new CustomEvent('toast', {
                        detail: { type: 'error', message: err.message }
                    }));
                } finally {
                    this.bidding = false;
                }
            },

            destroy() {
                if (this.timer) clearInterval(this.timer);
            }
        };
    }

    // Global date formatter (used by Q&A, reviews, and other components)
    function formatDate(dateStr) {
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
            return days[d.getUTCDay()] + ', ' + months[d.getUTCMonth()] + ' ' + day + suffix + ' ' + d.getUTCFullYear() + ', ' + h + ':' + String(m).padStart(2, '0') + ampm + ' UTC';
        } catch(e) { return ''; }
    }

    // Q&A component
    function listingQA() {
        var listingIds = window.LP.item.listingIds;
        return {
            questions: [],
            loaded: false,
            newQuestion: '',
            asking: false,
            isOwner: window.LP.item.isOwner,
            async init() {
                for (var lid of listingIds) {
                    try {
                        var resp = await fetch('/api/v1/listing-qa?listing_id=' + lid);
                        if (resp.ok) {
                            var data = await resp.json();
                            this.questions = this.questions.concat(data);
                        }
                    } catch(e) {}
                }
                this.loaded = true;
            },
            async askQuestion() {
                if (this.newQuestion.length < 5 || !listingIds.length) return;
                this.asking = true;
                try {
                    var resp = await fetch('/api/v1/listing-qa', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ listing_id: listingIds[0], question: this.newQuestion })
                    });
                    if (resp.ok) {
                        var qa = await resp.json();
                        this.questions.unshift(qa);
                        this.newQuestion = '';
                    }
                } catch(e) {}
                this.asking = false;
            },
            async answerQuestion(qa) {
                if (!qa._draft) return;
                try {
                    var resp = await fetch('/api/v1/listing-qa/' + qa.id + '/answer', {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ answer: qa._draft })
                    });
                    if (resp.ok) {
                        var updated = await resp.json();
                        qa.answer = updated.answer;
                        qa.answerer_name = updated.answerer_name;
                        qa.answered_at = updated.answered_at;
                    }
                } catch(e) {}
            }
        };
    }

    // Recently Viewed -- track this item and render strip
    (function() {
        var KEY = 'bh_recently_viewed';
        var MAX = 12;
        var current = {
            slug: window.LP.item.slug,
            name: window.LP.item.name,
            image: window.LP.item.firstImage,
            price: window.LP.item.firstPrice,
        };
        try {
            var items = JSON.parse(localStorage.getItem(KEY) || '[]');
            items = items.filter(function(i) { return i.slug !== current.slug; });
            items.unshift(current);
            if (items.length > MAX) items = items.slice(0, MAX);
            localStorage.setItem(KEY, JSON.stringify(items));
            // Render strip (skip current item)
            var others = items.filter(function(i) { return i.slug !== current.slug; });
            if (others.length > 0) {
                var container = document.getElementById('recently-viewed-strip');
                if (container) {
                    container.textContent = '';
                    others.forEach(function(item) {
                        var link = document.createElement('a');
                        link.href = '/items/' + encodeURIComponent(item.slug);
                        link.className = 'flex-shrink-0 w-32 group';
                        if (item.image) {
                            var img = document.createElement('img');
                            img.src = item.image;
                            img.alt = item.name;
                            img.className = 'w-32 h-24 rounded-lg object-cover group-hover:ring-2 group-hover:ring-indigo-400 transition-all';
                            link.appendChild(img);
                        } else {
                            var placeholder = document.createElement('div');
                            placeholder.className = 'w-32 h-24 rounded-lg bg-gray-100 flex items-center justify-center';
                            placeholder.innerHTML = '<svg class="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>';
                            link.appendChild(placeholder);
                        }
                        var nameP = document.createElement('p');
                        nameP.className = 'text-xs text-gray-600 mt-1 truncate group-hover:text-indigo-600';
                        nameP.textContent = item.name;
                        link.appendChild(nameP);
                        if (item.price) {
                            var priceP = document.createElement('p');
                            priceP.className = 'text-xs font-medium text-gray-900';
                            priceP.textContent = 'EUR ' + item.price;
                            link.appendChild(priceP);
                        }
                        container.appendChild(link);
                    });
                    container.parentElement.style.display = 'block';
                }
            }
        } catch(e) {}
    })();

    // Review section component -- best-in-class review system
    function reviewSection(ownerId) {
        return {
            ownerId,
            reviews: [],
            summary: {count: 0, average: 0, weighted_average: 0, star_distribution: {1:0,2:0,3:0,4:0,5:0}, subcategory_averages: null, recommend_rate: null},
            loaded: false,
            sortBy: 'recent',
            starFilter: null,
            expandedPhoto: null,

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

            // Write review modal state
            showReviewModal: false,
            completedRentals: [],
            rentalsLoaded: false,
            reviewConsent: false,
            submittingReview: false,
            reviewError: null,
            reviewPhotos: [],       // base64 previews
            reviewPhotoFiles: [],   // File objects
            newReview: {
                rental_id: '',
                rating: 0,
                title: '',
                body: '',
                would_recommend: null,
                rating_accuracy: null,
                rating_communication: null,
                rating_value: null,
                rating_timeliness: null,
            },

            async init() {
                await Promise.all([this.fetchReviews(), this.fetchSummary()]);
                this.loaded = true;
            },

            async fetchReviews() {
                try {
                    var url = '/api/v1/reviews?reviewee_id=' + this.ownerId + '&limit=50&sort=' + this.sortBy;
                    if (this.starFilter) url += '&rating=' + this.starFilter;
                    const resp = await fetch(url);
                    if (resp.ok) {
                        this.reviews = await resp.json();
                    }
                } catch (e) {
                    console.error('Failed to fetch reviews:', e);
                }
            },

            async fetchSummary() {
                try {
                    const resp = await fetch('/api/v1/reviews/summary/' + this.ownerId);
                    if (resp.ok) {
                        this.summary = await resp.json();
                    }
                } catch (e) {
                    console.error('Failed to fetch review summary:', e);
                }
            },

            filterByStar(star) {
                if (this.starFilter === star) {
                    this.starFilter = null;
                } else {
                    this.starFilter = star;
                }
                this.fetchReviews();
            },

            async voteReview(reviewId, helpful) {
                try {
                    const resp = await fetch('/api/v1/reviews/' + reviewId + '/vote', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({helpful: helpful})
                    });
                    if (resp.ok) {
                        const result = await resp.json();
                        const review = this.reviews.find(function(r) { return r.id === reviewId; });
                        if (review) {
                            review.helpful_count = result.helpful_count;
                            review.not_helpful_count = result.not_helpful_count;
                        }
                    } else if (resp.status === 401) {
                        window.location.href = '/login';
                    }
                } catch (e) {
                    console.error('Vote failed:', e);
                }
            },

            async openReviewModal() {
                this.showReviewModal = true;
                this.reviewError = null;
                this.reviewConsent = false;
                this.reviewPhotos = [];
                this.reviewPhotoFiles = [];
                this.newReview = {
                    rental_id: '',
                    rating: 0,
                    title: '',
                    body: '',
                    would_recommend: null,
                    rating_accuracy: null,
                    rating_communication: null,
                    rating_value: null,
                    rating_timeliness: null,
                };
                // Fetch completed rentals for this owner
                if (!this.rentalsLoaded) {
                    try {
                        const resp = await fetch('/api/v1/rentals?status=completed&role=renter');
                        if (resp.ok) {
                            this.completedRentals = await resp.json();
                        }
                    } catch (e) {
                        console.error('Failed to fetch rentals:', e);
                    }
                    this.rentalsLoaded = true;
                }
            },

            async submitReview() {
                if (!this.newReview.rental_id || !this.newReview.rating || !this.reviewConsent) return;
                this.submittingReview = true;
                this.reviewError = null;

                try {
                    var payload = {
                        rental_id: this.newReview.rental_id,
                        reviewee_id: this.ownerId,
                        rating: this.newReview.rating,
                        title: this.newReview.title || null,
                        body: this.newReview.body || null,
                        would_recommend: this.newReview.would_recommend,
                        rating_accuracy: this.newReview.rating_accuracy,
                        rating_communication: this.newReview.rating_communication,
                        rating_value: this.newReview.rating_value,
                        rating_timeliness: this.newReview.rating_timeliness,
                    };

                    const resp = await fetch('/api/v1/reviews', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(payload)
                    });

                    if (!resp.ok) {
                        const err = await resp.json();
                        this.reviewError = err.detail || 'Failed to submit review';
                        return;
                    }

                    const createdReview = await resp.json();

                    // Upload photos if any
                    for (var i = 0; i < this.reviewPhotoFiles.length; i++) {
                        var formData = new FormData();
                        formData.append('file', this.reviewPhotoFiles[i]);
                        await fetch('/api/v1/reviews/' + createdReview.id + '/photos', {
                            method: 'POST',
                            body: formData
                        });
                    }

                    // Refresh reviews and summary
                    this.showReviewModal = false;
                    await Promise.all([this.fetchReviews(), this.fetchSummary()]);

                    window.dispatchEvent(new CustomEvent('toast', {
                        detail: { type: 'success', message: 'Review published!' }
                    }));

                } catch (e) {
                    this.reviewError = 'Network error. Please try again.';
                    console.error('Submit review failed:', e);
                } finally {
                    this.submittingReview = false;
                }
            }
        };
    }
