import socketio
from aiohttp import web
import json

connected_devices = []
installations = []

zp_state = {
    'current_project': None
}

zp_data_dir = './projects'

async def handle_api(request):
    global connected_devices
    print('request: ', request)    
    data = json.dumps(connected_devices)
    return web.Response(text=data)

async def handle_get_installation(request):
    global installations
    data = json.dumps(installations)
    return web.Response(text=data)

async def handle_add_installation(request):
    global installations
    data = await request.post()
    print("data: ", data)
    return web.Response(text='done')

app = web.Application()

sio = socketio.AsyncServer(async_mode='aiohttp')
sio.attach(app)

app.add_routes([
    web.get('/api', handle_api),
    web.get('/api/installation', handle_get_installation),
    web.post('/api/installation', handle_add_installation),
    web.static('/', 'web-client', show_index=True, follow_symlinks=True),
])

@sio.event
async def connect(sid, data):
    global connected_devices
    print(sid, ' connected')
    new_device = {
        'sid': sid
    }
    connected_devices.append(new_device)

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


if __name__ == '__main__':
    web.run_app(app)
