from aiohttp import web
import socketio
import json
import logging
from database import Database
import copy


class SocketIOManager:
    ROOM_DEVICES = "room_devices"
    ROOM_WEB = "room_web_clients"

    connected_devices = []

    def __merge_devices(self):
        # merge known devices with connected devices
        all_devices = []
        for known_device in self.database.get_devices():
            device_list_item = copy.deepcopy(known_device)
            active_device = None
            for connected_device in self.connected_devices:
                if known_device["uid"] == connected_device["uid"]:
                    active_device = connected_device
            if active_device is not None:
                device_list_item["online"] = True
            else:
                device_list_item["online"] = False
            all_devices.append(device_list_item)
        return all_devices

    def __init__(self, app: web.Application, database: Database):
        sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        sio.attach(app)
        self.sio = sio
        self.database = database

        @sio.on("disconnect")
        async def disconnect(sid):
            # remove device from connected devices
            index = -1
            for i, device in enumerate(self.connected_devices):
                if device["sid"] == sid:
                    index = i
            if index != -1:
                del self.connected_devices[index]
            logging.info(sid + " disconnected")
            all_devices = self.__merge_devices()
            await sio.emit(
                "device-list", json.dumps(all_devices), room=self.ROOM_WEB
            )

        @sio.on("register")
        async def register(sid, data):
            # check and put all devices in one room
            if data["type"] == "player":
                new_device = {"sid": sid}
                new_device["uid"] = data["uid"]
                new_device["type"] = data["type"]
                self.database.add_or_update_device(new_device)
                self.connected_devices.append(new_device)
                await sio.enter_room(sid, self.ROOM_DEVICES)
                logging.info("device connected: " + sid)
            if data["type"] == "web":
                await sio.enter_room(sid, self.ROOM_WEB)
                logging.info("web ui connected: " + sid)
            
            all_devices = self.__merge_devices()
            await sio.emit(
                "device-list", json.dumps(all_devices), room=self.ROOM_WEB
            )
