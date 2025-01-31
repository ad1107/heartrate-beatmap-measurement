import { LOCAL_WS_URL } from "./config.js";
import { updateChart, clearChart } from "./chart.js";

let state, timeelapsed, songTitle;
let prevTimeElapsed = 0;
let shouldUpdateChart = false;

export function connectToGosumemoryWebSocket() {
  let connection = new WebSocket(LOCAL_WS_URL);

  connection.onopen = () => console.log("Connected to Gosumemory");

  connection.onmessage = (event) => {
    try {
      let data = JSON.parse(event.data);
      let menu = data.menu;
      let newState = menu.state;
      songTitle = menu.bm.metadata.title;

      if (newState !== state) {
        if (newState === 2) {
          clearChart();
          shouldUpdateChart = true;
        } else {
          shouldUpdateChart = false;
        }
        state = newState;
      }

      if (menu.bm.time.current - menu.bm.time.firstObj < prevTimeElapsed) {
        clearChart();
      }

      prevTimeElapsed = timeelapsed;
      timeelapsed = menu.bm.time.current - menu.bm.time.firstObj;
    } catch (error) {
      console.error("Error parsing Gosumemory message:", error);
    }
  };

  connection.onclose = () => console.log("Gosumemory WebSocket Closed");
  connection.onerror = (error) => console.error("Gosumemory WebSocket Error:", error);
}
