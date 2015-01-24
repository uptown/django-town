# -*- encoding: utf-8 -*-
# import cStringIO
from django.utils.six import BytesIO

from PIL import Image
from django.core.files.base import ContentFile
from django.db.models.fields.files import ImageFieldFile


def generate_thumb(img, thumb_size, extension, image_size=None):
    img.seek(0)  # see http://code.djangoproject.com/ticket/8222 for details
    image = Image.open(img)

    # Convert to RGB if necessary
    if image.mode not in ('L', 'RGB', 'RGBA'):
        image = image.convert('RGB')
    # get size
    thumb_w, thumb_h = thumb_size
    if not thumb_h:
        if not image_size:
            image_size = image.size
        xsize, ysize = image_size
        thumb_h = float(thumb_w) / xsize * ysize
    elif not thumb_w:
        if not image_size:
            image_size = image.size
        xsize, ysize = image_size
        thumb_w = float(thumb_h) / ysize * xsize
    # If you want to generate a square thumbnail
    if thumb_w == thumb_h:
        # quad
        if not image_size:
            image_size = image.size
        xsize, ysize = image_size
        # get minimum size
        minsize = min(xsize, ysize)
        # largest square possible in the image
        xnewsize = (xsize - minsize) / 2
        ynewsize = (ysize - minsize) / 2
        # crop it
        image2 = image.crop((xnewsize, ynewsize, xsize - xnewsize, ysize - ynewsize))
        # load is necessary after crop
        image2.load()
        # thumbnail of the cropped image (with ANTIALIAS to make it look better)
        image2.thumbnail((thumb_w, thumb_h), Image.ANTIALIAS)
    else:
        # not quad
        image2 = image
        image2.thumbnail((thumb_w, thumb_h), Image.ANTIALIAS)

    io = BytesIO()
    # PNG and GIF are the same, JPG is JPEG
    if extension.upper() == 'JPG':
        extension = 'JPEG'
    image2.save(io, extension)
    return ContentFile(io.getvalue()), (thumb_w, thumb_h)



def get_thumbnails(url, original_size, sizes):
    ret = []
    prefix = ''
    if '/' in url:
        prefix, url = url.rsplit('/', 1)
    for size in sizes:
        (w, h) = size
        split = url.rsplit('.', 1)
        if len(split) == 1:
            split.append('jpg')
        thumb_w, thumb_h = size
        if not thumb_h:
            xsize, ysize = original_size
            thumb_h = float(thumb_w) / xsize * ysize
        elif not thumb_w:
            xsize, ysize = original_size
            thumb_w = float(thumb_h) / ysize * xsize
        thumb_name = '%s.%sx%s.%s' % (split[0], w or '', h or '', split[1])
        ret.append({'url': prefix + '/' + thumb_name, 'wight': int(thumb_w), 'height': int(thumb_h)})
    sorted(ret, key=lambda k: k['wight'])
    return ret


class ThumbnailFile(ImageFieldFile):
    def __init__(self, *args, **kwargs):
        super(ThumbnailFile, self).__init__(*args, **kwargs)
        self.sizes = self.field.sizes

    def save(self, name, content, save=True):
        content.seek(0)
        super(ThumbnailFile, self).save(name, content, save)
        if self.sizes:
            for size in self.sizes:
                (w, h) = size
                split = self.name.rsplit('.', 1)
                if len(split) == 1:
                    split.append('jpg')
                thumb_content, size_unused = generate_thumb(content, (w, h), split[1],
                                                            image_size=(self.width, self.height))
                thumb_name = '%s.%sx%s.%s' % (split[0], w or '', h or '', split[1])
                thumb_name_ = self.storage.save(thumb_name, thumb_content)
                if not thumb_name == thumb_name_:
                    raise ValueError('There is already a file named %s' % thumb_name)

    def delete(self, save=True):
        name = self.name
        super(ThumbnailFile, self).delete(save)
        if self.sizes:
            for size in self.sizes:
                (w, h) = size
                split = name.rsplit('.', 1)
                if len(split) == 1:
                    split.append('jpg')
                thumb_name = '%s.%sx%s.%s' % (split[0], w or '', h or '', split[1])
                self.storage.delete(thumb_name)

    def get_thumbnails(self, url=None):
        ret = []
        if self.sizes:
            for size in self.sizes:
                (w, h) = size
                split = self.url.rsplit('.', 1) if not url else url.rsplit('.', 1)
                if len(split) == 1:
                    split.append('jpg')
                thumb_w, thumb_h = size
                if not thumb_h:
                    xsize, ysize = self.width, self.height
                    thumb_h = float(thumb_w) / xsize * ysize
                elif not thumb_w:
                    xsize, ysize = self.width, self.height
                    thumb_w = float(thumb_h) / ysize * xsize
                thumb_name = '%s.%sx%s.%s' % (split[0], w or '', h or '', split[1])
                ret.append({'source': thumb_name, 'wight': int(thumb_w), 'height': int(thumb_h)})
        sorted(ret, key=lambda k: k['wight'])
        return ret
