from flask import current_app
from sqlalchemy import Column, DateTime, Integer, String, Text
from PIL import Image, ImageOps, ImageChops

class UploadedFileBase(object):
    """ An Uploaded File"""
    __tablename__ = 'uploaded_file'
    id = Column(Integer, primary_key=True)
    path = Column(String(255))
    name = Column(String(255))
    title = Column(String(255))
    mime = Column(String(100))
    height = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    def __init__(self, path, name, mime, title, height=None, width=None):
        self.path = path
        self.name = name
        self.mime = mime
        self.title = title
        self.height = height
        self.width = width
    def __repr__(self):
        return "<File '%s' [%s] %s%s>" % \
            (self.title, self.mime, self.path, self.name)
    def __json__(self):
        file_data = {
            'id': self.id,
            'path': self.path,
            'name': self.name,
            'title': self.title,
            'mime': self.mime,
            'web_path': self.get_web_path()
        }
        if self.height != None:
            file_data['image'] = True
            file_data['width'] = self.width
            file_data['height'] = self.height
        return file_data

    def get_external_uri(self):
        return str(current_app.config['EXTERNAL_URI'] + 
            current_app.config['UPLOAD_WEB_PATH'] + self.path + self.name)
    
    def get_absolute_path(self):
        return str(current_app.config['UPLOAD_PATH'] + 
            self.path + self.name)
    
    def get_web_path(self):
        return str(current_app.config['UPLOAD_WEB_PATH'] + 
            self.path + self.name)   
         
    @classmethod
    def get_by_directory(self, path='/'):
        return self.query.filter(self.path == path).all()
    @classmethod
    def get_file(self, path='/', name='/'):
        return self.query.filter()

    def thumbnail_css(self, size=260):
        if self.width > self.height:
            css = 'width: 100%; margin-top: ' + \
                str((size - ((size * self.height) / self.width)) / 2) + 'px;'
        else:
            css = 'height: 100%'
        return css

    def thumbnail(self, size=(250,250), pad=False):
        image = Image.open(self.get_absolute_path())
        image_size = image.size

        if pad:
            
            thumb = image.crop( (0, 0, size[0], size[1]) )

            offset_x = max( (size[0] - image_size[0]) / 2, 0 )
            offset_y = max( (size[1] - image_size[1]) / 2, 0 )

            thumb = ImageChops.offset(thumb, offset_x, offset_y)

        else:
            thumb = ImageOps.fit(image, size, Image.ANTIALIAS, (0.5, 0.5))

        thumb.convert('RGB').save(current_app.config['THUMBNAIL_PATH'] + 
            self.path + self.name + str(size[0]) + '.jpg')