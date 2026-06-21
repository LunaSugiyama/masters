
import React, { useState } from 'react';
import { shopData } from '../data';
import Floor from './Floor';
import SearchBar from './SearchBar';
import FloorSelector from './FloorSelector';
import './Map.css';

const Map = () => {
  const [selectedFloor, setSelectedFloor] = useState(shopData.floors[0]);
  const [searchTerm, setSearchTerm] = useState('');

  const handleFloorChange = (floor) => {
    setSelectedFloor(floor);
  };

  const handleSearch = (term) => {
    setSearchTerm(term);
  };

  return (
    <div className="map-container">
      <SearchBar onSearch={handleSearch} />
      <FloorSelector floors={shopData.floors} onFloorChange={handleFloorChange} selectedFloor={selectedFloor} />
      <Floor floor={selectedFloor} searchTerm={searchTerm} />
    </div>
  );
};

export default Map;
