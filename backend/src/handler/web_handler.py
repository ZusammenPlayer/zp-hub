from aiohttp import web
import config
import json
import logging
from socketio_manager import SocketIOManager


def setup(app: web.Application):
    app.router.add_get("/api/debug/ping", debug_ping)
    app.router.add_post("/api/debug/play", debug_play)
    app.router.add_get("/", index_handler)
    app.router.add_static(
        "/", config.zp_web_client_path, show_index=True, follow_symlinks=True
    )


async def index_handler(_):
    with open(config.zp_web_client_path + "/index.html") as f:
        html = f.read()
        return web.Response(text=html, content_type="text/html")


async def debug_play(request):
    request_data = await request.json()
    payload = request_data["payload"]
    try:
        payload = json.loads(payload)
    except:
        logging.info("cannot parse json")
    return web.json_response({})


async def debug_ping(request):
    sio_mngr: SocketIOManager = request["sio_mngr"]
    print(sio_mngr.connected_devices)
