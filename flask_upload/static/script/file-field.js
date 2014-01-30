;(function($) {
    function FileField(element, options) {
        var self = this;
        this.files = [];
        this.multiple = typeof element.attr('multiple') !== 'undefined';
        this.selectable = !!element.data('selectable'); // If a picture can be selected
        this.selectable_field = $(element.data('selectable'));
        this.selected = false; 
        this.field = element.wrap('<div class="file-field">').parent()
            .addClass(this.multiple ? 'multiple' : '');       
        
        this.controls = $('<div class="controls">').appendTo(this.field);
        this.button = $(['<div class="btn btn-success fileinput-button">',
            '<i class="glyphicon glyphicon-plus"/>',
            '<span>Upload File' + (this.multiple ? 's' : '') + '</span>',
        '</div>'].join('')).append(element).appendTo(this.controls);

        if (window.FileBrowser) {
            this.controls.append([
            ' <div class="btn btn-primary" data-toggle="modal" data-target="#file_browser_modal">',
                '<i class="glyphicon glyphicon-plus"/>',
                '<span>Select from files</span>',
            '</div>'
            ].join(''));
        }

        this.filewidget = $('<div/>').prependTo(this.field).filewidget({ size: 2});

        this.filewidget.on('makefile', function(e, file) {
            if (self.multiple && self.selectable)
                Array.prototype.splice.apply(file, [5, 0,
                    '<div class="item-select-wrapper">',
                        '<div class="item-select trans-super"><i class="glyphicon glyphicon-ok" /></div>',
                        '<div class="trans-bkgd" />',
                    '</div>'
                ]);
        }).on('delete-item', function(e, file) {
            for (var x = 0; x < self.files.length; x++) {
                if (self.files[x].id == file.data('info').id) {
                    file = self.files.splice(x, 1)[0];
                    break;
                }
            }
            if (file.id == self.selected)  {
                if (self.files[0]) {
                    self.selected = self.files[0].id;
                    self.get_item(self.files[0].id).addClass('selected');
                } else {
                    self.selected = false;
                }
            }
            self.get_item(file.id).fadeOut();
            self.element.trigger('filefield.change');
        }).on('click', '.item-select-wrapper', function() {
            var item = $(this).parent();
            self._set_selected(item);
            item.siblings().removeClass('selected');
            self.element.trigger('filefield.change');
        });

        this.element = element.fileupload({
            url: '/upload/submit',
            dataType: 'json',
            done: function(e, data) {
                self.val(data.result.files)
            }
        }).on('submit-files', function(e, files) {
            self.filewidget.val(files);
        });
    }
    FileField.prototype = {
        disable: function() {
            this.element.attr('disabled','disabled');
            this.controls.find('.btn').addClass('disabled');
        },
        enable: function() {
            this.element.removeAttr('disabled');
            this.controls.find('.btn').removeClass('disabled');
        },
        load: function(ids) {
            var self = this;
            $.post('/upload/load',{ids: ids}, function(files) {
                self.val(files);
            },'json');
            return this;
        },
        load_dom: function(ids, selected) {
            var self = this;
            $.post('/upload/load',{ids: ids}, function(files) {
                self.val(files);
                if (self.selectable)
                    self._set_selected(self.get_item(self.selectable_field.val()));
            },'json');
        },
        val: function(files) {    
            if (files) {
                if (!_.isArray(files)) 
                    files = [files];
                this.filewidget.find('.files').html('');   
                if (!this.multiple)
                    this.files = [];
                this.files = _.uniq(_.union(this.files, files), 'id');
                this.filewidget.filewidget('loadfiles', this.files);
                if (this.multiple && this.selectable) {
                    if (!this.selected) {
                        var selected = _.filter(this.files, 'selected');
                        if (selected.length > 0) {
                            this.selected = selected[0].id;
                            selected[0].selected = false
                        } else if (files.length > 0)
                            this.selected = files[0].id;
                    }
                    if (this.selected)
                        this._set_selected(this.get_item(this.selected))
                }
                this.element.trigger('filefield.change');
            } else {
                if (this.files.length == 0) 
                    return undefined;
                if(this.multiple) { 
                    files = _.clone(this.files);
                    if (this.selectable)
                        _.filter(files,{ id: this.selected })[0].selected = true;
                    //return files;
                    return _.map(this.files, 'id');
                }
                else 
                    return this.files[0].id;
            }
            return undefined;
        }, 
        get_item: function(id) {
            return this.filewidget.find('[data-id=' + id + ']');
        },
        remove: function(remove) {
            _.remove(this.files, function(file) { return file.id == remove.id });
        },
        clear: function() {
            this.files = [];
            this.selected = false;
            this.filewidget.find('.files').html('');
            this.element.trigger('filefield.change');
            return this;
        },
        _set_selected: function(item) {
            item.addClass('selected'); 
            this.selected = item.data('id');
            this.selectable_field.val(this.selected);
        }
    }
    FileField.DEFAULTS = {}
    $.fn.filefield = function(option) {
        if (this.length == 0) 
            return;
        var args = arguments,
            init = function(filefield) {
                var data = filefield.data('filefield'),
                options = $.extend({}, FileField.DEFAULTS, typeof option === 'object' && option);

            if (!data) filefield.data('filefield', (data = new FileField(filefield, options)));
            if (typeof option === 'string') {
                if (typeof data[option] === 'function')
                    return data[option].apply(data, Array.prototype.slice.call(args,1))
                else if(typeof args[1] !== 'undefined') data[option] = args[1];     
                else return data[option];
            }    
        }
        if (this.length == 1) 
            return init(this)
        else this.each(function() {
            init($(this));
        });
        return this;
    }
    $('input:file.form-control').each(function () {
         $(this).filefield();        
    });
})(jQuery);