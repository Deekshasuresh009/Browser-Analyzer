import React from 'react';
export default function Spinner({size=18}) {
  return <div style={{width:size, height:size, borderRadius:50, border:`3px solid #e5e7eb`, borderTop:`3px solid #2563eb`, animation:'spin 1s linear infinite'}} />;
}
