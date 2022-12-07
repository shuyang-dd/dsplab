import pyaudio
import websockets
import asyncio
import base64
import json

auth_key = "462b128affa344b181872384bf7a01cb"

BLOCKLEN = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"


class Transcripter:
    text = "111"

    def __init__(self) -> None:
        self.block_len = BLOCKLEN
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=BLOCKLEN
        )

    async def send_receive(self):
        print(f'Connecting websocket to url ${URL}')
        async with websockets.connect(
                URL,
                extra_headers=(("Authorization", auth_key),),
                ping_interval=5,
                ping_timeout=20
        ) as self._ws:
            await asyncio.sleep(0.1)
            print("Receiving SessionBegins ...")
            session_begins = await self._ws.recv()
            print(session_begins)
            print("Sending messages ...")

            async def send():
                while True:
                    try:
                        data = self.stream.read(self.block_len)
                        data = base64.b64encode(data).decode("utf-8")
                        json_data = json.dumps({"audio_data": str(data)})
                        await self._ws.send(json_data)
                    except websockets.exceptions.ConnectionClosedError as e:
                        print(e)
                        assert e.code == 4008
                        break
                    except Exception as e:
                        assert False, "Not a websocket 4008 error"
                    await asyncio.sleep(0.01)

                return True

            async def receive():
                while True:
                    try:

                        result_str = await self._ws.recv()
                        result_str = json.loads(result_str)['text']

                        Transcripter.text = result_str
                        print(result_str)
                        #print("self test"+self.text)

                    except websockets.exceptions.ConnectionClosedError as e:
                        print(e)
                        assert e.code == 4008
                        break
                    except Exception as e:
                        assert False, "Not a websocket 4008 error"

            send_result, receive_result = await asyncio.gather(send(), receive())

    def return_text(self):
        print(str(self.text))
        return self.text


ts = Transcripter()
asyncio.run(ts.send_receive())
