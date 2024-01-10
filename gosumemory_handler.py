# Your implementation in trying to get realtime json response.

import websockets, asyncio, json
class RealtimeGosumemoryWebsocket():
    def __init__(self, uri: str):
        self.uri = uri
        self.cache = {}
    async def on_message(self, message):
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

    async def connect_ws(self):
        async with websockets.connect(self.uri) as ws:
            while True:
                try:
                    # Create an event task on every message received.
                    asyncio.create_task(self.on_message(await ws.recv()))
                except websockets.exceptions.ConnectionClosed:
                    # Connection closed.
                    break
    def connect(self):
        asyncio.run(self.connect_ws())

if __name__ == "__main__":
    handler = RealtimeGosumemoryWebsocket(uri="ws://localhost:24050/ws")
    handler.connect()


"""
To use this:

handler = RealtimeGosumemoryWebsocket(uri="ws://...", ...)
handler.connect()

Do you have the code to handle gosumemory json yet? You should give me so I can help you trigger events. It is suggested to stack our code in this class.


"""