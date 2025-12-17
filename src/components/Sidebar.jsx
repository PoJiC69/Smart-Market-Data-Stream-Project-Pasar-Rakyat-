import React from "react";
import clsx from "clsx";

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="side-brand">
        <strong>PasarRakyat</strong>
      </div>
      <nav className="nav">
        <a className={clsx("nav-item", "active")}>Dashboard</a>
        <a className="nav-item">Devices</a>
        <a className="nav-item">Alerts</a>
        <a className="nav-item">Settings</a>
      </nav>
      <div className="sidebar-footer muted">Local dev</div>
    </aside>
  );
}