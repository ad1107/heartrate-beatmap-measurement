export function mstommss(ms) {
    let isNeg = ms < 0;
    if (isNeg) ms = Math.abs(ms);
    let sec = Math.floor(ms / 1000);
    let min = Math.floor(sec / 60);
    sec = sec % 60;
    return `${isNeg ? "-" : ""}${min < 10 ? "0" : ""}${min}:${sec < 10 ? "0" : ""}${sec}`;
  }
  
  export function updateFooter(minHeartRate, maxHeartRate) {
    document.getElementById("footer").innerText = `Min: ${minHeartRate} | Max: ${maxHeartRate}`;
  }
  
  export function updateHeader(songTitle) {
    document.getElementById("header").innerText = `Current song: ${songTitle}`;
  }
  