from aiohttp import web
import socketio
import json
import logging


class SocketIOManager:
    ROOM_DEVICES = "room_devices"
    ROOM_WEB = "room_web_clients"

    connected_devices = []

    def __init__(self, app: web.Application):
        sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        sio.attach(app)
        self.sio = sio

        @sio.on("disconnect")
        async def disconnect(sid):
            # remove device from connected devices
            index = -1
            for i, device in enumerate(self.connected_devices):
                if device["sid"] == sid:
                    index = i
            if index != -1:
                del self.connected_devices[index]
            logging.info(sid, " disconnected")
            await sio.emit(
                "device-list", json.dumps(self.connected_devices), room=self.ROOM_WEB
            )

        @sio.on("register")
        async def register(sid, data):
            # check and put all devices in one room
            if data["type"] == "player":
                new_device = {"sid": sid}
                new_device["uid"] = data["uid"]
                new_device["name"] = data["name"]
                new_device["type"] = data["type"]
                self.connected_devices.append(new_device)
                await sio.enter_room(sid, self.ROOM_DEVICES)
                logging.info("device connected: ", sid)
            if data["type"] == "web":
                await sio.enter_room(sid, self.ROOM_WEB)
                logging.info("web ui connected: " + sid)
            await sio.emit(
                "device-list", json.dumps(self.connected_devices), room=self.ROOM_WEB
            )
