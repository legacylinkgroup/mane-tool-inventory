// ============================================================
// Global Toast Notification System
// ============================================================
function showToast(message, type = 'success', duration = 3000) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none';
        document.body.appendChild(container);
    }

    const colors = {
        success: 'bg-green-600',
        error: 'bg-red-600',
        info: 'bg-blue-600'
    };
    const icons = {
        success: `<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`,
        error: `<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>`,
        info: `<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M12 2a10 10 0 100 20 10 10 0 000-20z"/></svg>`
    };

    const toast = document.createElement('div');
    toast.className = `${colors[type] || colors.info} text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 pointer-events-auto transform translate-x-full transition-transform duration-300 max-w-sm`;
    toast.innerHTML = `${icons[type] || icons.info}<span class="text-sm font-medium">${message}</span>`;
    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.remove('translate-x-full');
        toast.classList.add('translate-x-0');
    });

    setTimeout(() => {
        toast.classList.remove('translate-x-0');
        toast.classList.add('translate-x-full');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ============================================================
// Global Confirmation Modal System
// ============================================================
function confirmModal() {
    return {
        _modal: {
            show: false,
            title: '',
            message: '',
            confirmText: 'Confirm',
            confirmClass: 'bg-red-600 hover:bg-red-700',
            inputRequired: false,
            inputLabel: '',
            inputValue: '',
            inputMatch: '',
            onConfirm: null
        },

        openConfirmModal(title, message, callback, opts = {}) {
            this._modal.title = title;
            this._modal.message = message;
            this._modal.onConfirm = callback;
            this._modal.confirmText = opts.confirmText || 'Confirm';
            this._modal.confirmClass = opts.confirmClass || 'bg-red-600 hover:bg-red-700';
            this._modal.inputRequired = opts.inputRequired || false;
            this._modal.inputLabel = opts.inputLabel || '';
            this._modal.inputValue = '';
            this._modal.inputMatch = opts.inputMatch || '';
            this._modal.show = true;
        },

        closeModal() {
            this._modal.show = false;
            this._modal.onConfirm = null;
        },

        doConfirm() {
            if (this._modal.inputRequired && this._modal.inputValue !== this._modal.inputMatch) {
                showToast(`You must type exactly "${this._modal.inputMatch}" to confirm.`, 'error');
                return;
            }
            if (this._modal.onConfirm) this._modal.onConfirm();
            this._modal.show = false;
        }
    };
}

// Shared modal HTML template — inject via Alpine x-if
// Each page includes the modal markup in its HTML

// ============================================================
// Dark Mode Toggle
// ============================================================
function toggleDarkMode() {
    document.documentElement.classList.toggle('dark');
    localStorage.setItem('darkMode', document.documentElement.classList.contains('dark'));
}

// ============================================================
// Sidebar Layout (shared across all pages with sidebar)
// ============================================================
function sidebarLayout() {
    return {
        sidebarOpen: false,
        currentPath: window.location.pathname,
        isActive(path) {
            if (path === '/') return this.currentPath === '/';
            return this.currentPath.startsWith(path);
        }
    };
}

// ============================================================
// Dashboard App
// ============================================================
function dashboardApp() {
    return {
        stats: {
            total_items: 0,
            total_containers: 0,
            total_quantity: 0,
            total_value: 0
        },
        recentItems: [],
        lowStockItems: [],
        loading: true,

        async init() {
            try {
                const response = await fetch('/api/dashboard');
                const data = await response.json();
                if (data.success) {
                    this.stats = data.data;
                    this.recentItems = data.data.recent_items || [];
                    this.lowStockItems = data.data.low_stock_items || [];
                }
            } catch (error) {
                console.error('Failed to load dashboard:', error);
            } finally {
                this.loading = false;
            }
        },

        async shareRestockList() {
            const items = this.lowStockItems;
            if (!items.length) {
                showToast('No low stock items to share', 'info');
                return;
            }

            const lines = items.map(i => {
                const need = (i.low_stock_threshold || 5) - i.quantity;
                return `${need > 0 ? need : 1}x ${i.name}`;
            });
            const text = `Need to restock:\n${lines.join('\n')}`;

            if (navigator.share) {
                try {
                    await navigator.share({ title: 'Restock List', text });
                } catch (e) {
                    if (e.name !== 'AbortError') {
                        await navigator.clipboard.writeText(text);
                        showToast('Restock list copied to clipboard', 'success');
                    }
                }
            } else {
                try {
                    await navigator.clipboard.writeText(text);
                    showToast('Restock list copied to clipboard', 'success');
                } catch {
                    showToast('Could not copy to clipboard', 'error');
                }
            }
        }
    };
}

// ============================================================
// Inventory App (Alpine.js)
// ============================================================
function inventoryApp() {
    return {
        ...confirmModal(),
        items: [],
        filters: {
            locations: [],
            containers: [],
            categories: []
        },
        search: '',
        location: '',
        container: '',
        category: '',
        total: 0,
        loading: true,

        // Transfer modal state
        transferItem: null,
        transferOpen: false,
        transferSearch: '',
        transferContainer: '',
        transferLocation: '',

        async init() {
            await this.loadFilters();
            await this.loadItems();
        },

        async loadFilters() {
            try {
                const response = await fetch('/api/filters');
                const data = await response.json();
                if (data.success) {
                    this.filters = data.data;
                }
            } catch (error) {
                console.error('Failed to load filters:', error);
            }
        },

        async loadItems() {
            this.loading = true;
            try {
                const params = new URLSearchParams();
                if (this.search) params.append('search', this.search);
                if (this.location) params.append('location', this.location);
                if (this.container) params.append('container', this.container);
                if (this.category) params.append('category', this.category);
                params.append('limit', '100');

                const response = await fetch(`/api/items?${params.toString()}`);
                const data = await response.json();

                if (data.success) {
                    this.items = data.data;
                    this.total = data.total;
                }
            } catch (error) {
                console.error('Failed to load items:', error);
                showToast('Failed to load inventory. Please try again.', 'error');
            } finally {
                this.loading = false;
            }
        },

        clearFilters() {
            this.search = '';
            this.location = '';
            this.container = '';
            this.category = '';
            this.loadItems();
        },

        confirmDeleteItem(item) {
            this.openConfirmModal(
                'Delete Item',
                `Are you sure you want to delete "${item.name}"? This cannot be undone.`,
                () => this.deleteItem(item.id)
            );
        },

        async deleteItem(itemId) {
            try {
                const response = await fetch(`/api/item/${itemId}`, { method: 'DELETE' });
                const data = await response.json();
                if (data.success) {
                    this.items = this.items.filter(i => i.id !== itemId);
                    this.total = Math.max(0, this.total - 1);
                    showToast('Item deleted', 'success');
                } else {
                    showToast('Failed to delete item', 'error');
                }
            } catch (error) {
                showToast('Failed to delete item: ' + error.message, 'error');
            }
        },

        async updateQty(item, delta) {
            const newQty = Math.max(0, item.quantity + delta);
            const oldQty = item.quantity;
            item.quantity = newQty;

            try {
                const response = await fetch(`/api/item/${item.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ quantity: newQty })
                });
                const data = await response.json();
                if (!data.success) {
                    item.quantity = oldQty;
                    showToast('Failed to update quantity', 'error');
                }
            } catch (error) {
                item.quantity = oldQty;
                showToast('Failed to update quantity', 'error');
            }
        },

        openTransfer(item) {
            this.transferItem = item;
            this.transferSearch = '';
            this.transferContainer = '';
            this.transferLocation = '';
            this.transferOpen = true;
        },

        get filteredTransferContainers() {
            const boxes = this.filters.containers || [];
            if (!this.transferSearch) return boxes;
            return boxes.filter(c => c.toLowerCase().includes(this.transferSearch.toLowerCase()));
        },

        selectTransferContainer(name) {
            this.transferContainer = name;
            this.transferSearch = name;
        },

        async doTransfer() {
            if (!this.transferContainer || !this.transferLocation) {
                showToast('Select a container and enter a location', 'error');
                return;
            }
            try {
                const response = await fetch(`/api/item/${this.transferItem.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        container_name: this.transferContainer,
                        location: this.transferLocation
                    })
                });
                const data = await response.json();
                if (data.success) {
                    showToast(`Moved "${this.transferItem.name}" to ${this.transferContainer}`, 'success');
                    this.transferOpen = false;
                    await this.loadItems();
                } else {
                    showToast('Transfer failed', 'error');
                }
            } catch (error) {
                showToast('Transfer failed: ' + error.message, 'error');
            }
        }
    };
}

