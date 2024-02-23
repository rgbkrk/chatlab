import React from "react";

export const ColorPalette = (props) => {
    return (
      <div>
        {props.colors.map(color => (
          <div key={color} style={{ backgroundColor: color, width: '50px', height: '50px', display: 'inline-block' }}></div>
        ))}
      </div>
    );
  };
