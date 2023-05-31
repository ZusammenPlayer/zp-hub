import asyncio
import random
import socketio
import sys

sio = socketio.AsyncClient()

_uid = 'player_id_' + str(random.randint(10000, 99999))

if len(sys.argv) > 1:
    _uid = str(sys.argv[1])

config = {
    'name': 'Wohnzimmer',
    'type': 'player',
    'uid': _uid
}

@sio.event
async def connect():
    global config
    print('connection established')
    await sio.emit('register', config)

@sio.event
async def my_message(data):
    print('message received with ', data)
    await sio.emit('my response', {'response': 'my response'})

@sio.event
async def disconnect():
    print('disconnected from server')

@sio.event
async def s(data):
    print('play command received from server')

@sio.event
async def set_sys(data):
    global config
    if data['name']:
        config.name = data['name']

@sio.event
async def trigger(data):
    print('trigger: ', data)

async def main():
    await sio.connect('http://127.0.0.1:8080')
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(main())
