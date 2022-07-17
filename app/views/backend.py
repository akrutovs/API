from aiohttp import web
import os
import asyncpg
import uuid
from PIL import Image
from datetime import datetime

db_name = 'postgres'
db_user = 'postgres'
db_pass = 'postgres'
db_host = 'localhost'
db_port = '5433'
db_string = 'postgresql://{}:{}@{}:{}/{}'.format(db_user, db_pass, db_host, db_port, db_name)


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
