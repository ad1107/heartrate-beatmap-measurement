# ÙNFINISHED

import websockets, asyncio, json
from typing import Tuple
class OurWebsocketBase():
    def __init__(self, uri: str):
        self.uri = uri
        self.cache = {"last_message": '{"null": "null"}'}
        self.awaiting = {}
        self.queue = []
        self.stopped = False
        self.connected = False
        self.connnection_event = asyncio.Event()
    async def on_message(self, message) -> None:
        #print('DEBUG on_message called')
        self.cache["last_message"] = message
        self.awaiting["message"] = False
        return
    async def wait_for_message(self, check = lambda x: True) -> str | dict:
        self.awaiting["message"] = True
        while (not self.awaiting.get("message")) or (not check(self.cache.get("last_message", "{}"))): pass
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
        #print("DEBUG blocking?")
        async with websockets.connect(self.uri) as ws:
            print('DEBUG Connected to websocket')
            self.connected = True
            self.websocket = ws
            await self.before_wsloop(ws)
            #print('DEBUG done beforeloop')
            self.connnection_event.set()
            while not self.stopped:
                try:
                    # Create a event task on every message received.
                    #print('DEBUG waiting for message')
                    message = await ws.recv()
                    #print('DEBUG received message')
                    asyncio.create_task(self.on_message(message))
                    #print('DEBUG create handler task')
                    for message in self.queue:
                        self.queue.remove(message)
                        await ws.send(message)
                except websockets.exceptions.ConnectionClosed:
                    self.stopped = True
                    break
            else:
                #print('DEBUG afterloop:')
                await self.after_wsloop(ws)
            #print('DEBUG broken')
    async def connect(self):
        #print('DEBUG connecting')
        task = asyncio.create_task(self.connect_ws())
        await self.connnection_event.wait()
        await asyncio.sleep(0)
        #print(task)
        while not self.connected: pass

class GosumemoryMenuStates():
    NotRunning = -1
    MainMenu = 0
    EditingMap = 1
    Playing = 2
    GameShutdownAnimation = 3
    SongSelectEdit = 4
    SongSelect = 5
    WIP_NoIdeaWhatThisIs = 6
    ResultsScreen = 7
    GameStartupAnimation = 10
    MultiplayerRooms = 11
    MultiplayerRoom = 12
    MultiplayerSongSelect = 13
    MultiplayerResultsscreen = 14
    OsuDirect = 15
    RankingTagCoop = 17
    RankingTeam = 18
    ProcessingBeatmaps = 19
    Tourney = 22
    Unknown = -2

class RealtimeGosumemoryWebsocket(OurWebsocketBase):
    def __init__(self, port: int = 24050, uri: str = None):
        if uri is None:
            uri = f"ws://localhost:{port}/ws"
        super().__init__(uri=uri)
        self.cache["menuState"] = GosumemoryMenuStates.NotRunning
    
    async def state_change_handler(self, state: int, menu: dict):
        """
        This function is used to detect & handle states from osu! to convert to our own state.
        """
    async def on_message(self, message) -> None:
        await asyncio.sleep(0.01)
        await super().on_message(message)
        _resp = json.loads(message)
        assert isinstance(_resp, dict), _resp
        _menu = _resp.get("menu")
        assert isinstance(_menu, dict), _menu
        _state = _menu.get("state")
        assert isinstance(_state, int), _state
        await self.state_change_handler(_state, _menu)
        self.cache["menuState"] = _state


    
class HyperateWebsocket(OurWebsocketBase):
    def __init__(self, api_key: str, code: str):
        super().__init__(uri="ws://app.hyperate.io/socket/websocket?token=" + api_key)
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
        print("DEBUG .")
        task = asyncio.create_task(self.wait_for_message(self._check_1))
        await ws.send(json.dumps({ "topic": f"hr:{self.code}", "event": "phx_join", "payload": {}, "ref": 0 }))
        print("DEBUG ..")
        print("DEBUG ...")
        #await task
        #_r = task.result()
        #assert _r.get("payload", {}).get("status") == "ok", _r
        asyncio.create_task(self.stop_on_phx_close())
        return asyncio.create_task(self.keep_alive(ws))
    async def after_wsloop(self, ws):
        print("Stopped gracefully") # DEBUG

    
    

# UNFINISHED



if __name__ == "__main__":
    handler = RealtimeGosumemoryWebsocket(uri="ws://localhost:24050/ws")
    handler.connect()