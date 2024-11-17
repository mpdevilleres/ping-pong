import logging

import uvicorn
from fastapi import FastAPI, Request

from src.logger import Instance, logger
from src.pinger import Pinger, State


def create_app(server_name, destination_server_url, instance: Instance):
    app = FastAPI()
    pinger = Pinger(
        server_name=server_name,
        destination_server_url=destination_server_url,
        instance=instance,
    )

    @app.get("/status")
    async def status():
        _status = await pinger.status()
        logger.log(instance, _status)
        return {"message": str(_status)}

    @app.get("/ping")
    async def ping(pong_time_ms: int, request: Request):
        logger.log(instance, f"got ping by {request.client.host}:{request.client.port}")
        if pinger.state != State.RUNNING:
            pinger.start(pong_time_ms=pong_time_ms)
        return {"message": "pong"}

    @app.get("/pause")
    async def pause():
        if pinger.state == State.RUNNING:
            logger.log(instance, "Pausing")
            await pinger.pause()
        else:
            logger.log(instance, "Pausing not possible, pinger not running")

        return {"message": "Pinger paused."}

    @app.get("/resume")
    async def resume():
        if pinger.state == State.PAUSE:
            logger.log(instance, "Resuming")
            await pinger.resume()
        else:
            logger.log(instance, "Resuming not possible, pinger not paused")

        return {"message": "Pinger resumed."}

    @app.get("/stop")
    async def stop():
        if pinger.state != State.STOP:
            logger.log(instance, "Stopping")
            await pinger.stop()
        else:
            logger.log(instance, "Stopping not possible, pinger is stop")
        return {"message": "Pinger stopped."}

    return app


async def start_server(app: FastAPI, host: str, port: int):
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level=logging.CRITICAL,  # this suppresses the logging of the API
    )
    server = uvicorn.Server(config)
    await server.serve()
