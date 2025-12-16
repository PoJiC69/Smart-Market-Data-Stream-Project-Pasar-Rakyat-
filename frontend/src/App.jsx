import React, { useEffect, useState } from "react";
import { getOpenApiPaths, sendSampleIngest } from "./api";

export default function App() {
  const [paths, setPaths] = useState([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const p = await getOpenApiPaths();
        setPaths(p);
      } catch (err) {
        setMessage("Failed to fetch OpenAPI paths: " + (err.message || err));
      }
    })();
  }, []);

  async function handleSend() {
    setMessage("Sending sample ingest...");
    try {
      const res = await sendSampleIngest();
      setMessage("Response: " + JSON.stringify(res));
    } catch (err) {
      setMessage("Send failed: " + (err.message || JSON.stringify(err)));
    }
  }

  return (
    <div className="container">
      <header>
        <h1>Smart Market Dashboard (React)</h1>
        <p className="muted">Built with Vite + React — drop your real UI here.</p>
      </header>

      <section className="card">
        <h2>API Paths (OpenAPI)</h2>
        {paths.length ? (
          <ul className="paths">
            {paths.map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        ) : (
          <p>No paths loaded — backend might be offline.</p>
        )}
      </section>

      <section className="card">
        <h2>Quick Actions</h2>
        <button onClick={handleSend}>Send sample /ingest payload</button>
        <p className="message">{message}</p>
      </section>

      <footer className="foot">Tip: Replace this app with your full React/Vue dashboard build and copy to backend static folder.</footer>
    </div>
  );
}
