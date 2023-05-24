import socketio
from aiohttp import web
import json
import config
import os
from slugify import slugify
import random
import string

ROOM_DEVICES = 'room_devices'
ROOM_WEB = 'room_web_clients'

connected_devices = []
database = {
    'version': 1,
    'projects': []
}
current_project = []

async def handle_api(request):
    global connected_devices
    print('request: ', request)    
    data = json.dumps(connected_devices)
    return web.Response(text=data)

async def get_all_devices(request):
    global connected_devices
    data = json.dumps(connected_devices)
    return web.Response(text=data)

async def get_all_projects(request):
    global database
    data = []
    for project in database['projects']:
        data.append({
            'id': project['id'],
            'name': project['name'],
            'slug': project['slug'],
        })
    return web.json_response(data)

async def get_project(request):
    global database
    q = request.query
    project = None
    if 'id' in q:
        for item in database['projects']:
            if item['id'] == q['id']:
                project = item
    elif 'slug' in q:
        for item in database['projects']:
            if item['slug'] == q['slug']:
                project = item

    if project != None:
        file_name = project['file_name']
        with open(file_name, "r") as outfile:
            response_data = json.load(outfile)
            del response_data['file_name']
            return web.json_response(response_data)
    else:
        return web.HTTPNotFound()

async def create_new_project(request):
    global database

    request_data = await request.json()

    # check wether a project with the specified name already exists
    project_name_exists = False
    for project in database['projects']:
        if project['name'] == request_data['name']:
            project_name_exists = True

    if project_name_exists:
        error = {
            'code': 1,
            'message': 'project with given name already exists'
        }
        return web.HTTPBadRequest(text=json.dumps(error), content_type="application/json")
    else:
        slug = slugify(request_data['name'])
        id = 'project_' + ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        file_name = config.zp_projects_path + '/' + id + '.json'

        new_project = {
            'id': id,
            'name': request_data['name'],
            'slug': slug,
            'file_name': file_name,
        }

        out = json.dumps(new_project)

        with open(file_name, "w") as outfile:
            outfile.write(out)
        database['projects'].append(new_project)
        save_database()
        del new_project['file_name']
        return web.json_response(new_project)


app = web.Application()

sio = socketio.AsyncServer(cors_allowed_origin="*", async_mode='aiohttp')
sio.attach(app)


app.add_routes([
    web.get('/api', handle_api),
    web.get('/api/project/all', get_all_projects),
    web.get('/api/project', get_project),
    web.post('/api/project', create_new_project),
    web.get('/api/device', get_all_devices),
    web.static('/', 'web-client', show_index=True, follow_symlinks=True),
])


@sio.event
async def connect(sid, data):
    global connected_devices
    new_device = {
        'sid': sid
    }
    async def cb(data):
        # check and put all devices in one room
        if data['type'] == 'player':
            new_device['name'] = data['name']
            new_device['type'] = data['type']
            connected_devices.append(new_device)
            sio.enter_room(sid, ROOM_DEVICES)
            print('device connected: ', sid)
        if data['type'] == 'web':
            sio.enter_room(sid, ROOM_WEB)
            print('web ui connected: ', sid)
        await sio.emit('device-list', json.dumps(connected_devices), room=ROOM_WEB)
    await sio.emit('get_sys', {}, room=sid, callback=cb)

@sio.event
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


def init():
    global database
    print('Startup ZusammenPlayer Hub')

    # check if data path exists, otherwise create it
    if not os.path.exists(config.zp_data_path):
        os.mkdir(config.zp_data_path)
        print('created zp data directory')

    # check if projects directory exists otherwise create one
    if not os.path.exists(config.zp_projects_path):
        os.mkdir(config.zp_projects_path)
        print('created zp projects directory')
    
    # check if database file exists otherwise create one
    if not os.path.exists(config.zp_db_file_path):
        with open(config.zp_db_file_path, "w") as outfile:
            outfile.write(json.dumps(database))
            print('created zp database file')
    
    # check if data file is a file
    if not os.path.isfile(config.zp_db_file_path):
        print('error: database file is a directory')
        return False
    
    # check if project dir is a directory
    if not os.path.isdir(config.zp_projects_path):
        print('projects path is a file but should be a directory')
        return False
    
    # load projects
    with open(config.zp_db_file_path) as db:
        database = json.load(db)

    return True

def save_database():
    global database
    with open(config.zp_db_file_path, "w") as outfile:
        outfile.write(json.dumps(database))
        print('database saved')

init()

if __name__ == '__main__':
    web.run_app(app)
