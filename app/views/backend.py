from aiohttp import web
import os
import asyncpg
import uuid
from PIL import Image
from datetime import datetime
import logging

db_name = 'postgres'
db_user = 'postgres'
db_pass = 'postgres'
db_host = 'db'
db_port = '5432'
db_string = 'postgresql://{}:{}@{}:{}/{}'.format(db_user, db_pass, db_host, db_port, db_name)

def init_logger(name):
    logging.basicConfig(level='DEBUG')
    logger = logging.getLogger(name)
    FORMAT = '%(asctime)s:'
    logger.setLevel("DEBUG")
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(FORMAT))
    sh.setLevel('DEBUG')
    logger.addHandler(sh)
    logger.debug('logger was create')
    return logger

logger = init_logger('app')
logger.debug('ok')

async def add_image_to_db(filename, path, date):

    conn = await asyncpg.connect(db_string)
    # Execute a statement to create a new table.
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS images(
            id serial PRIMARY KEY,
            filename text,
            path text,
            upload_date date )
        ''')
    await conn.execute('''
            INSERT INTO images(filename, path,upload_date) VALUES($1, $2, $3)
        ''', filename,path,date)
    # Close the connection.
    await conn.close()


async def get_image_from_database(id):
    conn = await asyncpg.connect(db_string)
    row = await conn.fetchrow(
        'SELECT * FROM images WHERE id = $1', int(id))
    await conn.close()
    return row

async def convert_to_jpg(path, image_name):
    im = Image.open(path)
    rgb_im = im.convert('RGB')
    path = os.getcwd() + '/app/views/media/' + image_name + '.jpg'
    rgb_im.save(path)
    return path


async def upload(request):
    # save file
    reader = await request.multipart()
    field = await reader.next()
    assert field.name == 'image'

    filename = field.filename
    file_extension = os.path.splitext(filename)[1]
    unique_filename = str(uuid.uuid4())
    size = 0
    path = os.getcwd() + '/app/views/media/' + unique_filename + file_extension

    if not os.path.exists(path):
        open(path, 'w+').close()
    with open(path, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)
    # check extension and convert
    if file_extension.lower() != '.jpg' or file_extension.lower() != '.jpeg':
        new_path = await convert_to_jpg(path, unique_filename)
        if os.path.isfile(path):
            os.remove(path)
            print("File has been deleted")
    await add_image_to_db(filename=filename, path=new_path, date=datetime.utcnow())

    return web.Response(text='{} sized of {} successfully stored'
                             ''.format(filename, size))

async def get_image(request):
    id = request.match_info['id']
    row = await get_image_from_database(id)
    print(row)
    if row!=None:
        return web.Response(
            text="Hello, {}".format(row))
    else:
        return web.Response(
            text="Hello, {}".format("no data"))