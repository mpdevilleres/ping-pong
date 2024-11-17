import asyncio
from enum import Enum, auto

import httpx

from src.logger import Instance, logger


class State(Enum):
    RUNNING = auto()
    PAUSE = auto()
    STOP = auto()


class Pinger:
    def __init__(self, server_name, destination_server_url, instance: Instance):
        self.state: State = State.STOP
        self.task = None
        self.pong_time_ms: int = 1000
        self.server_name = server_name
        self.destination_server_url = destination_server_url
        self.instance = instance

    async def ping_server(self):
        while self.state != State.STOP:
            try:
                if self.state == State.PAUSE:
                    logger.log(
                        self.instance,
                        "Pinger is paused. Waiting...",
                    )
                    while self.state == State.PAUSE:
                        await asyncio.sleep(0.5)

                if self.state == State.RUNNING:
                    await asyncio.sleep(self.pong_time_ms / 1000)
                    try:
                        async with httpx.AsyncClient(timeout=1.0) as client:
                            response = await client.get(
                                f"{self.destination_server_url}/ping",
                                params={"pong_time_ms": self.pong_time_ms},
                            )
                            logger.log(
                                self.instance,
                                f"pinging {self.destination_server_url} after {self.pong_time_ms} ms. "
                                f"response code: {response.status_code} message: {response.text}",
                            )
                    except httpx.RequestError as e:
                        logger.log(
                            self.instance,
                            f"Error while pinging server: {e}",
                        )
            except asyncio.CancelledError:
                logger.log(self.instance, "Pinger task was cancelled.")
                break

        logger.log(self.instance, "Pinger stopped.")

    def start(self, pong_time_ms):
        logger.log(self.instance, f"Pinger started with {pong_time_ms=}ms")
        if self.task is None or self.task.done():
            self.pong_time_ms = pong_time_ms
            self.state = State.RUNNING
            self.task = asyncio.create_task(self.ping_server())
        else:
            logger.log(self.instance, "Pinger is already running.")

    async def stop(self):
        logger.log(self.instance, "Stopping Pinger...")
        if self.state != State.STOP:
            self.state = State.STOP  # Update the state to STOP
            if self.task and not self.task.done():
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    logger.log(
                        self.instance,
                        "Task was successfully cancelled.",
                    )
                finally:
                    self.task = None
            logger.log(self.instance, "Pinger has stopped.")
        else:
            logger.log(self.instance, "Pinger is already stopped.")

    async def pause(self):
        logger.log(self.instance, "Pinger pause.")
        if self.state == State.RUNNING:
            self.state = State.PAUSE
        else:
            logger.log(
                self.instance,
                "Pinger is not running or already paused.",
            )

    async def resume(self):
        if self.state == State.PAUSE:
            self.state = State.RUNNING
        else:
            logger.log(self.instance, "Pinger is not paused.")

    async def status(self):
        return self.state
