from flask import Flask
from flask_socketio import SocketIO, send
import eventlet
eventlet.monkey_patch(socket=True)
from flask import request
import config
import os
from slugify import slugify
import json
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

app = Flask(__name__, static_folder='web-client', static_url_path="/")
sio = SocketIO(app, cors_allowed_origin="*", async_mode='eventlet')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return app.send_static_file("index.html")

@app.get('/api/project')
def get_all_projects():
    global database
    return database['projects']

@app.post('/api/project')
def create_new_project():
    print('create new project')
    global database
    data = json.loads(request.data.decode('utf-8'))
    print('data: ', data)
    print('type: ', type(data))

    slug = slugify(data['name'])
    id = 'project_' + ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    file_name = config.zp_projects_path + '/' + id + '.json'

    new_project = {
        'id': id,
        'name': data['name'],
        'slug': slug,
        'file_name': file_name,
    }

    out = json.dumps(new_project)

    with open(file_name, "w") as outfile:
        outfile.write(out)
    database['projects'].append(new_project)
    save_database()
    return (out, 200)
    
@app.get('/api/device')
def get_all_devices():
    global connected_devices
    return connected_devices

@sio.event
def connect():
    global connected_devices
    new_device = {
        'sid': request.sid
    }
    def cb(data):
        new_device['name'] = data['name']
        new_device['type'] = data['type']
        connected_devices.append(new_device)
        # check and put all devices in one room
        # if new_device['type'] == 'player':
            # sio.enter_room(request.sid, ROOM_DEVICES)
        print('connected: ', request.sid)
    sio.emit('get_sys', {}, room=request.sid, callback=cb)

@sio.event
def disconnect():
    global connected_devices
    # remove device from connected devices
    index = -1
    for i, device in enumerate(connected_devices): 
        if device['sid'] == request.sid:
            index = i
    if index != -1:
        del connected_devices[index]
    print(request.sid, ' disconnected')


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

if __name__ == "__main__":
    app.run(port=8050, debug=True)
