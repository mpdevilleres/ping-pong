import asyncio
from enum import Enum, auto

import httpx


class State(Enum):
    RUNNING = auto()
    PAUSE = auto()
    STOP = auto()


class Pinger:
    def __init__(self, server_name, destination_server_url):
        self.state: State = State.STOP
        self.task = None
        self.pong_time_ms: int = 1000
        self.server_name = server_name
        self.destination_server_url = destination_server_url

    async def ping_server(self):
        while self.state != State.STOP:
            current_state = self.state
            if current_state == State.PAUSE:
                print(f"[{self.server_name}] Pinger is paused. Waiting...")
                while self.state == State.PAUSE:
                    await asyncio.sleep(0.5)
            elif current_state == State.RUNNING:
                await asyncio.sleep(self.pong_time_ms / 1000)
                response = httpx.get(
                    f"{self.destination_server_url}/ping",
                    params={'pong_time_ms': self.pong_time_ms},
                    timeout=1.0
                )
                print(
                    f"[{self.server_name}] pinged {self.destination_server_url} after {self.pong_time_ms} ms."
                    f"response code: {response.status_code} message: {response.text}"
                )

        print(f"[{self.server_name}] Pinger stopped.")

    def start(self, pong_time_ms):
        print(f"[{self.server_name}] Pinger started with {pong_time_ms=}ms")
        if self.task is None or self.task.done():
            self.pong_time_ms = pong_time_ms
            self.state = State.RUNNING
            self.task = asyncio.create_task(self.ping_server())
        else:
            raise Exception(f"[{self.server_name}] Pinger is already running.")

    async def stop(self):
        print(f"[{self.server_name}] Pinger stopped.")
        if self.state != State.STOP:
            self.state = State.STOP
            await self.task.cancel()
        else:
            raise Exception(f"[{self.server_name}] Pinger is not running.")

    async def pause(self):
        print(f"[{self.server_name}] Pinger pause.")
        if self.state == State.RUNNING:
            self.state = State.PAUSE
        else:
            raise Exception(f"[{self.server_name}] Pinger is not running or already paused.")

    async def resume(self):
        if self.state == State.PAUSE:
            self.state = State.RUNNING
        else:
            raise Exception(f"[{self.server_name}] Pinger is not paused.")

    async def status(self):
        return self.state
