import React, { useEffect, useRef, useState } from "react";
import { sendIngest } from "../api";

/**
 * SimulationManager
 * - Reads sim config from localStorage (set by Controls)
 * - When started, simulates N devices sending payloads every interval ms
 * - Emits onEmit(entry) for local UI updates (chart / table)
 * - If backend enabled, attempts sendIngest(payload) and marks sent status
 */
export default function SimulationManager({ onEmit }) {
  const timerRef = useRef(null);
  const [running, setRunning] = useState(false);
  const [stats, setStats] = useState({ sent: 0, failed: 0 });

  useEffect(() => {
    return () => stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function randomPrices() {
    // sample commodities
    const commodities = ["cabai", "bawang", "tomat", "kentang"];
    const base = { cabai: 15000, bawang: 9000, tomat: 7000, kentang: 5000 };
    const p = {};
    commodities.forEach((c) => {
      const variance = Math.round(base[c] * (Math.random() * 0.15 - 0.05));
      p[c] = base[c] + variance;
    });
    return p;
  }

  function makePayload(deviceId) {
    return {
      timestamp: new Date().toISOString(),
      market_id: `PASAR-${String(deviceId).padStart(3, "0")}`,
      region: "JAKARTA",
      prices: randomPrices()
    };
  }

  async function emitOne(deviceId) {
    const payload = makePayload(deviceId);
    const entry = { ...payload, sent: false, created_at: new Date().toISOString() };
    const useBackend = localStorage.getItem("sim.backend") === "true";
    if (useBackend) {
      try {
        const res = await sendIngest(payload);
        entry.sent = true;
        entry.details = res.details || null;
        setStats((s) => ({ ...s, sent: s.sent + 1 }));
      } catch (err) {
        entry.sent = false;
        setStats((s) => ({ ...s, failed: s.failed + 1 }));
      }
    } else {
      // mock: mark as "sent" locally
      entry.sent = true;
      setStats((s) => ({ ...s, sent: s.sent + 1 }));
    }
    onEmit && onEmit(entry);
  }

  function start() {
    if (running) return;
    const n = Number(localStorage.getItem("sim.devices") || 5);
    const interval = Number(localStorage.getItem("sim.interval") || 2000);

    // start timer that emits N events per tick (simultaneous devices)
    timerRef.current = setInterval(() => {
      for (let i = 1; i <= n; i++) {
        emitOne(i);
      }
    }, Math.max(200, interval));
    setRunning(true);
  }

  function stop() {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setRunning(false);
  }

  return (
    <div className="sim-manager">
      <div className="sim-controls">
        <button className="btn" onClick={start} disabled={running}>
          Start Simulation
        </button>
        <button className="btn danger" onClick={stop} disabled={!running}>
          Stop
        </button>
      </div>

      <div className="sim-status">
        <div>Running: <strong>{running ? "Yes" : "No"}</strong></div>
        <div>Sent: <strong>{stats.sent}</strong></div>
        <div>Failed: <strong>{stats.failed}</strong></div>
      </div>
    </div>
  );
}