import React from "react";

export default function DataTable({ data = [] }) {
  return (
    <div className="data-table">
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Market</th>
            <th>Prices (sample)</th>
            <th>Sent</th>
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr><td colSpan="4" className="muted">No data yet — start simulation</td></tr>
          ) : (
            data.map((r, idx) => (
              <tr key={idx}>
                <td>{new Date(r.timestamp || r.created_at).toLocaleString()}</td>
                <td>{r.market_id}</td>
                <td>
                  {r.prices ? Object.entries(r.prices).slice(0,3).map(([k,v]) => `${k}: ${v}`).join(", ") : "-"}
                </td>
                <td>{r.sent ? <span className="badge ok">✓</span> : <span className="badge bad">✕</span>}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}