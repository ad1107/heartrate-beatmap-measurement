import { apiKey } from "./config.js";

// Define the color change functions for the line graph
const down = (ctx, value) =>
  ctx.p0.parsed.y > ctx.p1.parsed.y ? value : undefined;
const up = (ctx, value) =>
  ctx.p0.parsed.y < ctx.p1.parsed.y ? value : undefined;
const stagnate = (ctx, value) =>
  ctx.p0.parsed.y == ctx.p1.parsed.y ? value : undefined;

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
        borderColor: (ctx) =>
          down(ctx, "rgb(192, 57, 43)") ||
          up(ctx, "rgb(22, 160, 133)") ||
          stagnate(ctx, "rgb(149, 165, 166)"),
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

let gameMode, state;

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
    if (data.event === "hr_update") {
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
      gameMode = gameplay.gameMode;
      state = menu.state;

      let finaltime;
      let timemp3 = mstommss(menu.bm.time.mp3 - menu.bm.time.firstObj);
      let timefull = mstommss(menu.bm.time.full - menu.bm.time.firstObj);
      let timecurrent = mstommss(menu.bm.time.current);
      let timeelapsed = mstommss(menu.bm.time.current - menu.bm.time.firstObj);
      if (state == 0 || state == 2 || state == 7) {
        if (menu.bm.time.mp3 != 0) finaltime = timeelapsed + " / " + timemp3;
        else if (menu.bm.time.full != 0)
          finaltime = timeelapsed + " / " + timefull;
        else finaltime = timeelapsed;
      } else {
        if (menu.bm.time.mp3 != 0) finaltime = timemp3;
        else if (menu.bm.time.full != 0) finaltime = timefull;
        else finaltime = "-";
      }

      document.getElementById("footer").innerText = `${
        "State: " + state + " Time:" + finaltime
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
  data.labels.push(now);
  data.datasets[0].data.push(value);
  myChart.update();
  document.getElementById("heartrate-current").innerText = `${value}`;
}
