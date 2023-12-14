from aiohttp import web
from socketio_manager import SocketIOManager


def setup(app: web.Application):
    app.router.add_get("/api/device", get_all_devices)


async def get_all_devices(request):
    sio_mngr: SocketIOManager = request["sio_mngr"]
    return web.json_response(sio_mngr.connected_devices)
