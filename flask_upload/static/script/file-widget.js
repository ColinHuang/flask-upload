;(function() {
    var FileWidget = function(element, options) {   
        var fw = this;   
        _.extend(this, options);
        this.$ = $(element).addClass('file-widget');
        this.files = $('<div/>',{'class':'files'}).appendTo(element);
        this.setview(this.view)
        this.setsize(this.size)
        this.files.on('click', '.item-delete-wrapper', function() {
            fw.$.trigger('delete-item', [$(this).parent()]);
        });
    }
    FileWidget.prototype = {
        _view: ['list','grid'],
        setview: function(view) {
            this.files.removeClass(this._view.join(' ')).addClass(view);
            this.view = view;
            return this;
        },  
        setsize: function(size) {
            this.files.removeClass('size' + _.range(10).join(' size')).addClass('size' + size);
            this.size = size
            return this;
        },
        makefile: function(name) {
            var file = ['<div class="item">',
                '<div class="item-delete-wrapper">',
                    '<div class="item-delete trans-super"><i class="glyphicon glyphicon-remove" /></div>',
                    '<div class="trans-bkgd" />',
                '</div>',
                '<div class="item-name-wrapper">',
                    '<div class="item-name trans-super" title=" ' + name + '">'+ name + '</div>',
                    '<div class="trans-bkgd" />',
                '</div>',
                '<div class="item-wrapper"/>',    
            '</div>'];
            this.$.trigger('makefile', [file])
            return $(file.join(''));
        },
        loadfiles: function(files, c) {
            if (typeof c === 'undefined') 
                c = 'file';
            for(var x = 0; x < files.length; x++) {
                var file = files[x], 
                    item = this.makefile(file.title).appendTo(this.files).addClass(c),
                    iw = item.find('.item-wrapper'),
                    size = iw.height();
                item.data('info', file);
                if (file.id)
                    item.attr('data-id', file.id);
                if (file.image) {
                    var img = $('<img/>',{src: file.web_path});

                    if (file.width > file.height) {
                        img.width('100%').css('margin-top', (size - ((size * file.height) / file.width)) / 2);
                    }
                    else {
                        img.height('100%');
                        item.css('text-align','center');
                    }
                    if (file.width < size || file.height < size) {
                        img.width('auto').height('auto').css({
                            'margin-top': (size - file.height)/2
                        })
                    }
                    iw.html(img);
                } else if (file.mime) 
                    file.addClass(file.mime.replace('/','_'));
            }
            return this;
        }
    };

    FileWidget.DEFAULTS = {
        size: 4, 
        view: 'grid'
    }

    $.fn.filewidget = function(option) {
        var args = arguments;
        return this.each(function() {
            var $this = $(this),
                data = $this.data('filewidget'),
                options = $.extend({}, FileWidget.DEFAULTS, typeof option === 'object' && option);
            if (!data) $this.data('filewidget', (data = new FileWidget(this, options)));
            if (typeof option === 'string') {
                if (typeof data[option] === 'function')
                    data[option].apply(data, Array.prototype.slice.call(args,1))
                else if(typeof args[1] !== 'undefined') data[option] = args[1];        
                else return data[option];      
            }     
        });
        return data;
    }
    
})();
