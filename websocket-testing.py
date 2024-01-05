# My code for testing a websocket website (localhost:24050/ws)

import asyncio
import json

import websockets

uri = "ws://localhost:24050/ws"

async def websocket_tester():
    try:
        async with websockets.connect(uri) as websocket:
            while True:
                user_input = input("Enter a variable (e.g., menu.mainMenu.bassDensity), 'all' or 'exit' ")

                if user_input.lower().strip() == 'exit': break

                await websocket.send(user_input)

                response = await websocket.recv()

                if user_input.lower().strip()=='all':
                    result = json.loads(response)
                    # Parsing included.
                    print(json.dumps(result, indent=2))


                try:
                    result = json.loads(response)
                    value = result
                    keys = user_input.split('.')

                    # Extract the corresponding value based on the provided keys
                    for key in keys:
                        if key in value:
                            value = value[key]
                        else:
                            if user_input.lower().strip()!='all':
                                print(f"The key '{key}' does not exist in the response.")
                            break
                    else:
                        print(f"{user_input}: {json.dumps(value, indent=2)}") 

                except json.JSONDecodeError:
                    print("Result:", response)
    except websockets.exceptions.ConnectionError:
        print("Error: Could not connect to the WebSocket server.")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(websocket_tester())
