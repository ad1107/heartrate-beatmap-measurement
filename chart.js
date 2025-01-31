import { mstommss, updateFooter, updateHeader } from "./utils.js";

let minHeartRate = Infinity;
let maxHeartRate = -Infinity;
let pausedData = [];

export const chartData = {
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
        borderColor: (ctx) => {
          return pausedData[ctx.p1DataIndex] ? "rgb(192, 57, 43)" : "rgb(22, 160, 133)";
        },
      },
    },
  ],
};

export const chartConfig = {
  type: "line",
  data: chartData,
  options: {
    scales: {
      x: { grid: { color: "#555" }, ticks: { color: "#e0e0e0", font: { size: 20 } } },
      y: { grid: { color: "#555" }, ticks: { color: "#e0e0e0", font: { size: 20 } } },
    },
    plugins: { legend: { display: false }, tooltips: { enabled: false } },
  },
};

export const myChart = new Chart(document.getElementById("myChart"), chartConfig);

export function updateChart(value, timeelapsed, songTitle) {
  let now = new Date();
  let formattedTime = mstommss(timeelapsed);

  updateHeader(songTitle);

  pausedData.push(timeelapsed !== prevTimeElapsed);
  chartData.labels.push(timeelapsed !== prevTimeElapsed ? formattedTime : "Paused");
  chartData.datasets[0].data.push(value);

  if (value < minHeartRate) minHeartRate = value;
  if (value > maxHeartRate) maxHeartRate = value;

  updateFooter(minHeartRate, maxHeartRate);
  myChart.update();

  document.getElementById("heartrate-current").innerText = `${value}`;
}

export function clearChart() {
  chartData.labels = [];
  chartData.datasets[0].data = [];
  pausedData = [];
  minHeartRate = Infinity;
  maxHeartRate = -Infinity;
  myChart.update();
}
