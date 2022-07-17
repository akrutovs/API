from aiohttp_jinja2 import template



@template('upload.html')
async def index(request):
    return {}




