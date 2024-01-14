# Your implementation in trying to get realtime json response.

import websockets, asyncio, json
from typing import Tuple
class OurWebsocketBase():
    def __init__(self, uri: str):
        self.uri = uri
        self.cache = {}
        self.awaiting = {}
        self.queue = []
        self.stopped = False
    async def on_message(self, message) -> None:
        self.cache["last_message"] = message
        self.awaiting["message"] = False
        return
    async def wait_for_message(self, check = lambda x: True) -> str | dict:
        self.awaiting["message"] = True
        while not self.awaiting.get("message") or not check(self.cache.get("last_message", "")): await asyncio.sleep(0.1)
        try:
            _final = json.loads(self.cache.get("last_message", ""))
        except json.JSONDecodeError:
            return self.cache.get("last_message", "")
        return _final

    async def before_wsloop(self, ws):
        pass
    async def after_wsloop(self, ws):
        pass
    async def connect_ws(self):
        async with websockets.connect(self.uri) as ws:
            self.websocket = ws
            await self.before_wsloop(ws)
            while not self.stopped:
                try:
                    # Create a event task on every message received.
                    asyncio.create_task(self.on_message(await ws.recv()))
                    for message in self.queue:
                        self.quene.remove(message)
                        await ws.send(message)
                except websockets.exceptions.ConnectionClosed:
                    self.stopped = True
                    break
            else:
                await self.after_wsloop(ws)
    def connect(self):
        asyncio.run(self.connect_ws())

class HyperateWebsocket(OurWebsocketBase):
    def __init__(self, api_key: str, code: str):
        super().__init__(uri="wss://app.hyperate.io/socket/websocket?token=" + api_key)
        self.code = code
        self.cache["latestHeartrate"] = 0
    async def on_message(self, message) -> None:
        await asyncio.sleep(0.01)
        await super().on_message(message)
        _resp = json.loads(message)
        _event = _resp.get("event")
        _topic = _resp.get("topic")
        assert isinstance(_event, str), _event
        if _topic == f"hr:{self.code}":
            match _event:
                case "hr_update":
                    _hr = _resp.get("payload").get("hr")
                    assert isinstance(_hr, int), _hr
                    self.cache["latestHeartrate"] = _hr

    async def wait_for_heartrate(self) -> int:
        # NOTE: Incomplete
        func = lambda x: json.loads(x).get("event") == "hr_update"
        _resp = await self.wait_for_message(func)
        return _resp.get("payload").get("hr")
    
    async def wait_for_heartrate_change(self) -> Tuple[int, int]:
        while True:
            _old = self.cache.get("latestHeartrate")
            _new = await self.wait_for_heartrate()
            if _old != _new:
                return (_old, _new)

    async def keep_alive(self, ws):
        while not self.stopped:
            asyncio.create_task(ws.send(json.dumps({ "topic": "phoenix", "event": "heartbeat", "payload": {}, "ref": 0 })))
            await asyncio.sleep(7)
    async def stop_on_phx_close(self):
        def _check(x):
            _event = json.loads(x).get("event")
            _topic = json.loads(x).get("topic")
            return _event == "phx_close" and _topic == f"hr:{self.code}"
        await self.wait_for_message(_check)
        self.stopped = True
        return 
    def _check_1(self, x):
        _event = json.loads(x).get("event")
        _topic = json.loads(x).get("topic")
        return _event == "phx_reply" and _topic == f"hr:{self.code}"
    async def before_wsloop(self, ws):
        task = asyncio.create_task(self.wait_for_message(self._check_1))
        _send1 = asyncio.create_task(ws.send(json.dumps({ "topic": f"hr:{self.code}", "event": "phx_join", "payload": {}, "ref": 0 })))
        await _send1
        await task
        _r = task.result()
        assert _r.get("payload").get("status") == "ok", _r
        asyncio.create_task(self.stop_on_phx_close())
        return asyncio.create_task(self.keep_alive(ws))
    async def after_wsloop(self, ws):
        print("Stopped gracefully") # DEBUG

    
    

# UNFINISHED
class RealtimeGosumemoryWebsocket(OurWebsocketBase):
    async def on_message(self, message):
        await super().on_message(message)
        try:
            _resp = json.loads(message)
        except json.JSONDecodeError:
            return # Idk what I should do in this situation
        _menu = _resp.get("menu")
        assert isinstance(_menu, dict), _menu
        _state = _menu.get("state")              # menu.state final output. 
        assert isinstance(_state, int), _state
        if _state != self.cache.get("currentState"):

            # print(f"State changed from {self.cache.get('currentState')} to {_state}")

            print("menu.state: ", _state)
            
            self.cache["currentState"] = _state


if __name__ == "__main__":
    handler = RealtimeGosumemoryWebsocket(uri="ws://localhost:24050/ws")
    handler.connect()