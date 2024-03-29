from aiohttp import web
from handler import project_handler, web_handler, device_handler, interaction_handler
from middlewares import database_middleware, socketio_middleware
from socketio_manager import SocketIOManager
from database import Database
import config
import logging
import logging.handlers
import sys


def setup_logging():
    log_file_name = config.log_dir_path + "/zp-hub.log"
    formatter = logging.Formatter(
        "[%(levelname)s]%(asctime)s|%(filename)s - %(message)s"
    )
    handler = logging.handlers.TimedRotatingFileHandler(log_file_name, when="midnight")
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    if config.app_mode == 'develop':
        logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)


def init_app():
    setup_logging()

    # create web application
    app = web.Application()

    database = Database(config.zp_data_path)
    database.init()

    # init socketio
    sio_mngr = SocketIOManager(app, database)

    app.middlewares.append(database_middleware(database))
    app.middlewares.append(socketio_middleware(sio_mngr))

    # setup api handler
    interaction_handler.setup(app)
    project_handler.setup(app)
    device_handler.setup(app)
    web_handler.setup(app)

    logging.info("ZusammenPlayer HUB started")
    return app


if __name__ == "__main__":
    web.run_app(init_app(), access_log=None)
