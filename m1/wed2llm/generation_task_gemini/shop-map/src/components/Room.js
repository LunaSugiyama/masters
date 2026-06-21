
import React from 'react';
import Product from './Product';

const Room = ({ room, searchTerm }) => {
  const filteredProducts = room.products.filter((product) =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className={`room ${filteredProducts.length > 0 ? 'highlight' : ''}`}>
      <h3>{room.name}</h3>
      <div className="product-container">
        {filteredProducts.map((product) => (
          <Product key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
};

export default Room;
