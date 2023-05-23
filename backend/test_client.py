import asyncio
import socketio

sio = socketio.AsyncClient()

config = {
    'name': 'Wohnzimmer',
    'type': 'player',
    'uid': "lksdjfslkdfjslk"
}

@sio.event
async def connect():
    print('connection established')

@sio.event
async def my_message(data):
    print('message received with ', data)
    await sio.emit('my response', {'response': 'my response'})

@sio.event
async def disconnect():
    print('disconnected from server')

@sio.event
async def get_sys(data):
    global config
    return config

@sio.event
async def set_sys(data):
    global config
    if data['name']:
        config.name = data['name']

async def main():
    await sio.connect('http://127.0.0.1:8050')
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(main())
