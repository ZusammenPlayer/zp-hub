from aiohttp.web import middleware
from database import Database
from socketio_manager import SocketIOManager
import config


def database_middleware():
    database = Database(config.zp_data_path)
    database.init()

    @middleware
    async def inner(request, handler):
        request["db"] = database
        return await handler(request)

    return inner


def socketio_middleware(sio_mngr: SocketIOManager):
    @middleware
    async def inner(request, handler):
        request["sio_mngr"] = sio_mngr
        return await handler(request)

    return inner
