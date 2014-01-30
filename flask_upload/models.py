from flask import current_app as app
from flask_spirits.database import Model
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship, backref
from PIL import Image, ImageOps, ImageChops


class UploadedFile(Model):
    """
    An uploaded file with meme. Image data included if file is image.
    File may be in one folder.
    """
    
    __tablename__ = 'uploaded_file'
    id = Column(Integer, primary_key=True)
    path = Column(String(255))
    name = Column(String(255))
    mime = Column(String(100))
    height = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    folder_id = Column(ForeignKey('upload_folder.id'), unique=False, nullable=True)
    folder = relationship('UploadFolder', backref='files')

    def __init__(self, path, mime, name, height=None, width=None):
        self.path = path
        self.mime = mime
        self.name = name
        self.height = height
        self.width = width

    def __repr__(self):
        return "<File '%s' [%s] %s>" %  (self.name, self.mime, self.path)

    def __json__(self):
        file_data = {
            'id': self.id,
            'path': self.path,
            'name': self.name,
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

    def get_external_uri(self):
        return "%s%s%s" % (app.config['EXTERNAL_URI'],
            app.config['UPLOAD_WEB_PATH'], self.path)
    
    def get_absolute_path(self):
        return "%s%s" % (app.config['UPLOAD_PATH'], self.path)
    
    def get_web_path(self):
        return "%s%s" % (app.config['UPLOAD_WEB_PATH'], self.path)   

    def get_thumbnail(size):
        return "%s%s%s%s.jpg" % (app.config['EXTERNAL_URI'], 
            app.config['THUMBNAIL_WEB_PATH'], self.path, str(size))

    def get_graph_thumbnail(self):
        return "%s%s%s_graph.jpg" % (app.config['EXTERNAL_URI'], 
            app.config['THUMBNAIL_WEB_PATH'], self.path)

    def get_img_tag(self, thumbnail_size=None):
        params = (self.get_web_path(), self.id)
        if thumbnail_size:
            params += ('style="%s"' % self.thumbnail_css(int(thumbnail_size)),) 
        else:
            params += ('',)
        return '<img src="%s" data-id="%s" %s />' % params

    @classmethod
    def get_root_files(self):
        return self.query.filter(self.folder_id == None).all()
   
    def open(self):
        return open(self.get_absolute_path())

    def thumbnail_css(self, size=260):
        if self.width > self.height:
            print (size - ((size * self.height) / self.width) / 2)
            print (size - ((size * self.height) / self.width)) 
            offset = (size - ((size * self.height) / self.width) ) / 2
            css = 'width: 100%%; margin-top: %spx' % offset
        else:
            css = 'height: 100%'
        print size, type(size)
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

class UploadFolder(Model):
    __tablename__ = 'upload_folder'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    created = Column(DateTime)
    parent_id = Column(ForeignKey('upload_folder.id'), unique=False, nullable=True)
    children = relationship('UploadFolder', 
        backref=backref('parent', remote_side=[id]))

    @classmethod
    def get_root_folders(self):
        return self.query.filter(self.parent_id == None).all()


    def __json__(self):
        return dict(
            id=self.id,
            name=self.name,
            parent=self.parent
        )
    
    
