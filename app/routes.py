from .views import frontend, backend
from aiohttp import web
def set_routes(app):
    app.add_routes([web.get('/',frontend.index),
                    web.post('/upload', backend.upload)])
