import { apiKey, HYPERATE_WS_URL } from "./config.js";
import { updateChart } from "./chart.js";

export function connectToHyperateWebSocket(ID) {
  let connection = new WebSocket(`${HYPERATE_WS_URL}?token=${apiKey}`);

  connection.onopen = () => {
    console.log("Connected to Hyperate");
    connection.send(JSON.stringify({ topic: `hr:${ID}`, event: "phx_join", payload: {}, ref: 0 }));
    setInterval(() => {
      connection.send(JSON.stringify({ topic: "phoenix", event: "heartbeat", payload: {}, ref: 0 }));
    }, 30000);
  };

  connection.onmessage = (message) => {
    let data = JSON.parse(message.data);
    if (data.event === "hr_update" && shouldUpdateChart) {
      let heartRate = data.payload.hr;
      if (heartRate !== 0) {
        updateChart(heartRate, timeelapsed, songTitle);
        document.documentElement.style.setProperty("--pulse-time", `${60000 / heartRate}ms`);
      }
    }
  };

  connection.onclose = () => console.log("Hyperate WebSocket Closed");
  connection.onerror = (error) => console.error("Hyperate WebSocket Error:", error);
}
