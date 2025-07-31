class ShopMap {
    constructor() {
        this.currentFloor = 1;
        this.searchResults = [];
        this.highlightedProducts = [];
        
        this.initializeElements();
        this.setupEventListeners();
        this.generateFloorButtons();
        this.renderCurrentFloor();
    }
    
    initializeElements() {
        this.floorButtonsContainer = document.getElementById('floor-buttons');
        this.floorMapContainer = document.getElementById('floor-map');
        this.searchInput = document.getElementById('product-search');
        this.searchBtn = document.getElementById('search-btn');
        this.clearSearchBtn = document.getElementById('clear-search');
        this.searchResultsContainer = document.getElementById('search-results');
    }
    
    setupEventListeners() {
        this.searchBtn.addEventListener('click', () => this.handleSearch());
        this.clearSearchBtn.addEventListener('click', () => this.clearSearch());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleSearch();
            }
        });
        
        // Real-time search as user types
        this.searchInput.addEventListener('input', () => {
            if (this.searchInput.value.trim()) {
                this.handleSearch();
            } else {
                this.clearSearch();
            }
        });
    }
    
    generateFloorButtons() {
        this.floorButtonsContainer.innerHTML = '';
        
        Object.keys(shopData.floors).forEach(floorNumber => {
            const floor = shopData.floors[floorNumber];
            const button = document.createElement('button');
            button.className = `floor-btn ${floorNumber == this.currentFloor ? 'active' : ''}`;
            button.textContent = floor.name;
            button.addEventListener('click', () => this.switchFloor(parseInt(floorNumber)));
            
            this.floorButtonsContainer.appendChild(button);
        });
    }
    
    switchFloor(floorNumber) {
        this.currentFloor = floorNumber;
        this.updateFloorButtons();
        this.renderCurrentFloor();
        
        // Re-highlight search results if there are any
        if (this.searchResults.length > 0) {
            this.highlightSearchResults();
        }
    }
    
    updateFloorButtons() {
        const buttons = this.floorButtonsContainer.querySelectorAll('.floor-btn');
        buttons.forEach((button, index) => {
            const floorNumber = parseInt(Object.keys(shopData.floors)[index]);
            button.classList.toggle('active', floorNumber === this.currentFloor);
        });
    }
    
    renderCurrentFloor() {
        const floor = shopData.floors[this.currentFloor];
        this.floorMapContainer.innerHTML = '';
        
        // Calculate scale for responsive design
        const containerWidth = this.floorMapContainer.offsetWidth || 500;
        const containerHeight = this.floorMapContainer.offsetHeight || 400;
        const mapWidth = 500;
        const mapHeight = 250;
        
        const scaleX = containerWidth / mapWidth;
        const scaleY = containerHeight / mapHeight;
        const scale = Math.min(scaleX, scaleY, 1);
        
        // Render areas
        Object.entries(floor.areas).forEach(([areaId, area]) => {
            const areaElement = this.createAreaElement(area, scale);
            areaElement.dataset.areaId = areaId;
            this.floorMapContainer.appendChild(areaElement);
        });
        
        // Render products
        floor.products.forEach((product, index) => {
            const productElement = this.createProductElement(product, scale, index);
            this.floorMapContainer.appendChild(productElement);
        });
    }
    
    createAreaElement(area, scale) {
        const areaDiv = document.createElement('div');
        areaDiv.className = `area ${area.type}`;
        areaDiv.style.left = `${area.x * scale}px`;
        areaDiv.style.top = `${area.y * scale}px`;
        areaDiv.style.width = `${area.width * scale}px`;
        areaDiv.style.height = `${area.height * scale}px`;
        areaDiv.textContent = area.label;
        
        // Add click handler to show area info
        areaDiv.addEventListener('click', () => {
            this.showAreaInfo(area);
        });
        
        return areaDiv;
    }
    
    createProductElement(product, scale, index) {
        const productDiv = document.createElement('div');
        productDiv.className = 'product';
        productDiv.style.left = `${product.x * scale - 4}px`;
        productDiv.style.top = `${product.y * scale - 4}px`;
        productDiv.dataset.productIndex = index;
        productDiv.dataset.floor = this.currentFloor;
        
        // Add tooltip functionality
        productDiv.addEventListener('mouseenter', (e) => {
            this.showTooltip(e, product);
        });
        
        productDiv.addEventListener('mouseleave', () => {
            this.hideTooltip();
        });
        
        productDiv.addEventListener('click', () => {
            this.showProductInfo(product);
        });
        
        return productDiv;
    }
    
    showTooltip(event, product) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = product.name;
        
        document.body.appendChild(tooltip);
        
        const rect = event.target.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2}px`;
        tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
        
        this.currentTooltip = tooltip;
    }
    
    hideTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }
    
    showAreaInfo(area) {
        const floor = shopData.floors[this.currentFloor];
        const areaProducts = floor.products.filter(product => product.area === area.label.toLowerCase().replace(/[^a-z]/g, ''));
        
        let message = `Area: ${area.label}`;
        if (areaProducts.length > 0) {
            message += `\n\nProducts in this area:\n${areaProducts.map(p => `• ${p.name}`).join('\n')}`;
        }
        
        alert(message);
    }
    
    showProductInfo(product) {
        const floor = shopData.floors[this.currentFloor];
        alert(`Product: ${product.name}\nCategory: ${product.category}\nLocation: Floor ${this.currentFloor}, ${product.area} area`);
    }
    
    handleSearch() {
        const query = this.searchInput.value.trim().toLowerCase();
        if (!query) {
            this.clearSearch();
            return;
        }
        
        this.searchResults = [];
        
        // Search through all floors
        Object.entries(shopData.floors).forEach(([floorNumber, floor]) => {
            floor.products.forEach(product => {
                if (product.name.toLowerCase().includes(query) || 
                    product.category.toLowerCase().includes(query) ||
                    product.area.toLowerCase().includes(query)) {
                    
                    this.searchResults.push({
                        ...product,
                        floor: parseInt(floorNumber),
                        floorName: floor.name
                    });
                }
            });
        });
        
        this.displaySearchResults();
        this.highlightSearchResults();
    }
    
    displaySearchResults() {
        if (this.searchResults.length === 0) {
            this.searchResultsContainer.innerHTML = '<h4>Search Results</h4><p>No products found.</p>';
            return;
        }
        
        let html = '<h4>Search Results</h4>';
        this.searchResults.forEach(result => {
            html += `
                <div class="result-item" data-floor="${result.floor}" data-product="${result.name}">
                    <h5>${result.name}</h5>
                    <div class="result-location">${result.floorName} - ${result.area} area</div>
                </div>
            `;
        });
        
        this.searchResultsContainer.innerHTML = html;
        
        // Add click handlers to result items
        this.searchResultsContainer.querySelectorAll('.result-item').forEach(item => {
            item.addEventListener('click', () => {
                const floor = parseInt(item.dataset.floor);
                if (floor !== this.currentFloor) {
                    this.switchFloor(floor);
                }
                // Scroll to the product (simulate - in a real app you might pan/zoom to it)
                this.highlightSpecificProduct(item.dataset.product);
            });
        });
    }
    
    highlightSearchResults() {
        // Remove previous highlights
        this.clearHighlights();
        
        // Highlight products on current floor that match search
        const currentFloorResults = this.searchResults.filter(result => result.floor === this.currentFloor);
        
        currentFloorResults.forEach(result => {
            const productElements = this.floorMapContainer.querySelectorAll('.product');
            const floor = shopData.floors[this.currentFloor];
            
            floor.products.forEach((product, index) => {
                if (product.name === result.name) {
                    const productElement = productElements[index];
                    if (productElement) {
                        productElement.classList.add('highlighted');
                        this.highlightedProducts.push(productElement);
                    }
                }
            });
        });
    }
    
    highlightSpecificProduct(productName) {
        this.clearHighlights();
        
        const productElements = this.floorMapContainer.querySelectorAll('.product');
        const floor = shopData.floors[this.currentFloor];
        
        floor.products.forEach((product, index) => {
            if (product.name === productName) {
                const productElement = productElements[index];
                if (productElement) {
                    productElement.classList.add('highlighted');
                    this.highlightedProducts.push(productElement);
                    
                    // Scroll into view
                    productElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    }
    
    clearHighlights() {
        this.highlightedProducts.forEach(element => {
            element.classList.remove('highlighted');
        });
        this.highlightedProducts = [];
    }
    
    clearSearch() {
        this.searchInput.value = '';
        this.searchResults = [];
        this.searchResultsContainer.innerHTML = '';
        this.clearHighlights();
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const shopMap = new ShopMap();
    
    // Handle window resize to maintain responsiveness
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            shopMap.renderCurrentFloor();
            if (shopMap.searchResults.length > 0) {
                shopMap.highlightSearchResults();
            }
        }, 250);
    });
});