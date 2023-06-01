import socketio
from aiohttp import web
import json
import config
import data_utils
from zp_database import ZP_Database as Database, DatabaseException

ROOM_DEVICES = 'room_devices'
ROOM_WEB = 'room_web_clients'

connected_devices = []
database = Database(config.zp_data_path)

async def index_handler(request):
    with open('web-client/index.html') as f:
        html = f.read()
        return web.Response(text=html, content_type='text/html')

# api endpoints

async def get_all_devices(_):
    global connected_devices
    return web.json_response(connected_devices)

async def get_all_projects(_):
    return web.json_response(database.get_projects())

async def get_project(request):
    q = request.query
    project = None
    if 'id' in q:
        project = database.get_project(q['id'])
    elif 'slug' in q:
        project = database.get_project_by_slug(q['slug'])

    if project != None:
        return web.json_response(project)
    else:
        return web.HTTPNotFound()

async def create_project(request):
    request_data = await request.json()
    try:
        new_project = database.create_new_project(request_data)
        return web.json_response(new_project)
    except DatabaseException as ex:
        return web.HTTPBadRequest(text=ex.to_json(), content_type="application/json")

async def update_project(request):
    id = request.match_info['project_id']
    request_data = await request.json()
    project = database.get_project(id)
    if project is None:
        return web.HTTPNotFound()
    else:
        if 'scenes' in request_data:
            project['scenes'] = request_data['scenes']
        if 'cuelists' in request_data:
            project['cuelists'] = request_data['cuelists']
        database.save_project(project)
        return web.json_response(project)

async def trigger_cue(request):
    global connected_devices

    request_data = await request.json()

    if 'projectId' not in request_data or 'cuelistId' not in request_data or 'cueId' not in request_data :
        error = {'code': 41, 'message': 'invalid request data'}
        return web.HTTPBadRequest(text=json.dumps(error))
    
    projectId = request_data['projectId']
    cuelistId = request_data['cuelistId']
    cueId = request_data['cueId']

    project = database.get_project(projectId)
    cuelist = None
    for list in project['cuelists']:
        if list['id'] == cuelistId:
            cuelist = list

    if cuelist is None:
        error = {'code': 43, 'message': 'unknown cuelistId'}
        return web.HTTPBadRequest(text=json.dumps(error))
    
    cue = None
    for c in cuelist['cues']:
        if c['id'] == cueId:
            cue = c
    
    if cue is None:
        error = {'code': 44, 'message': 'unknown cueId'}
        return web.HTTPBadRequest(text=json.dumps(error))

    print('trigger cue: ', cue['label'])

    # collect all trigger
    trigger = []
    for mapping in cue['mappings']:
        vdid = mapping['virtual_device_id']
        scene_id = mapping['scene_id']

        scene = data_utils.get_scene(project, scene_id)
        devices = data_utils.get_devices(connected_devices, project, vdid)

        for device in devices:
            t = {'instructions': scene['instructions'], 'uid': device['uid'], 'sid': device['sid']}
            trigger.append(t)

    for t in trigger:
        await sio.emit('trigger', t['instructions'], room=t['sid'])

    response_data = {}
    return web.json_response(response_data)

async def pause_all(request):
    global connected_devices

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
    await sio.emit('pause', 'pause')


async def debug_play(request):
    request_data = await request.json()
    payload = request_data['payload']
    try:
        payload = json.loads(payload)
    except:
        print("cannot parse json")
        pass
    await sio.emit(request_data['eventName'], payload, room=ROOM_DEVICES)
    return web.json_response({})


# create web application 
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

app.add_routes([
    web.get('/api/project/all', get_all_projects),
    web.get('/api/project', get_project),
    web.post('/api/project', create_project),
    web.put('/api/project/{project_id}', update_project),
    web.get('/api/device', get_all_devices),
    web.post('/api/project/trigger', trigger_cue),
    web.post('/api/project/pause', pause_all),
    web.post('/api/debug/play', debug_play),
    web.get('/', index_handler),
    web.static('/', 'web-client', show_index=True, follow_symlinks=True),
])

# socket io event handling

@sio.on('disconnect')
async def disconnect(sid):
    global connected_devices
    # remove device from connected devices
    index = -1
    for i, device in enumerate(connected_devices): 
        if device['sid'] == sid:
            index = i
    if index != -1:
        del connected_devices[index]
    print(sid, ' disconnected')
    await sio.emit('device-list', json.dumps(connected_devices), room=ROOM_WEB)

@sio.on('register')
async def register(sid, data):
    global connected_devices    
    # check and put all devices in one room
    if data['type'] == 'player':
        new_device = {
            'sid': sid
        }
        new_device['uid'] = data['uid']
        new_device['name'] = data['name']
        new_device['type'] = data['type']
        connected_devices.append(new_device)
        sio.enter_room(sid, ROOM_DEVICES)
        print('device connected: ', sid)
    if data['type'] == 'web':
        sio.enter_room(sid, ROOM_WEB)
        print('web ui connected: ', sid)
    await sio.emit('device-list', json.dumps(connected_devices), room=ROOM_WEB)


def init():
    print('Startup ZusammenPlayer Hub')
    try:
        database.init()
    except DatabaseException as ex:
        print("could not create database: ", ex.message)
        return False
    return True

init()

if __name__ == '__main__':
    web.run_app(app)
