import uvicorn
from fastapi import FastAPI

from src.pinger import Pinger, State


def create_app(server_name, destination_server_url):
    app = FastAPI()
    pinger = Pinger(server_name=server_name, destination_server_url=destination_server_url)

    @app.get("/status")
    async def status():
        _status = await pinger.status()
        return {"message": str(_status)}

    @app.get("/ping")
    async def ping(pong_time_ms: int):
        if pinger.state != State.RUNNING:
            pinger.start(pong_time_ms=pong_time_ms)
        return {"message": "pong"}

    @app.get("/pause")
    async def pause():
        if pinger.state != State.RUNNING:
            await pinger.pause()
        return {"message": "Pinger paused."}

    @app.get("/resume")
    async def resume():
        if pinger.state != State.PAUSE:
            await pinger.resume()
        return {"message": "Pinger resumed."}

    @app.get("/stop")
    async def stop():
        if pinger.state != State.RUNNING:
            await pinger.stop()
        return {"message": "Pinger stopped."}

    return app


async def start_server(app: FastAPI, host: str, port: int):
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()
