;var FileBrowser = (function() { 
    var modal = $('#file_browser_modal'), 
        fb = {
            upload_url: '/upload/submit',
            delete_url: '/upload/delete',
            list_url: '/upload/list',
            body: $('.modal-body', modal),
            multiple: true,
            dir: '/',   
            getfiles: function() {
                $.get(this.list_url, function(json) {
                    fw.find('.files').html('');
                    fb.loaded_files = json;
                    fw.filewidget('loadfiles',json.dirs,'folder')
                    fw.filewidget('loadfiles',json.files);
                },'json');
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
            _onresize: function() {
                var height = $window.height() - 252;
                fb.body.height(height < 252 ? 252 : height)
            }

        }, 
        fw = $('.modal-body', modal).filewidget(), 
        shift = false, $window = $(window);
    fb.fw = fw; 
    
    $('.fileinput-button input', modal).fileupload({
        url: fb.upload_url,
        dataType: 'json',
        done: function(e, data) {
            fw.filewidget('loadfiles',data.result.files)
        }
    });
    $('.btn.btn-primary.submit', modal).on('click', function() {3
        fb.submit();
    });
    
    fw.on('click','.item-delete-wrapper', function() {
        var file = $(this).parents('.item'), data = file.data('info');
        alertify.confirm('Are you sure you wish to delete this file?', function(result) {
            if (!result)
                return;
            $.post(fb.delete_url,{id:data.id}, function(json) {
                if (json.success) {
                    alertify.success('Deleted file successfully.');
                    file.remove();
                } else {
                    alertify.error('Failed to remove file.')
                }
            },'json').fail(function() { alertify.error("Failed to remove file.") });
        });
    });

    fw.on('click', '.file .item-wrapper', function() {
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
        fb.getfiles().multiple = input.filefield('multiple');
        modal.one('submit-files',function(e,files) {
            if (input.length > 0) {
                input.filefield('val',files);
                modal.modal('hide');
            }
        });
    });

    $('body').keydown(function(e) {
        if (e.keyCode == 16)
            shift = true;
    }).keyup(function(e) {
        if (e.keyCode == 16)
            shift = false;
    });

    fb._onresize();
    $window.resize(fb._onresize);
    return fb;
})();
