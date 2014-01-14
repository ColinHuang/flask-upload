from flask import current_app as app
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
            file_data.update(
                image=True,
                height=self.height,
                width=self.width
            )
        return file_data

    def get_path(self):
        return "%s%s" % (self.path, self.name)

    def get_external_uri(self):
        return "%s%s%s" % (app.config['EXTERNAL_URI'],
            app.config['UPLOAD_WEB_PATH'], self.get_path())
    
    def get_absolute_path(self):
        return "%s%s" % (app.config['UPLOAD_PATH'], self.get_path())
    
    def get_web_path(self):
        return "%s%s" % (app.config['UPLOAD_WEB_PATH'], self.get_path())   

    def get_thumbnail(size):
        return "%s%s%s%s.jpg" % (app.config['EXTERNAL_URI'], 
            app.config['THUMBNAIL_WEB_PATH'], self.get_path(), str(size))

    def get_graph_thumbnail(self):
        return "%s%s%s_graph.jpg" % (app.config['EXTERNAL_URI'], 
            app.config['THUMBNAIL_WEB_PATH'], self.get_path())


    @classmethod
    def get_by_directory(self, path='/'):
        return self.query.filter(self.path == path).all()
   
    def open(self):
        return open(self.get_absolute_path())

    def thumbnail_css(self, size=260):
        if self.width > self.height:
            css = 'width: 100%; margin-top: %spx' % \
                (size - ((size * self.height) / self.width) / 2) 
        else:
            css = 'height: 100%'
        return css

    def thumbnail(self, size=(250,250), pad=False):
        image = Image.open(self.get_absolute_path())

        if pad:
            thumb = image.crop((0, 0, size[0], size[1]))

            offset_x = max((size[0] - self.width) / 2, 0)
            offset_y = max((size[1] - self.height) / 2, 0)

            thumb = ImageChops.offset(thumb, offset_x, offset_y)

        else:
            thumb = ImageOps.fit(image, size, Image.ANTIALIAS, (0.5, 0.5))
        path = (app.config['THUMBNAIL_PATH'], self.get_path(), size[0])
        thumb.convert('RGB').save('%s%s%s.jpg' % path)

    def graph_thumbnail(self):
        """ Generates a thumbnail as close as possible to 1.91:1 ratio""" 
        image = Image.open(self.get_absolute_path())
        if self.width >= 1200:
            size = (1200, 630)
        elif self.width >= 600:
            size = (600, 315)
        else:
            aspect = self.width / float(self.height)
            ideal_aspect = 600 / float(315)
            if aspect > ideal_aspect:
                # Then crop the left and right edges:
                new_width = int(ideal_aspect * height)
                offset = (width - new_width) / 2
                resize = (offset, 0, width - offset, height)
            else:
                # ... crop the top and bottom:
                new_height = int(width / ideal_aspect)
                offset = (height - new_height) / 2
                resize = (0, offset, width, height - offset)
            thumb = image.crop(resize).resize((600, 315), Image.ANTIALIAS)

        if self.width >= 600:
            thumb = ImageOps.fit(image, size, Image.ANTIALIAS, (0.5, 0.5))
        path = (app.config['THUMBNAIL_PATH'], self.get_path())
        thumb.convert('RGB').save("%s%s_graph.jpg" % path)
