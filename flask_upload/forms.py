from wtforms.fields import Field
from wtforms.widgets import Input, HTMLString, html_params

from flask_upload.models import UploadedFile

class FileInput(Input):
    input_type = 'file'

    def __init__(self, multiple=None, selectable_field=None):
        self.multiple = multiple
        self.selectable_field =selectable_field

    def __call__(self, field, **kwargs):
        
        if self.multiple:
            kwargs['multiple'] = ''
            if self.selectable_field:
                kwargs['data-selectable'] = self.selectable_field
        return HTMLString('<input %s>' % 
            html_params(name=field.name, type='file', **kwargs))


class FileField(Field):

    widget = FileInput()

    def __init__(self, fk_field=None, uploaded_file_model=UploadedFile, 
                 multiple=None, selectable_field=None, **kwargs):
        
        self.fk_field = fk_field
        self.uploaded_file_model = uploaded_file_model
        self.multiple = multiple
        super(FileField, self).__init__(**kwargs)

    def process(self, formdata, data=None):
        self.data = None
        if formdata:
            if not self.multiple and self.short_name in formdata:
                self.data = formdata[self.short_name]
            else:
                self.data = formdata.getlist(self.short_name + '[]')


    def process_formdata(self, valuelist):
        
        super(FileField, self).process_formdata(valuelist)

    def populate_obj(self, obj, name):
        data = None if not self.data else self.data
        if data:
            if self.multiple:
                setattr(obj, name, self.uploaded_file_model.gets(data))
            else:
                setattr(obj, name, self.uploaded_file_model.get(data))
            if self.fk_field:
                setattr(obj, self.fk_field, data) 

    def _value(self):
        return ''