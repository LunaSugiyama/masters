const shopData = {
    floors: {
        1: {
            name: "Ground Floor",
            areas: {
                entrance: { x: 10, y: 10, width: 80, height: 20, type: "entrance", label: "Main Entrance" },
                electronics: { x: 20, y: 50, width: 150, height: 100, type: "section", label: "Electronics" },
                clothing: { x: 200, y: 50, width: 150, height: 100, type: "section", label: "Clothing" },
                shoes: { x: 370, y: 50, width: 100, height: 100, type: "section", label: "Shoes" },
                checkout: { x: 150, y: 180, width: 200, height: 40, type: "service", label: "Checkout Counters" },
                restroom: { x: 400, y: 180, width: 70, height: 40, type: "service", label: "Restrooms" }
            },
            products: [
                { name: "iPhone 15", category: "electronics", x: 50, y: 80, area: "electronics" },
                { name: "Samsung TV", category: "electronics", x: 120, y: 100, area: "electronics" },
                { name: "Laptop", category: "electronics", x: 80, y: 120, area: "electronics" },
                { name: "Headphones", category: "electronics", x: 140, y: 80, area: "electronics" },
                { name: "Jeans", category: "clothing", x: 230, y: 80, area: "clothing" },
                { name: "T-Shirt", category: "clothing", x: 280, y: 100, area: "clothing" },
                { name: "Jacket", category: "clothing", x: 320, y: 80, area: "clothing" },
                { name: "Dress", category: "clothing", x: 250, y: 120, area: "clothing" },
                { name: "Sneakers", category: "shoes", x: 400, y: 80, area: "shoes" },
                { name: "Boots", category: "shoes", x: 420, y: 120, area: "shoes" }
            ]
        },
        2: {
            name: "Second Floor",
            areas: {
                stairs: { x: 10, y: 10, width: 50, height: 30, type: "service", label: "Stairs" },
                elevator: { x: 70, y: 10, width: 30, height: 30, type: "service", label: "Elevator" },
                books: { x: 20, y: 60, width: 140, height: 80, type: "section", label: "Books & Media" },
                home: { x: 180, y: 60, width: 140, height: 80, type: "section", label: "Home & Garden" },
                sports: { x: 340, y: 60, width: 130, height: 80, type: "section", label: "Sports & Outdoor" },
                cafe: { x: 150, y: 160, width: 120, height: 60, type: "service", label: "Café" },
                customer_service: { x: 300, y: 160, width: 100, height: 40, type: "service", label: "Customer Service" }
            },
            products: [
                { name: "Novel", category: "books", x: 50, y: 100, area: "books" },
                { name: "Magazine", category: "books", x: 80, y: 80, area: "books" },
                { name: "DVD", category: "books", x: 120, y: 110, area: "books" },
                { name: "Cookbook", category: "books", x: 140, y: 90, area: "books" },
                { name: "Plant Pot", category: "home", x: 210, y: 90, area: "home" },
                { name: "Cushion", category: "home", x: 250, y: 110, area: "home" },
                { name: "Lamp", category: "home", x: 290, y: 80, area: "home" },
                { name: "Candle", category: "home", x: 200, y: 120, area: "home" },
                { name: "Basketball", category: "sports", x: 370, y: 90, area: "sports" },
                { name: "Tent", category: "sports", x: 420, y: 110, area: "sports" },
                { name: "Yoga Mat", category: "sports", x: 390, y: 120, area: "sports" }
            ]
        },
        3: {
            name: "Third Floor",
            areas: {
                stairs: { x: 10, y: 10, width: 50, height: 30, type: "service", label: "Stairs" },
                elevator: { x: 70, y: 10, width: 30, height: 30, type: "service", label: "Elevator" },
                toys: { x: 20, y: 60, width: 120, height: 80, type: "section", label: "Toys & Games" },
                beauty: { x: 160, y: 60, width: 120, height: 80, type: "section", label: "Beauty & Health" },
                food: { x: 300, y: 60, width: 170, height: 80, type: "section", label: "Food & Beverages" },
                storage: { x: 200, y: 160, width: 150, height: 50, type: "service", label: "Storage Area" }
            },
            products: [
                { name: "LEGO Set", category: "toys", x: 50, y: 90, area: "toys" },
                { name: "Board Game", category: "toys", x: 80, y: 110, area: "toys" },
                { name: "Puzzle", category: "toys", x: 110, y: 80, area: "toys" },
                { name: "Action Figure", category: "toys", x: 120, y: 120, area: "toys" },
                { name: "Shampoo", category: "beauty", x: 190, y: 80, area: "beauty" },
                { name: "Makeup", category: "beauty", x: 220, y: 100, area: "beauty" },
                { name: "Toothbrush", category: "beauty", x: 250, y: 120, area: "beauty" },
                { name: "Perfume", category: "beauty", x: 200, y: 110, area: "beauty" },
                { name: "Coffee", category: "food", x: 330, y: 90, area: "food" },
                { name: "Chocolate", category: "food", x: 370, y: 110, area: "food" },
                { name: "Snacks", category: "food", x: 420, y: 80, area: "food" },
                { name: "Water", category: "food", x: 450, y: 120, area: "food" }
            ]
        }
    }
};

const categories = {
    electronics: "#4A90E2",
    clothing: "#F5A623",
    shoes: "#7ED321",
    books: "#9013FE",
    home: "#FF6B6B",
    sports: "#50C878",
    toys: "#FF69B4",
    beauty: "#FF1493",
    food: "#FFD700"
};