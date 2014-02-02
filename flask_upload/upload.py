import os
import magic
import random
from flask import Blueprint, render_template, abort, session, redirect, \
    request, current_app as app
from flask.ext.assets import Bundle
from flask_spirits.spirits import jsonify
from flask_upload.models import UploadedFile, UploadFolder
from PIL import Image
from werkzeug import secure_filename

bp = Blueprint('upload', __name__, template_folder='jinja', 
    static_folder='static')

@bp.app_template_global()
def get_upload_web_path():
    return app.config['UPLOAD_WEB_PATH']

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


def generate_filename(length=16):
    'Generates a unique file name containing a-z A-Z 0-9'
    pool = range(48, 57) + range(65, 90) + range(97, 122)
    return ''.join(chr(random.choice(pool)) for _ in range(length))


def _handle_upload(files):
    'Handles uploaded files'
    if not files:
        return []

    json = []
    folder =  _get_request_folder()
    upload_path = app.config['UPLOAD_PATH']
    web_path = app.config['UPLOAD_WEB_PATH']
    magic_mime = magic.Magic(mime=True)

    accept_only = None
    if 'UPLOAD_ACCEPT_ONLY' in app.config:
        accept_only = app.config['UPLOAD_ACCEPT_ONLY']

    for key, upload in files.iteritems():
        if '.' not in upload.filename:
            upload.rawname = upload.filename
            upload.ext = ''
        else:
            upload.rawname, upload.ext = upload.filename.rsplit('.', 1)
            upload.ext = '.' + upload.ext
           
        exists = True
        while exists:
            path = secure_filename(generate_filename() + upload.ext)
            file_path = upload_path + path
            exists = os.path.exists(file_path)

        upload.save(file_path)

        mime = magic_mime.from_file(file_path)
        if accept_only and mime not in accept_only:
            os.remove(file_path)
            continue

        file_data = dict(path=path, name=upload.rawname, mime=mime)
        
        if file_data['mime'] in _image_mimes:
            im = Image.open(file_path)
            file_data['width'] = im.size[0]
            file_data['height'] = im.size[1]

        uploaded_file = UploadedFile(**file_data)
        uploaded_file.folder_id = folder.id
        uploaded_file.save()

        json.append(uploaded_file)

    return json

def _get_root_folder():
    folder = UploadFolder.query.filter(UploadFolder.parent_id == None).first()
    if not folder:
        folder = UploadFolder()
        folder.save()
    return folder

def _get_request_folder(name='folder'):
    if name in request.form:
        folder = UploadFolder.get(request.form[name])
    else:
        folder = _get_root_folder()
    return folder

@bp.route('/', methods=['POST'])
def submit_view():
    print request.form
    try:
        return jsonify(success=True, files=_handle_upload(request.files))
    except:
        return jsonify(success=False)

@bp.route('/load', methods=['POST'])
def load_view():
    return jsonify(UploadedFile.gets(request.form.getlist('ids[]')))

@bp.route('/list', methods=['POST'])
def files_view():
    folder = _get_request_folder()
    files = folder.files
    folders = folder.children
    if folder.parent:
        folders = [dict(name='..', id=folder.parent.id)] + folders

    return jsonify(files=files, folders=folders)

@bp.route('/mv', methods=['POST'])
def mv_view():
    folder = _get_request_folder('dest')
    if 'folder' in request.form:
        move = UploadFolder.get(request.form['folder'])
        move.parent = folder
        move.save()
    else:
        files = UploadedFile.gets(request.form.getlist('files[]'))
        folder.files += files
        folder.save()
    return jsonify(success=True)

@bp.route('/folder', methods=['POST'])
def folder_view():
    folder = UploadFolder()
    if 'id' in request.form:
        folder = UploadFolder.get(request.form['id'])
        folder.created = datetime.today()
    folder.name = request.form['name']
    if 'parent' in request.form:
        folder.parent_id = request.form['parent']  
    else:
        folder.parent_id = _get_root_folder().id
    folder.save()
    return jsonify(success=True)

@bp.route('/rm', methods=['POST'])
def delete_file_view():
    upload_path = app.config['UPLOAD_PATH']
    upload_file = UploadedFile.get(request.form['id'])
    try:
        os.remove(upload_path + upload_file.path)
        upload_file.delete()
    except:
        return jsonify(success=False)

    return jsonify(success=True)  

@bp.route('/delete/folder', methods=['POST'])
def delete_folder_view():
    pass