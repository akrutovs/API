import jinja2
from aiohttp import web
import aiohttp_jinja2
from .routes import set_routes


async def create_app():
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader("app", "templates"))
    set_routes(app)
    return app
