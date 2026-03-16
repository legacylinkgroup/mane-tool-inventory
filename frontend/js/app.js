// Dark Mode Toggle
function toggleDarkMode() {
    document.documentElement.classList.toggle('dark');
    localStorage.setItem('darkMode', document.documentElement.classList.contains('dark'));
}

// Sidebar Layout (shared across all pages with sidebar)
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

// Dashboard App
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
        }
    };
}

// Inventory App (Alpine.js)
function inventoryApp() {
    return {
        // State
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

        // Initialize
        async init() {
            await this.loadFilters();
            await this.loadItems();
        },

        // Load dynamic filter options
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

        // Load items with filters
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
                alert('Failed to load inventory. Please try again.');
            } finally {
                this.loading = false;
            }
        },

        // Clear all filters
        clearFilters() {
            this.search = '';
            this.location = '';
            this.container = '';
            this.category = '';
            this.loadItems();
        }
    };
}

// Admin App
function adminApp() {
    return {
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

                if (data.success || response.ok) {
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
                window.location.href = '/api/export';
            } catch (error) {
                alert('Export failed: ' + error.message);
            }
        },

        async downloadQR() {
            try {
                window.location.href = '/api/qr/download';
            } catch (error) {
                alert('QR download failed: ' + error.message);
            }
        },

        wiping: false,
        wipeResult: null,

        async wipeDatabase() {
            const confirmation = prompt('This will permanently delete ALL items and containers.\n\nType WIPE to confirm:');
            if (confirmation !== 'WIPE') {
                if (confirmation !== null) alert('Wipe cancelled. You must type exactly "WIPE" to confirm.');
                return;
            }

            this.wiping = true;
            this.wipeResult = null;

            try {
                const response = await fetch('/api/wipe', { method: 'DELETE' });
                const data = await response.json();

                if (data.success) {
                    this.wipeResult = { success: true, message: data.message };
                    setTimeout(() => window.location.href = '/', 2000);
                } else {
                    this.wipeResult = { success: false, message: 'Wipe failed: ' + (data.detail || 'Unknown error') };
                }
            } catch (error) {
                this.wipeResult = { success: false, message: 'Wipe failed: ' + error.message };
            } finally {
                this.wiping = false;
            }
        }
    };
}

// Item Form App
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

        // Combobox state
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
                const response = await fetch(`/api/items?limit=1000`);
                const data = await response.json();
                if (!data.success || !data.data) {
                    alert('Could not load item. Please try again.');
                    return;
                }
                const item = data.data.find(i => i.id === this.itemId);

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

                    // Sync combobox search fields
                    this.comboboxState.location.search = this.item.location;
                    this.comboboxState.container_name.search = this.item.container_name;
                    this.comboboxState.category.search = this.item.category;
                }
            } catch (error) {
                alert('Failed to load item: ' + error.message);
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
                alert('Please fill in all required fields (Name, Category, Quantity, Location, Container Name)');
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

                    alert(this.isEditMode ? 'Item updated successfully!' : 'Item created successfully!');
                    window.location.href = '/inventory.html';
                } else {
                    alert('Failed to save item: ' + (data.detail || 'Unknown error'));
                }
            } catch (error) {
                alert('Failed to save item: ' + error.message);
            } finally {
                this.saving = false;
            }
        }
    };
}

// Containers App
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
