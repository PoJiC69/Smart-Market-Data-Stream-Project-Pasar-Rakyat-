// Dashboard frontend using Chart.js and WebSocket to update in real-time.
// The chart now visualizes impact via color-coded point backgrounds and tooltip details.

(() => {
  const marketInput = document.getElementById("marketInput");
  const commodityInput = document.getElementById("commodityInput");
  const regionInput = document.getElementById("regionInput");
  const loadBtn = document.getElementById("loadHistory");
  const connectBtn = document.getElementById("connectWs");
  const disconnectBtn = document.getElementById("disconnectWs");

  let ws = null;
  let chart = null;
  const maxPoints = 500;

  function impactToColor(score) {
    // score: 0..100
    // green (low) -> yellow (mid) -> red (high)
    const s = Math.min(Math.max(score, 0), 100);
    if (s <= 20) {
      return "rgba(75, 192, 192, 0.9)"; // green
    } else if (s <= 50) {
      return "rgba(255, 193, 7, 0.95)"; // yellow/orange
    } else if (s <= 80) {
      return "rgba(255, 140, 0, 0.95)"; // deep orange
    } else {
      return "rgba(220, 53, 69, 0.95)"; // red
    }
  }

  function createChart() {
    const ctx = document.getElementById("priceChart").getContext("2d");
    const cfg = {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Price",
            data: [],
            borderColor: "rgba(75, 192, 192, 1)",
            backgroundColor: "rgba(75, 192, 192, 0.05)",
            tension: 0.2,
            pointRadius: 5,
            pointHoverRadius: 7,
            // We will set pointBackgroundColor as an array alongside data
            pointBackgroundColor: [],
          },
        ],
      },
      options: {
        scales: {
          x: { type: "time", time: { tooltipFormat: "yyyy-MM-dd HH:mm:ss" }, title: { display: true, text: "Time" } },
          y: { title: { display: true, text: "Price (IDR)" } },
        },
        plugins: {
          legend: { display: true },
          tooltip: {
            callbacks: {
              label: function (context) {
                const p = context.raw;
                let lines = [];
                if (p && typeof p === "object") {
                  lines.push("Price: " + p.y);
                  if (p.impact_score !== undefined) {
                    lines.push("Impact: " + p.impact_score + " (" + p.dominant_factor + ")");
                    // show top 3 factors
                    if (p.factors_with_weights) {
                      const f = Object.entries(p.factors_with_weights)
                        .sort((a, b) => b[1] - a[1])
                        .slice(0, 3)
                        .map((it) => `${it[0]}:${it[1]}%`);
                      if (f.length) lines.push("Factors: " + f.join(", "));
                    }
                  }
                } else {
                  lines.push(context.formattedValue);
                }
                return lines;
              },
            },
          },
        },
        animation: { duration: 0 },
        responsive: true,
        maintainAspectRatio: false,
      },
    };
    chart = new Chart(ctx, cfg);
  }

  async function loadHistory() {
    const market = marketInput.value.trim();
    const commodity = commodityInput.value.trim();
    const region = regionInput.value.trim() || undefined;
    if (!market || !commodity) {
      alert("Please enter market and commodity.");
      return;
    }
    const params = new URLSearchParams({ market_id: market, commodity, limit: "500" });
    if (region) params.set("region", region);
    const res = await fetch(`/prices/history?${params.toString()}`);
    if (!res.ok) {
      alert("Failed to fetch history");
      return;
    }
    const data = await res.json();
    // data = [{timestamp, market_id, commodity, price, region, price_change, impact_score, ...}, ...]
    chart.data.labels = data.map((p) => new Date(p.timestamp));
    chart.data.datasets[0].data = data.map((p) => ({ x: new Date(p.timestamp), y: p.price, impact_score: p.impact_score, dominant_factor: p.dominant_factor, factors_with_weights: p.factors_with_weights }));
    chart.data.datasets[0].pointBackgroundColor = data.map((p) => impactToColor(p.impact_score || 0));
    chart.update();
  }

  function connectWebSocket() {
    const market = marketInput.value.trim();
    const commodity = commodityInput.value.trim();
    const region = regionInput.value.trim();
    // Build query params for initial subscription
    const params = new URLSearchParams();
    if (market) params.set("market_id", market);
    if (commodity) params.set("commodity", commodity);
    if (region) params.set("region", region);
    ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws/prices?` + params.toString());
    ws.onopen = () => {
      console.info("WebSocket connected");
      // Send subscribe message with explicit commodity list so server can filter
      ws.send(JSON.stringify({ action: "subscribe", market_id: market || null, commodities: commodity ? [commodity] : null, region: region || null }));
    };
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === "price_update" && msg.data && Array.isArray(msg.data)) {
          msg.data.forEach((p) => {
            const ts = new Date(p.timestamp);
            // push new data point (object carrying extra metadata)
            chart.data.labels.push(ts);
            chart.data.datasets[0].data.push({ x: ts, y: p.price, impact_score: p.impact_score, dominant_factor: p.dominant_factor, factors_with_weights: p.factors_with_weights });
            // push corresponding color
            chart.data.datasets[0].pointBackgroundColor.push(impactToColor(p.impact_score || 0));
            // keep size within maxPoints
            while (chart.data.labels.length > maxPoints) {
              chart.data.labels.shift();
              chart.data.datasets[0].data.shift();
              if (chart.data.datasets[0].pointBackgroundColor && chart.data.datasets[0].pointBackgroundColor.length)
                chart.data.datasets[0].pointBackgroundColor.shift();
            }
          });
          chart.update();
        }
      } catch (e) {
        console.error("Failed to parse WS message", e);
      }
    };
    ws.onclose = () => {
      console.info("WebSocket disconnected");
      ws = null;
    };
    ws.onerror = (e) => {
      console.error("WebSocket error", e);
    };
  }

  function disconnectWebSocket() {
    if (ws) {
      ws.close();
      ws = null;
    }
  }

  // init
  createChart();
  loadBtn.addEventListener("click", loadHistory);
  connectBtn.addEventListener("click", connectWebSocket);
  disconnectBtn.addEventListener("click", disconnectWebSocket);
})();