import asyncio
import typer
import httpx

from src.factory import start_server, create_app

app = typer.Typer()

INSTANCE_ONE_URL = "http://localhost:9001"
INSTANCE_TWO_URL = "http://localhost:9002"


@app.command()
def runserver(instance_name: str, server_port: int, destination_port: int) -> None:
    app1 = create_app(server_name=instance_name, destination_server_url=f'http://localhost:{destination_port}')

    async def main():
        await start_server(app1, "0.0.0.0", server_port)

    asyncio.run(main())


@app.command()
def start(pong_time_ms: int):
    print(f'start game with {pong_time_ms=}')
    httpx.get(f"{INSTANCE_ONE_URL}/ping", params={"pong_time_ms": pong_time_ms})


@app.command()
def stop():
    httpx.get(f"{INSTANCE_ONE_URL}/stop")
    httpx.get(f"{INSTANCE_TWO_URL}/stop")


@app.command()
def pause():
    httpx.get(f"{INSTANCE_ONE_URL}/pause")
    httpx.get(f"{INSTANCE_TWO_URL}/pause")


@app.command()
def resume():
    httpx.get(f"{INSTANCE_ONE_URL}/resume")
    httpx.get(f"{INSTANCE_TWO_URL}/resume")


@app.command()
def status():
    response = httpx.get(f"{INSTANCE_ONE_URL}/status")
    print(f"[instance-1] {response.text}")
    response = httpx.get(f"{INSTANCE_TWO_URL}/status")
    print(f"[instance-2] {response.text}")


if __name__ == "__main__":
    app()
