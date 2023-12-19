from aiohttp import web
import os
import magic
import hashlib
import json
import config
from database import DatabaseException
from socketio_manager import SocketIOManager
from database import Database
import data_utils


def setup(app: web.Application):
    app.router.add_get("/api/project/all", get_all_projects)
    app.router.add_get("/api/project", get_project)
    app.router.add_post("/api/project", create_project)
    app.router.add_post("/api/project/file", upload_project_file)
    app.router.add_put("/api/project/{project_id}", update_project)
    app.router.add_get("/api/project/{project_id}/{filename}", get_project_file)


async def trigger_file_sync(project, sio_mngr: SocketIOManager):
    device_ids = data_utils.devices_for_project(project)
    for device_id in device_ids:
        device = next(
            (d for d in sio_mngr.connected_devices if d["uid"] == device_id), None
        )
        if device is not None:
            files = data_utils.files_for_device(project, device_id)
            data = {"project_id": project["id"], "device_id": device_id, "media": files}
            await sio_mngr.sio.emit(event="file_sync", data=data, to=device["sid"])


async def get_all_projects(request):
    database = request["db"]
    return web.json_response(database.get_projects())


async def get_project(request):
    database: Database = request["db"]
    q = request.query
    project = None
    if "id" in q:
        project = database.get_project(q["id"])
    elif "slug" in q:
        project = database.get_project_by_slug(q["slug"])

    if project != None:
        return web.json_response(project)
    else:
        return web.HTTPNotFound()


async def create_project(request):
    database = request["db"]
    request_data = await request.json()
    try:
        new_project = database.create_new_project(request_data)
        return web.json_response(new_project)
    except DatabaseException as ex:
        return web.HTTPBadRequest(text=ex.to_json(), content_type="application/json")


async def update_project(request):
    sio_mngr: SocketIOManager = request["sio_mngr"]
    database = request["db"]
    id = request.match_info["project_id"]
    request_data = await request.json()
    project = database.get_project(id)
    if project is None:
        return web.HTTPNotFound()
    else:
        if "scenes" in request_data:
            project["scenes"] = request_data["scenes"]
        if "cuelists" in request_data:
            project["cuelists"] = request_data["cuelists"]
        database.save_project(project)
        await trigger_file_sync(project, sio_mngr)
        return web.json_response(project)


async def upload_project_file(request):
    database = request["db"]
    project_id = None
    file_data = None

    # read request data
    reader = await request.multipart()
    while True:
        field = await reader.next()
        if field is None:
            break

        if field.name == "projectId":
            project_id = await field.read(decode=True)
            project_id = project_id.decode("utf-8")

        if field.name == "file":
            filename = field.filename
            file_data = await field.read(decode=False)

    # validate request data
    if project_id is None:
        error = {"code": 41, "message": "invalid request data - project_id missing"}
        return web.HTTPBadRequest(text=json.dumps(error))

    project = database.get_project(project_id)
    if project is None:
        error = {"code": 41, "message": "invalid request data - project not found"}
        return web.HTTPBadRequest(text=json.dumps(error))

    if file_data is None:
        error = {"code": 41, "message": "invalid request data - file is missing"}
        return web.HTTPBadRequest(text=json.dumps(error))

    md5 = hashlib.md5(file_data).hexdigest()

    project_files = []
    if "media" in project:
        project_files = project["media"]

        # check if file already exists
        for file in project_files:
            if file["md5"] == md5:
                error = {"code": 42, "message": "file already exists"}
                return web.HTTPBadRequest(text=json.dumps(error))

    # check if project data directory exists
    project_data_dir = config.zp_data_path + "/projects/" + project_id
    if not os.path.exists(project_data_dir):
        os.mkdir(project_data_dir)

    file_path = project_data_dir + "/" + filename
    with open(file_path, "wb") as f:
        f.write(file_data)

    mime_type = magic.from_file(file_path, mime=True)

    # add file to project file
    project_file = {
        "filename": filename,
        "file_path": file_path,
        "mime_type": mime_type,
        "md5": md5,
    }

    project_files.append(project_file)

    project["media"] = project_files
    database.save_project(project)

    return web.json_response(project_file)


async def get_project_file(request):
    database: Database = request["db"]
    project_id = request.match_info["project_id"]
    filename = request.match_info["filename"]

    project = database.get_project(project_id)
    if project is None:
        error = {"code": 44, "message": "project not found"}
        return web.HTTPBadRequest(text=json.dumps(error))
    
    for file in project["media"]:
        if file["filename"] == filename:
            with open(file["file_path"], mode="rb") as f:
                data = f.read()
                return web.Response(body=data, content_type=file["mime_type"])
    
    return web.HTTPNotFound()
