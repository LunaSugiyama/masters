# Shop Floor Map

A responsive interactive map for a multi-floor shop with product search functionality.

## Features

- **Multi-floor Navigation**: Switch between 3 floors (Ground Floor, Second Floor, Third Floor)
- **Product Search**: Search for products by name, category, or area
- **Interactive Map**: Click on areas and products for more information
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Search**: Search results update as you type
- **Visual Indicators**: Products are highlighted on the map when found in search

## How to Use

1. **Open the Application**: Open `index.html` in a web browser
2. **Navigate Floors**: Click on floor buttons to switch between different floors
3. **Search Products**: Use the search bar to find specific products
4. **View Results**: Click on search results to navigate to the product location
5. **Explore Map**: Click on areas and products for detailed information

## Map Elements

- **Red Dots**: Product locations
- **Blue Areas**: Shopping sections (Electronics, Clothing, etc.)
- **Gray Areas**: Service areas (Restrooms, Customer Service, etc.)
- **Green Areas**: Entrances and exits
- **Orange Dots**: Highlighted search results

## Mobile Support

The map is fully responsive and optimized for:
- Desktop computers (1200px+)
- Tablets (768px - 1199px)
- Mobile phones (< 768px)

## Structure

- `index.html` - Main HTML structure
- `styles.css` - Responsive CSS styling
- `app.js` - JavaScript application logic
- `data.js` - Shop layout and product data

## Customization

To add more floors or products, edit the `shopData` object in `data.js`. Each floor can contain:
- Areas (sections, services, entrances)
- Products with specific coordinates
- Custom styling and colors