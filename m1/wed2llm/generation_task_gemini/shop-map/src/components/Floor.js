
import React from 'react';
import Room from './Room';

const Floor = ({ floor, searchTerm }) => {
  return (
    <div className="floor">
      <h2>{floor.name}</h2>
      <div className="room-container">
        {floor.rooms.map((room) => (
          <Room key={room.id} room={room} searchTerm={searchTerm} />
        ))}
      </div>
    </div>
  );
};

export default Floor;
