import { apiKey } from "./config.js";

// Function to format milliseconds to mm:ss format
function mstommss(ms) {
  var isNeg = ms < 0;
  if (isNeg) ms = Math.abs(ms);
  var sec = Math.floor(ms / 1000);
  var min = Math.floor(sec / 60);
  sec = sec % 60;
  var res =
    (isNeg ? "-" : "") +
    (min < 10 ? "0" : "") +
    min +
    ":" +
    (sec < 10 ? "0" : "") +
    sec;
  return res;
}

var data = {
  labels: [],
  datasets: [
    {
      label: "Heartrate",
      data: [],
      borderColor: "rgb(149, 165, 166)",
      lineTension: 0.5,
      pointRadius: 5,
      pointBackgroundColor: "#ffffff",
      segment: {
        borderColor: (ctx, timeChanged) =>
          timeChanged ? "rgb(192, 57, 43)" : "rgb(22, 160, 133)",
      },
    },
  ],
};

let overflow = 14;
let steps = 3;

var config = {
  type: "line",
  data: data,
  options: {
    scales: {
      x: {
        grid: {
          color: "#555",
        },
        ticks: {
          maxRotation: 0,
          font: {
            size: 20,
          },
          color: "#e0e0e0",
          callback: function (value, index, values) {
            if (values.length > overflow) {
              return index % steps === 0 ? this.getLabelForValue(value) : "";
            }
            return this.getLabelForValue(value);
          },
        },
      },
      y: {
        grid: {
          color: "#555",
        },
        ticks: {
          font: {
            size: 20,
          },
          color: "#e0e0e0",
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltips: {
        enabled: false,
      },
    },
  },
};

var myChart = new Chart(document.getElementById("myChart"), config);

// Extract tracker ID from URL query parameter
const urlParams = new URLSearchParams(window.location.search);
const trackerID = urlParams.get("code");

if (trackerID) {
  connectToHyperateWebSocket(trackerID);
}

let state, timeelapsed, songTitle, timeChanged;
let shouldUpdateChart = false;
let prevTimeElapsed = 0;

function connectToHyperateWebSocket(ID) {
  const API_KEY = apiKey;
  const API_URL = `wss://app.hyperate.io/socket/websocket?token=${API_KEY}`;
  let connection = new WebSocket(API_URL);

  connection.onopen = () => {
    console.log("Hyperate WebSocket Connected");
    connection.send(
      JSON.stringify({
        topic: `hr:${ID}`,
        event: "phx_join",
        payload: {},
        ref: 0,
      })
    );

    setInterval(() => {
      connection.send(
        JSON.stringify({
          topic: "phoenix",
          event: "heartbeat",
          payload: {},
          ref: 0,
        })
      );
    }, 30000);
  };

  connection.onmessage = (message) => {
    const data = JSON.parse(message.data);
    if (data.event === "hr_update" && shouldUpdateChart) {
      const heartRate = data.payload.hr;
      if (heartRate != 0) {
        updateChart(heartRate);
        document.documentElement.style.setProperty(
          "--pulse-time",
          `${60000 / heartRate}ms`
        );
      }
    }
  };

  connection.onclose = () => {
    console.log("Hyperate WebSocket Closed");
  };

  connection.onerror = (error) => {
    console.error("Hyperate WebSocket Error: ", error);
  };
}

function connectToGosumemoryWebSocket() {
  const LOCAL_WS_URL = "ws://localhost:24050/ws";
  let localConnection = new WebSocket(LOCAL_WS_URL);

  localConnection.onopen = () => {
    console.log("Gosumemory WebSocket Connected");
  };

  localConnection.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      const menu = data.menu;
      const gameplay = data.gameplay;
      const newState = menu.state;
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

      prevTimeElapsed = timeelapsed;
      timeelapsed = menu.bm.time.current - menu.bm.time.firstObj;

      document.getElementById("footer").innerText = `${
        "State: " + state + " | Time Changed? " + timeChanged + "\n"
      }`;
    } catch (error) {
      console.error("Error parsing local WebSocket message:", error);
    }
  };

  localConnection.onclose = () => {
    console.log("Gosumemory WebSocket Closed");
  };

  localConnection.onerror = (error) => {
    console.error("Gosumemory WebSocket Error: ", error);
  };
}

connectToGosumemoryWebSocket();

function updateChart(value) {
  var now = new Date();
  now = now.getHours() + ":" + now.getMinutes() + ":" + now.getSeconds();

  document.getElementById("header").innerText = `Current song: ${songTitle}`;

  timeChanged = timeelapsed !== prevTimeElapsed;

  data.labels.push(mstommss(timeelapsed));
  data.datasets[0].data.push({
    x: mstommss(timeelapsed),
    y: value,
    timeChanged: timeChanged,
  });
  myChart.update();
  document.getElementById("heartrate-current").innerText = `${value}`;
}

function clearChart() {
  data.labels = [];
  data.datasets[0].data = [];
  myChart.update();
}
