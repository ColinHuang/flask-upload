;window.FileBrowser = (function($, $window, $body, modal, shift) { 
    var fb = {
        upload_url: '/upload/',
        delete_file_url: '/upload/rm',
        list_url: '/upload/list',
        folder_url: '/upload/folder',
        move_url: '/upload/mv',
        body: $('.modal-body', modal).addClass('text-center').filewidget(),
        submit: $('.btn.submit', modal),
        multiple: true,
        folder: undefined,   

        create_folder: function(name) {
            $.post(this.folder_url, {
                parent: this.folder,
                name: name
            }, function(json) {

            }, 'json')
        },

        get_files: function() {
            modal.toggleClass('root', !this.folder).removeClass('is-empty');
            $.post(this.list_url, { folder: this.folder }, function(json) {
                fb.body.find('.files').html('');
                fb.loaded_files = json;
                fb._filewidget('loadfiles', json.folders, function(item, file) { 
                    item.addClass('folder').draggable({
                        revert: true,
                        delay: 337
                    }).droppable({
                        accept: '.item',
                        hoverClass: 'ui-item-over',
                        drop: fb._onfiledrop
                    }).find('.item-wrapper').append('<i class="glyphicon glyphicon-folder-open">');
                });
                fb._filewidget('loadfiles', json.files, function(item, file) {
                    item.addClass('file').draggable({
                        revert: true,
                        delay: 337
                    });
                });
                if (json.folders.length == 0 && json.files.length == 0) 
                    modal.addClass('is-empty')
            }, 'json');
            return this;
        },
        open: function() {
            modal.modal();
            return this;
        },
        close: function() {
            modal.modal('hide');
            return this;
        },
        up_folder: function() {

        },
        set_folder: function(folder) {
            this.folder = folder === 'undefined' ? undefined : folder;
            this.get_files();
            return this;
        },
        _delete_file: function(file) {
            var data = file.data('info');
            $.post(this.delete_file_url, { id: data.id }, function(json) {
                if (json.success) {
                    alertify.success('Deleted file successfully.');
                    file.remove();
                } else {
                    alertify.error('Failed to remove file.')
                }
            },'json').fail(function() { alertify.error("Failed to remove file.") });
        },
        _onresize: function() {
            var height = $window.height() - 252;
            fb.body.height(height < 252 ? 252 : height)
        },
        _onfiledrop: function(event, ui) {
            var data = { dest: $(this).data('id') };
            if (ui.draggable.hasClass('file'))
                data.files= [ui.draggable.data('id')];
            else 
                data.folder = ui.draggable.data('id');
            $.post(fb.move_url, data, function(json) {
                if (json.success) {
                    ui.draggable.fadeOut('fast', function() {
                        $(this).remove();
                    });
                }
            }, 'json');
        },
        _onsubmit: function() {
            var files = [];
            $('.item.selected', this.files).each(function() {
                files.push($(this).data('info'));
            });
            modal.trigger('submit-files', [files]);
        },
        _onfail: function() {
            return function() {  }
        },
        _filewidget: function() {
            return this.body.filewidget.apply(this.body, arguments);
        }
    }

    $('.fileinput-button input', modal).fileupload({
        url: fb.upload_url,
        dataType: 'json',
        formData: function() {
            return fb.folder ? [{ name: 'folder', value: fb.folder }] : [] ;
        },
        done: function(e, data) {
            fb._filewidget('loadfiles',data.result.files)
        }
    });

    fb.submit.on('click', fb._onsubmit);
    
    // Delete File
    fb.body.on('click','.item-delete-wrapper', function() {
        var file = $(this).parents('.item');
        alertify.confirm('Are you sure you wish to delete this file?', function(result) {
            if (result) 
                fb._delete_file(file);
        });
    })

    // Folder click
    .on('click', '.item.folder', function() {
        fb.set_folder($(this).data('id'));
    })

    // Select multiple items if shift is held down and multiple enabled
    .on('click', '.file .item-wrapper', function() {
        var item = $(this).parent();
        if (!shift || !fb.multiple)
            item.siblings().removeClass('selected');
        item.toggleClass('selected', !item.hasClass('selected'));
    });

    modal.on('show.bs.modal',function(e) {
        var button = $(e.relatedTarget),
            button_modal = button.parents('.modal'),
            filefield = button.parents('.file-field').find('input');

        fb.get_files();

        if (button.length == 0) {
            return fb.submit.hide();
        }

        fb.submit.show();
        button_modal.css('z-index', 1000);
        $(this).one('hide.bs.modal', function() {
            button_modal.css('z-index', 1040);
        });
        fb.multiple = filefield.filefield('multiple');
        modal.one('submit-files', function(e, files) {
            if (filefield.length > 0) {
                filefield.filefield('val', files);
                fb.close();
            }
        });
    }).on('shown.bs.modal', function() {
        $(document).off('focusin.bs.modal');
    });

    $('.up-folder', modal).click(function() {
        fb.up_folder()
    });

    $('.root-folder', modal).click(function() {
        fb.set_folder(undefined);
    });

    $('.create-folder', modal).click(function() {
        alertify.prompt('Please enter the folder name:', function(s, val) {
            if (s) 
                fb.create_folder(val);
        })
    });

    $body.keydown(function(e) {
        if (e.keyCode == 16)
            shift = true;
    }).keyup(function(e) {
        if (e.keyCode == 16)
            shift = false;
    });

    fb._onresize();
    
    $window.resize(fb._onresize);

    return fb;
})(jQuery, jQuery(window), jQuery('body'), jQuery('#file_browser_modal'), false);
