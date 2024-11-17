import asyncio
from typing import Annotated

import typer
import httpx
from src.logger import logger, Instance

from src.factory import start_server, create_app

cli = typer.Typer()

INSTANCE_ONE_URL = "http://localhost:9001"
INSTANCE_TWO_URL = "http://localhost:9002"


def _runserver(instance: Instance, server_port: int, destination_port: int):
    logger.log(instance, f"Starting {instance} pinging from {server_port} ➡️ {destination_port}")
    _app = create_app(
        server_name=instance,
        destination_server_url=f'http://localhost:{destination_port}',
        instance=instance
    )

    async def run():
        await start_server(_app, "0.0.0.0", server_port)

    return run


@cli.command()
def runserver(instance: Instance, server_port: int, destination_port: int) -> None:
    asyncio.run(_runserver(instance=instance, server_port=server_port, destination_port=destination_port)())


@cli.command()
def start(pong_time_ms: Annotated[int, typer.Argument()] = 1000) -> None:
    logger.log('cli', f'starting ping-pong with instance-1 and {pong_time_ms} ms')
    httpx.get(f"{INSTANCE_ONE_URL}/ping", params={"pong_time_ms": pong_time_ms})


@cli.command()
def stop() -> None:
    logger.log('cli', 'stopping ping-pong')
    httpx.get(f"{INSTANCE_ONE_URL}/stop")
    httpx.get(f"{INSTANCE_TWO_URL}/stop")


@cli.command()
def pause() -> None:
    logger.log('cli', 'pausing ping-pong')
    httpx.get(f"{INSTANCE_ONE_URL}/pause")
    httpx.get(f"{INSTANCE_TWO_URL}/pause")


@cli.command()
def resume() -> None:
    logger.log('cli', 'resuming ping-pong')
    httpx.get(f"{INSTANCE_ONE_URL}/resume")
    httpx.get(f"{INSTANCE_TWO_URL}/resume")


@cli.command()
def status() -> None:
    logger.log('cli', 'retrieving status')
    response = httpx.get(f"{INSTANCE_ONE_URL}/status")
    logger.log('cli', f"Instance 1: {response.text}")
    response = httpx.get(f"{INSTANCE_TWO_URL}/status")
    logger.log('cli', f"Instance 2: {response.text}")


if __name__ == "__main__":
    cli()
