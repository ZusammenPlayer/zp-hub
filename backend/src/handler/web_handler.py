from aiohttp import web
import config
import json

def setup(app: web.Application):
    app.router.add_post('/api/debug/play', debug_play)
    app.router.add_get('/', index_handler)
    app.router.add_static('/', config.zp_web_client_path, show_index=True, follow_symlinks=True)

async def index_handler(_):
    with open(config.zp_web_client_path + '/index.html') as f:
        html = f.read()
        return web.Response(text=html, content_type='text/html')

async def debug_play(request):
    request_data = await request.json()
    payload = request_data['payload']
    try:
        payload = json.loads(payload)
    except:
        print("cannot parse json")
        pass
    return web.json_response({})
