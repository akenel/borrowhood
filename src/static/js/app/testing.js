/**
 * testing.js — Alpine factory for /testing (QA dashboard)
 * Requires window.LP.username.
 */

function qaDashboard() {
    return {
        activeTab: 'tests',
        summary: { total_tests: 0, passed: 0, failed: 0, skipped: 0, blocked: 0, pending: 0, percent_complete: 0, total_bugs: 0, open_bugs: 0, critical_bugs: 0 },
        phases: [],
        tests: [],
        bugs: [],
        showBugModal: false,
        newBug: { title: '', description: '', severity: 'medium', category: 'functional', reported_by: window.LP.username, screenshot_data: '' },
        screenshotPreview: '',

        // Bug detail state
        selectedBug: null,
        bugActivities: [],
        bugFilters: { severity: '', status: '', category: '' },
        bugSearch: '',
        bugUpdateStatus: 'open',
        bugComment: '',
        bugAssignee: '',
        commitSha: '',
        commitMessage: '',
        editTitle: '',
        editDescription: '',
        editSeverity: 'medium',

        async api(url, options = {}) {
            const r = await fetch(url, { ...options, headers: { 'Content-Type': 'application/json', ...options.headers } });
            if (!r.ok) throw new Error(`API error: ${r.status}`);
            return r.json();
        },

        async loadAll() {
            try {
                const [s, p, t] = await Promise.all([
                    this.api('/api/v1/testing/summary'),
                    this.api('/api/v1/testing/phases'),
                    this.api('/api/v1/testing/tests'),
                ]);
                this.summary = s;
                this.phases = p;
                this.tests = t;
                await this.loadBugs();
            } catch (e) {
                console.error('Failed to load QA data:', e);
            }
        },

        async loadBugs() {
            try {
                const params = new URLSearchParams();
                if (this.bugSearch.trim()) params.set('q', this.bugSearch.trim());
                if (this.bugFilters.severity) params.set('severity', this.bugFilters.severity);
                if (this.bugFilters.status) params.set('status_filter', this.bugFilters.status);
                if (this.bugFilters.category) params.set('category', this.bugFilters.category);
                const qs = params.toString();
                this.bugs = await this.api('/api/v1/testing/bugs' + (qs ? '?' + qs : ''));
            } catch (e) {
                console.error('Failed to load bugs:', e);
            }
        },

        async toggleBugDetail(bug) {
            if (this.selectedBug?.id === bug.id) {
                this.selectedBug = null;
                this.bugActivities = [];
                return;
            }
            this.selectedBug = bug;
            this.bugUpdateStatus = bug.status;
            this.bugComment = '';
            this.bugAssignee = bug.assigned_to || '';
            this.commitSha = '';
            this.commitMessage = '';
            this.editTitle = bug.title;
            this.editDescription = bug.description || '';
            this.editSeverity = bug.severity;
            try {
                this.bugActivities = await this.api(`/api/v1/testing/bugs/${bug.id}/activities`);
            } catch (e) {
                this.bugActivities = [];
            }
        },

        async updateBugStatus(bug) {
            if (this.bugUpdateStatus === bug.status) return;
            try {
                const actor = window.LP.username;
                await this.api(`/api/v1/testing/bugs/${bug.id}`, {
                    method: 'PUT',
                    body: JSON.stringify({ status: this.bugUpdateStatus, actor }),
                });
                await this.loadBugs();
                // Refresh the summary too (open_bugs count changes)
                this.summary = await this.api('/api/v1/testing/summary');
                // Refresh detail
                const updated = this.bugs.find(b => b.id === bug.id);
                if (updated) {
                    this.selectedBug = updated;
                    this.bugUpdateStatus = updated.status;
                    this.bugActivities = await this.api(`/api/v1/testing/bugs/${bug.id}/activities`);
                }
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Bug status updated' } }));
            } catch (e) {
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Failed to update bug' } }));
            }
        },

        async addBugComment(bug) {
            if (!this.bugComment.trim()) return;
            try {
                const actor = window.LP.username;
                await this.api(`/api/v1/testing/bugs/${bug.id}`, {
                    method: 'PUT',
                    body: JSON.stringify({ comment: this.bugComment, actor }),
                });
                this.bugComment = '';
                this.bugActivities = await this.api(`/api/v1/testing/bugs/${bug.id}/activities`);
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Comment added' } }));
            } catch (e) {
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Failed to add comment' } }));
            }
        },

        async assignBug(bug) {
            try {
                const actor = window.LP.username;
                await this.api(`/api/v1/testing/bugs/${bug.id}`, {
                    method: 'PUT',
                    body: JSON.stringify({ assigned_to: this.bugAssignee || '', actor }),
                });
                await this.loadBugs();
                const updated = this.bugs.find(b => b.id === bug.id);
                if (updated) {
                    this.selectedBug = updated;
                    this.bugActivities = await this.api(`/api/v1/testing/bugs/${bug.id}/activities`);
                }
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: this.bugAssignee ? `Assigned to ${this.bugAssignee}` : 'Unassigned' } }));
            } catch (e) {
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Failed to assign bug' } }));
            }
        },

        async linkCommit(bug) {
            if (!this.commitSha.trim()) return;
            try {
                const actor = window.LP.username;
                await this.api(`/api/v1/testing/bugs/${bug.id}/commits`, {
                    method: 'POST',
                    body: JSON.stringify({ sha: this.commitSha.trim(), message: this.commitMessage || '', actor }),
                });
                this.commitSha = '';
                this.commitMessage = '';
                await this.loadBugs();
                const updated = this.bugs.find(b => b.id === bug.id);
                if (updated) {
                    this.selectedBug = updated;
                    this.bugActivities = await this.api(`/api/v1/testing/bugs/${bug.id}/activities`);
                }
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Commit linked' } }));
            } catch (e) {
                const msg = e.message.includes('409') ? 'Commit already linked' : 'Failed to link commit';
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: msg } }));
            }
        },

        async editBug(bug) {
            try {
                const actor = window.LP.username;
                const payload = { actor };
                if (this.editTitle !== bug.title) payload.title = this.editTitle;
                if (this.editDescription !== bug.description) payload.description = this.editDescription;
                if (this.editSeverity !== bug.severity) payload.severity = this.editSeverity;
                await this.api(`/api/v1/testing/bugs/${bug.id}`, {
                    method: 'PUT',
                    body: JSON.stringify(payload),
                });
                await this.loadBugs();
                const updated = this.bugs.find(b => b.id === bug.id);
                if (updated) {
                    this.selectedBug = updated;
                    this.editTitle = updated.title;
                    this.editDescription = updated.description || '';
                    this.editSeverity = updated.severity;
                }
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Bug updated' } }));
            } catch (e) {
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Failed to update bug' } }));
            }
        },

        async updateTest(testId, newStatus) {
            try {
                const tester = window.LP.username;
                await this.api(`/api/v1/testing/tests/${testId}`, {
                    method: 'PUT',
                    body: JSON.stringify({ status: newStatus, tester_name: tester }),
                });
                await this.loadAll();
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: `Test marked as ${newStatus}` } }));
            } catch (e) {
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Failed to update test' } }));
            }
        },

        async resetTests() {
            if (!confirm('Reset all tests to pending? This cannot be undone.')) return;
            try {
                await this.api('/api/v1/testing/tests/reset', { method: 'POST' });
                await this.loadAll();
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'All tests reset to pending' } }));
            } catch (e) {
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Failed to reset tests' } }));
            }
        },

        handleScreenshot(event) {
            const file = event.target.files[0];
            if (!file) return;
            if (file.size > 5 * 1024 * 1024) {
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Screenshot must be under 5MB' } }));
                event.target.value = '';
                return;
            }
            const reader = new FileReader();
            reader.onload = (e) => {
                this.screenshotPreview = e.target.result;
                this.newBug.screenshot_data = e.target.result;
            };
            reader.readAsDataURL(file);
        },

        async addScreenshotToBug(bug, event) {
            const file = event.target.files[0];
            if (!file) return;
            if (file.size > 5 * 1024 * 1024) {
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Screenshot must be under 5MB' } }));
                event.target.value = '';
                return;
            }
            const reader = new FileReader();
            reader.onload = async (e) => {
                try {
                    const actor = window.LP.username;
                    await this.api(`/api/v1/testing/bugs/${bug.id}`, {
                        method: 'PUT',
                        body: JSON.stringify({ screenshot_data: e.target.result, actor }),
                    });
                    await this.loadBugs();
                    const updated = this.bugs.find(b => b.id === bug.id);
                    if (updated) this.selectedBug = updated;
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Screenshot added' } }));
                } catch (err) {
                    window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Failed to add screenshot' } }));
                }
            };
            reader.readAsDataURL(file);
        },

        async submitBug() {
            try {
                const payload = { ...this.newBug };
                if (!payload.screenshot_data) delete payload.screenshot_data;
                await this.api('/api/v1/testing/bugs', {
                    method: 'POST',
                    body: JSON.stringify(payload),
                });
                this.showBugModal = false;
                this.screenshotPreview = '';
                this.newBug = { title: '', description: '', severity: 'medium', category: 'functional', reported_by: this.newBug.reported_by, screenshot_data: '' };
                await this.loadBugs();
                this.summary = await this.api('/api/v1/testing/summary');
                this.activeTab = 'bugs';
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message: 'Bug reported!' } }));
            } catch (e) {
                window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message: 'Failed to submit bug' } }));
            }
        },
    };
}
