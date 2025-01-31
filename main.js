import { connectToGosumemoryWebSocket } from "./gosumemory.js";
import { connectToHyperateWebSocket } from "./hyperate.js";

const urlParams = new URLSearchParams(window.location.search);
const trackerID = urlParams.get("code");

if (trackerID) {
  connectToHyperateWebSocket(trackerID);
}

connectToGosumemoryWebSocket();
