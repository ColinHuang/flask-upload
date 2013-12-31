from wtforms.fields import Field
from wtforms.widgets import Input, HTMLString, html_params

from flask_upload.upload import bp

class FileInput(Input):
    input_type = 'file'

    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        if self.multiple:
            kwargs['multiple'] = ''
        return HTMLString('<input %s>' % 
            html_params(name=field.name, type='file', **kwargs))


class FileField(Field):
    widget = FileInput()
    def __init__(self, prop=None, uploaded_file_model=None, **kwargs):
        if prop is None and '_id' in kwargs['_name']:
            prop = kwargs['_name'].replace('_id','')
        self.prop = prop
        if uploaded_file_model is None:
            uploaded_file_model = bp.UploadedFile
        self.uploaded_file_model = uploaded_file_model
        super(FileField, self).__init__(**kwargs)

    def process(self, formdata, data=None):
        
        if formdata and self.name in formdata:
            self.data = formdata[self.name]
        else:
            self.data = None
        #super(FileField, self).process(formdata, data)

    def process_formdata(self, valuelist):
        
        super(FileField, self).process_formdata(valuelist)

    def populate_obj(self, obj, name):
        data = None if not self.data else self.data
        setattr(obj, name, data)
        if data and self.prop:
            setattr(obj, self.prop, self.uploaded_file_model.get(self.data))
