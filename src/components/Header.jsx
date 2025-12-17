import React from "react";

export default function Header() {
  return (
    <header className="header">
      <div className="header-left">
        <h2>Smart Market Platform</h2>
        <span className="muted">Dashboard & Simulation</span>
      </div>
      <div className="header-right">
        <div className="brand">v0.1</div>
      </div>
    </header>
  );
}