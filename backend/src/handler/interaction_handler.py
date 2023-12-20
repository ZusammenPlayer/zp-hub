from aiohttp import web
import json
import logging
from socketio_manager import SocketIOManager
from database import Database
import data_utils


def setup(app: web.Application):
    app.router.add_post("/api/project/trigger", trigger_cue)
    app.router.add_post("/api/project/pause", pause_all)


async def trigger_cue(request):
    sio_mngr: SocketIOManager = request["sio_mngr"]
    database: Database = request["db"]

    request_data = await request.json()

    if (
        "projectId" not in request_data
        or "cuelistId" not in request_data
        or "cueId" not in request_data
    ):
        error = {"code": 41, "message": "invalid request data"}
        return web.HTTPBadRequest(text=json.dumps(error))

    projectId = request_data["projectId"]
    cuelistId = request_data["cuelistId"]
    cueId = request_data["cueId"]

    project = database.get_project(projectId)
    cuelist = None
    for list in project["cuelists"]:
        if list["id"] == cuelistId:
            cuelist = list

    if cuelist is None:
        error = {"code": 43, "message": "unknown cuelistId"}
        return web.HTTPBadRequest(text=json.dumps(error))

    cue = None
    for c in cuelist["cues"]:
        if c["id"] == cueId:
            cue = c

    if cue is None:
        error = {"code": 44, "message": "unknown cueId"}
        return web.HTTPBadRequest(text=json.dumps(error))

    logging.info("trigger cue: " + cue["label"])

    # collect all trigger
    trigger = []
    for mapping in cue["mappings"]:
        vdid = mapping["virtual_device_id"]
        scene_id = mapping["scene_id"]

        scene = data_utils.get_scene(project, scene_id)
        devices = data_utils.get_devices(sio_mngr.connected_devices, project, vdid)

        for device in devices:
            t = {
                "instructions": scene["instructions"],
                "uid": device["uid"],
                "sid": device["sid"],
            }
            trigger.append(t)

    for t in trigger:
        await sio_mngr.sio.emit("trigger", t["instructions"], room=t["sid"])

    response_data = {}
    return web.json_response(response_data)


async def pause_all(request):
    sio_mngr: SocketIOManager = request["sio_mngr"]
    database: Database = request["db"]

    logging.info('pause all devices')

    # for now just send pause event to all connected devices
    # later we will change it so that only devices that are used
    # within a project are paused

    # request_data = await request.json()

    # if 'projectId' not in request_data:
    #     error = {'code': 41, 'message': 'invalid request data'}
    #     return web.HTTPBadRequest(text=json.dumps(error))

    # projectId = request_data['projectId']
    # project = database.get_project(projectId)

    # if project is None:
    #     error = {'code': 40, 'message': 'project not found'}
    #     return web.HTTPBadRequest(text=json.dumps(error))

    # response_data = []
    # return web.json_response(response_data)
    await sio_mngr.sio.emit("pause", "pause")
