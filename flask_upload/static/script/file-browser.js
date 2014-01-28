;window.FileBrowser = (function($, $window, $body, modal, shift) { 
    var fb = {
        upload_url: '/upload/submit',
        delete_file_url: '/upload/delete/file',
        list_url: '/upload/list',
        folder_url: '/upload/folder',
        move_url: '/upload/mv',
        body: $('.modal-body', modal),
        filewidget: $('.modal-body', modal).filewidget(),
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
                    item.addClass('folder').droppable({
                        accept: '.file',
                        drop: fb._onfiledrop
                    });
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
        submit: function() {
            var files = [];
            $('.item.selected', this.files).each(function() {
                files.push($(this).data('info'));
            });
            modal.trigger('submit-files', [files]);
        },
        open: function() {
            modal.modal();
            return this;
        },
        close: function() {
            modal.modal('hide');
            return this;
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
            var folder = $(this).data('id');
            $.post(fb.move_url, { 
                files: [ui.draggable.data('id')],
                folder_id: folder === 'undefined' ? undefined : folder
            }, function(json) {
                if (json.success) {
                    ui.draggable.fadeOut('fast', function() {
                        $(this).remove();
                    });
                }
            }, 'json');
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
        done: function(e, data) {
            fb._filewidget('loadfiles',data.result.files)
        }
    });

    $('.btn.btn-primary.submit', modal).on('click', fb.submit);
    
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
        var $item = $(this).parent();
        if (!shift || !fb.multiple)
            $item.siblings().removeClass('selected');
        $item.addClass('selected');
    });

    modal.on('show.bs.modal',function(e) {
        var $rt = $(e.relatedTarget),
            rtmodal = $rt.parents('.modal'),
            field = $rt.parents('.file-field'),
            input = field.find('input');
        rtmodal.css('z-index',1000);
        $(this).one('hide.bs.modal', function() {
            rtmodal.css('z-index',1040);
        });
        fb.get_files().multiple = input.filefield('multiple');
        modal.one('submit-files', function(e, files) {
            if (input.length > 0) {
                input.filefield('val', files);
                modal.modal('hide');
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

    //$('.modal-footer .btn', modal).tooltip();

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