// ============================================================
// Admin App
// ============================================================
function adminApp() {
    return {
        ...confirmModal(),
        uploading: false,
        uploadResult: null,

        async uploadCSV(event) {
            const file = event.target.files[0];
            if (!file) return;

            this.uploading = true;
            this.uploadResult = null;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    this.uploadResult = {
                        success: true,
                        message: `Upload complete! ${data.summary.items_created} items created, ${data.summary.items_updated} items updated, ${data.summary.boxes_created} new containers.`,
                        details: data.summary
                    };
                } else {
                    this.uploadResult = {
                        success: false,
                        message: 'Upload failed: ' + (data.detail || 'Unknown error')
                    };
                }
            } catch (error) {
                console.error('Upload error:', error);
                this.uploadResult = {
                    success: false,
                    message: 'Upload failed: ' + error.message
                };
            } finally {
                this.uploading = false;
                event.target.value = '';
            }
        },

        async exportCSV() {
            try {
                const response = await fetch('/api/export');
                if (!response.ok) {
                    showToast('Export failed', 'error');
                    return;
                }
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url; a.download = 'inventory_export.csv'; a.click();
                URL.revokeObjectURL(url);
                showToast('Export downloaded', 'success');
            } catch (error) {
                showToast('Export failed: ' + error.message, 'error');
            }
        },

        async downloadQR() {
            try {
                const response = await fetch('/api/qr/download');
                if (!response.ok) {
                    showToast('QR download failed', 'error');
                    return;
                }
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url; a.download = 'qr_codes.pdf'; a.click();
                URL.revokeObjectURL(url);
                showToast('QR codes downloaded', 'success');
            } catch (error) {
                showToast('QR download failed: ' + error.message, 'error');
            }
        },

        wiping: false,
        wipeResult: null,

        startWipe() {
            this.openConfirmModal(
                'Wipe Database',
                'This will permanently delete ALL items and containers. This cannot be undone.',
                () => this.doWipe(),
                {
                    confirmText: 'Wipe Everything',
                    confirmClass: 'bg-red-600 hover:bg-red-700',
                    inputRequired: true,
                    inputLabel: 'Type WIPE to confirm',
                    inputMatch: 'WIPE'
                }
            );
        },

        async doWipe() {
            this.wiping = true;
            this.wipeResult = null;

            try {
                const response = await fetch('/api/wipe', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ confirm: 'WIPE' })
                });
                const data = await response.json();

                if (data.success) {
                    this.wipeResult = { success: true, message: data.message };
                    showToast('Database wiped successfully', 'success');
                    setTimeout(() => window.location.href = '/', 2000);
                } else {
                    this.wipeResult = { success: false, message: 'Wipe failed: ' + (data.detail || 'Unknown error') };
                    showToast('Wipe failed', 'error');
                }
            } catch (error) {
                this.wipeResult = { success: false, message: 'Wipe failed: ' + error.message };
                showToast('Wipe failed: ' + error.message, 'error');
            } finally {
                this.wiping = false;
            }
        }
    };
}

