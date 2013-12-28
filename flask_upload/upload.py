import os
import magic

from random import randint

from PIL import Image
from flask import Blueprint, render_template, abort, session, redirect, \
    request, current_app
from flask.ext.assets import Bundle
from werkzeug import secure_filename
from flask_spirits.spirits import jsonify
from flask_upload.models import UploadedFileBase

bp = Blueprint('upload', __name__, template_folder='../jinja', 
    static_folder='../static')

# Overwite this in app!
bp.UploadedFile = UploadedFileBase

@bp.app_template_global()
def get_upload_web_path():
    return current_app.config['UPLOAD_WEB_PATH']

js_blueimp = Bundle(
    'upload/lib/jquery.iframe-transport.js', 
    'upload/lib/jquery.fileupload.js'
)
js_file = Bundle(
    'upload/script/file-widget.js',
    'upload/script/file-browser.js',
    'upload/script/file-field.js',
)
js_all = Bundle(js_blueimp, js_file)

css_blueimp = Bundle('upload/lib/jquery.fileupload.css')
css_file = Bundle('upload/style/file-widget.css')
css_filebrowser = Bundle('upload/style/file-browser.css',)
css_filefield = Bundle('upload/style/file-field.css')
css_all = Bundle(css_blueimp, css_file, css_filebrowser, css_filefield)

_image_mimes = ['image/jpeg', 'image/png', 'image/gif', 'image/x-ms-bmp']


def generate_filename():
    return ''.join(chr(randint(97, 122)) for _ in range(16))


def _handle_upload(files, upload_dir='/'):
    if not files:
        return None
    json = []
    upload_path = current_app.config['UPLOAD_PATH']
    web_path = current_app.config['UPLOAD_WEB_PATH']
    accept_only = None
    if 'UPLOAD_ACCEPT_ONLY' in current_app.config:
        accept_only = current_app.config['UPLOAD_ACCEPT_ONLY']
    mime = magic.Magic(mime=True)
    for key, upload in files.iteritems():
        if '.' not in upload.filename:
            upload.rawname = upload.filename
            upload.ext = ''
        else:
            upload.rawname, upload.ext = upload.filename.rsplit('.', 1)
           
        exists = True
        while exists:
            file_name = secure_filename(generate_filename() + upload.ext)
            file_path = upload_path + upload_dir + file_name
            exists = os.path.exists(file_path)

        upload.save(file_path)
        file_data = {
            'path': upload_dir,
            'name': file_name,
            'title': upload.rawname,
            'mime': mime.from_file(file_path)
        }
        if file_data['mime'] in _image_mimes:
            im = Image.open(file_path)
            file_data['width'] = im.size[0]
            file_data['height'] = im.size[1]
        uploaded_file = bp.UploadedFile(**file_data)
        uploaded_file.persist()
        json.append(uploaded_file)
    return json


@bp.route('/submit', methods=['POST'])
def submit():
    try:
        files = request.files
        uploaded_files = _handle_upload(files)
        return jsonify({'files': uploaded_files})
    except:
        raise
        return jsonify({'statis': 'error'})

@bp.route('/load', methods=['POST'])
def load():
    return jsonify(bp.UploadedFile.gets(request.form.getlist('ids[]')))

@bp.route('/list')
def files():
    upload_dir = request.form['dir'] if 'dir' in request.form else '/'
    path = current_app.config['UPLOAD_PATH'] + upload_dir
    dirs = []
    for folder in [x[1] for x in os.walk(path)][0]:
        dirs.append({'title': folder})
    return jsonify(dict(
        files=bp.UploadedFile.get_by_directory(upload_dir), 
        dirs=dirs
    ))

@bp.route('/delete', methods=['POST'])
def delete_file():
    upload_path = current_app.config['UPLOAD_PATH']
    upload_file = bp.UploadedFile.get(int(request.form['id']))
    try:
        os.remove(upload_path + upload_file.path + upload_file.name)
        upload_file.delete()
    except:
        return jsonify({'success': False})
    return jsonify({'success': True})  