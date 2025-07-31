
import React from 'react';

const FloorSelector = ({ floors, onFloorChange, selectedFloor }) => {
  return (
    <div className="floor-selector">
      {floors.map((floor) => (
        <button
          key={floor.id}
          onClick={() => onFloorChange(floor)}
          className={selectedFloor.id === floor.id ? 'active' : ''}
        >
          {floor.name}
        </button>
      ))}
    </div>
  );
};

export default FloorSelector;