// ============================================================
// Item Form App
// ============================================================
function itemFormApp() {
    return {
        item: {
            name: '',
            category: '',
            quantity: 0,
            container_name: '',
            location: '',
            brand_platform: '',
            serial_number: '',
            estimated_value: '',
            dropbox_manual_url: '',
            low_stock_threshold: 5
        },
        containers: [],
        locations: [],
        categories: [],
        imageFile: null,
        imagePreview: null,
        uploading: false,
        saving: false,
        isEditMode: false,
        itemId: null,

        comboboxState: {
            location: { open: false, search: '' },
            container_name: { open: false, search: '' },
            category: { open: false, search: '' }
        },

        filteredLocations() {
            const search = this.comboboxState.location.search.toLowerCase();
            if (!search) return this.locations;
            return this.locations.filter(loc => loc.toLowerCase().includes(search));
        },

        filteredContainers() {
            const search = this.comboboxState.container_name.search.toLowerCase();
            if (!search) return this.containers;
            return this.containers.filter(c => c.toLowerCase().includes(search));
        },

        filteredCategories() {
            const search = this.comboboxState.category.search.toLowerCase();
            if (!search) return this.categories;
            return this.categories.filter(cat => cat.toLowerCase().includes(search));
        },

        selectOption(field, value) {
            this.item[field] = value;
            this.comboboxState[field].search = value;
            this.comboboxState[field].open = false;
        },

        handleComboInput(field) {
            this.item[field] = this.comboboxState[field].search;
            this.comboboxState[field].open = true;
        },

        openCombobox(field) {
            this.comboboxState[field].open = true;
        },

        async init() {
            const params = new URLSearchParams(window.location.search);
            this.itemId = params.get('id');

            if (this.itemId) {
                this.isEditMode = true;
                await this.loadItem();
            }

            await this.loadFilters();
        },

        async loadItem() {
            try {
                const response = await fetch(`/api/item/${this.itemId}`);
                const data = await response.json();
                if (!data.success || !data.data) {
                    showToast('Could not load item. Please try again.', 'error');
                    return;
                }
                const item = data.data;

                if (item) {
                    this.item = {
                        name: item.name,
                        category: item.category,
                        quantity: item.quantity,
                        container_name: item.boxes?.name || '',
                        location: item.boxes?.location || '',
                        brand_platform: item.brand_platform || '',
                        serial_number: item.serial_number || '',
                        estimated_value: item.estimated_value || '',
                        dropbox_manual_url: item.dropbox_manual_url || '',
                        low_stock_threshold: item.low_stock_threshold || 5
                    };
                    this.imagePreview = item.image_url;

                    this.comboboxState.location.search = this.item.location;
                    this.comboboxState.container_name.search = this.item.container_name;
                    this.comboboxState.category.search = this.item.category;
                }
            } catch (error) {
                showToast('Failed to load item: ' + error.message, 'error');
            }
        },

        async loadFilters() {
            try {
                const response = await fetch('/api/filters');
                const data = await response.json();
                if (data.success) {
                    this.containers = data.data.containers || [];
                    this.locations = data.data.locations || [];
                    this.categories = data.data.categories || [];
                }
            } catch (error) {
                console.error('Failed to load filters:', error);
            }
        },

        handleImageSelect(event) {
            const file = event.target.files[0];
            if (!file) return;

            this.imageFile = file;

            const reader = new FileReader();
            reader.onload = (e) => {
                this.imagePreview = e.target.result;
            };
            reader.readAsDataURL(file);
        },

        async uploadImage() {
            if (!this.imageFile || !this.itemId) return null;

            const formData = new FormData();
            formData.append('image', this.imageFile);

            try {
                const response = await fetch(`/api/item/${this.itemId}/upload-image`, {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                if (data.success) {
                    return data.data.image_url;
                }
            } catch (error) {
                console.error('Image upload failed:', error);
            }
            return null;
        },

        async saveItem() {
            if (!this.item.name || !this.item.category || this.item.quantity < 0 || !this.item.container_name || !this.item.location) {
                showToast('Please fill in all required fields (Name, Category, Quantity, Location, Container)', 'error');
                return;
            }

            this.saving = true;

            try {
                const endpoint = this.isEditMode ? `/api/item/${this.itemId}` : '/api/item';
                const method = this.isEditMode ? 'PUT' : 'POST';

                const response = await fetch(endpoint, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.item)
                });

                const data = await response.json();

                if (data.success) {
                    if (!this.isEditMode) {
                        this.itemId = data.data.id;
                    }

                    if (this.imageFile && this.itemId) {
                        await this.uploadImage();
                    }

                    showToast(this.isEditMode ? 'Item updated successfully!' : 'Item created successfully!', 'success');
                    setTimeout(() => { window.location.href = '/inventory.html'; }, 800);
                } else {
                    showToast('Failed to save item: ' + (data.detail || 'Unknown error'), 'error');
                }
            } catch (error) {
                showToast('Failed to save item: ' + error.message, 'error');
            } finally {
                this.saving = false;
            }
        }
    };
}

// ============================================================
// Containers App
// ============================================================
function containersApp() {
    return {
        boxes: [],
        loading: true,
        openBoxes: {},

        async init() {
            try {
                const response = await fetch('/api/containers');
                const data = await response.json();
                if (data.success) {
                    this.boxes = data.data;
                }
            } catch (error) {
                console.error('Failed to load containers:', error);
            } finally {
                this.loading = false;
            }
        },

        toggleBox(boxId) {
            this.openBoxes[boxId] = !this.openBoxes[boxId];
        },

        isBoxOpen(boxId) {
            return this.openBoxes[boxId] === true;
        }
    };
}
