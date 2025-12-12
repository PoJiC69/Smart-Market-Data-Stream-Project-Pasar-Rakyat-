// Dashboard frontend using Chart.js and WebSocket to update in real-time.
// Auto-refreshes chart when receiving data over WebSocket and when loading history.

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
            backgroundColor: "rgba(75, 192, 192, 0.1)",
            tension: 0.2,
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
    // data = [{timestamp, market_id, commodity, price, region}, ...]
    chart.data.labels = data.map((p) => new Date(p.timestamp));
    chart.data.datasets[0].data = data.map((p) => ({ x: new Date(p.timestamp), y: p.price }));
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
      // Optionally send subscribe message
      ws.send(JSON.stringify({ action: "subscribe", market_id: market || null, commodities: commodity ? [commodity] : null, region: region || null }));
    };
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === "price_update" && msg.data && Array.isArray(msg.data)) {
          msg.data.forEach((p) => {
            const ts = new Date(p.timestamp);
            chart.data.labels.push(ts);
            chart.data.datasets[0].data.push({ x: ts, y: p.price });
            // keep size within maxPoints
            while (chart.data.labels.length > maxPoints) {
              chart.data.labels.shift();
              chart.data.datasets[0].data.shift();
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