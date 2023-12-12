from aiohttp import web
from handler import project_handler, web_handler, device_handler, interaction_handler
from middlewares import database_middleware, socketio_middleware
from socketio_manager import SocketIOManager

# create web application
app = web.Application()

# init socketio
sio_mngr = SocketIOManager(app)

app.middlewares.append(database_middleware())
app.middlewares.append(socketio_middleware(sio_mngr))

# setup api handler
interaction_handler.setup(app)
project_handler.setup(app)
device_handler.setup(app)
web_handler.setup(app)

if __name__ == '__main__':
    web.run_app(app)
