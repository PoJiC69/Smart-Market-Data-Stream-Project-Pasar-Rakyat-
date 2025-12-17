import React from "react";

export default function ControlsBar({
  deviceCount,
  setDeviceCount,
  intervalMs,
  setIntervalMs,
  useBackend,
  setUseBackend,
  running,
  onStart,
  onStop,
  onEmitSample
}) {
  return (
    <div className="controls">
      <h3>Simulation Controls</h3>

      <label>
        Devices
        <input type="number" min="1" max="200" value={deviceCount} onChange={(e) => setDeviceCount(Number(e.target.value))} />
      </label>

      <label>
        Interval (ms)
        <input type="number" min="200" step="100" value={intervalMs} onChange={(e) => setIntervalMs(Number(e.target.value))} />
      </label>

      <label className="row">
        <input type="checkbox" checked={useBackend} onChange={(e) => setUseBackend(e.target.checked)} /> Send to backend
      </label>

      <div className="controls-actions">
        {!running ? (
          <button className="btn primary" onClick={onStart}>Start</button>
        ) : (
          <button className="btn danger" onClick={onStop}>Stop</button>
        )}
        <button className="btn" onClick={onEmitSample}>Emit sample</button>
      </div>
    </div>
  );
}