import React, { useState } from "react";

/**
 * Controls: static UI for simulation options (UI only)
 * SimulationManager will read values directly from DOM via events or context;
 * here we provide a simple local UI that stores to localStorage for SimulationManager to read.
 */
export default function Controls() {
  const [deviceCount, setDeviceCount] = useState(() => Number(localStorage.getItem("sim.devices") || 5));
  const [intervalMs, setIntervalMs] = useState(() => Number(localStorage.getItem("sim.interval") || 2000));
  const [useBackend, setUseBackend] = useState(() => localStorage.getItem("sim.backend") === "true");

  function save() {
    localStorage.setItem("sim.devices", String(deviceCount));
    localStorage.setItem("sim.interval", String(intervalMs));
    localStorage.setItem("sim.backend", String(useBackend));
    // small feedback
    const el = document.createElement("div");
    el.className = "save-toast";
    el.textContent = "Saved";
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 900);
  }

  return (
    <div className="controls">
      <label>
        Number of devices
        <input type="number" min="1" max="200" value={deviceCount} onChange={(e) => setDeviceCount(Number(e.target.value))} />
      </label>

      <label>
        Interval (ms)
        <input type="number" min="200" step="100" value={intervalMs} onChange={(e) => setIntervalMs(Number(e.target.value))} />
      </label>

      <label className="row">
        <input type="checkbox" checked={useBackend} onChange={(e) => setUseBackend(e.target.checked)} /> Send to backend (POST /ingest)
      </label>

      <div className="controls-actions">
        <button onClick={save} className="btn primary">Save</button>
      </div>
    </div>
  );
}