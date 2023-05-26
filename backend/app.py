import socketio
from aiohttp import web
import json
import config
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

async def create_new_project(request):
    request_data = await request.json()
    try:
        new_project = database.create_new_project(request_data)
        return web.json_response(new_project)
    except DatabaseException as ex:
        return web.HTTPBadRequest(text=ex.to_json(), content_type="application/json")

async def debug_play(request):
    request_data = await request.json()
    eventName = request_data['eventName']
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
    web.post('/api/project', create_new_project),
    web.get('/api/device', get_all_devices),
    web.get('/', index_handler),
    web.post('/api/debug/play', debug_play),
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
        new_device['name'] = data['name']
        new_device['type'] = data['type']
        connected_devices.append(new_device)
        sio.enter_room(sid, ROOM_DEVICES)
        print('device connected: ', sid)
    if data['type'] == 'web':
        sio.enter_room(sid, ROOM_WEB)
        print('web ui connected: ', sid)


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
