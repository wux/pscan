from __future__ import print_function
import sys
import os
import fnmatch
from PIL import Image
import hashlib 
import pickle

def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

def is_image(filename, extensions=['.jpg', '.jpeg', '.gif', '.png']):
    return any(filename.lower().endswith(e) for e in extensions)

# Uses a generator
def photo_generator(root):
    for rootpath, subdirs, files in os.walk(os.path.abspath(root)):
        for filename in filter(is_image, files):
            yield os.path.join(rootpath, filename).replace('\\','/')

import PIL.ExifTags
def get_exif_tags(img):
    return {
        PIL.ExifTags.TAGS[k]: v
        for k, v in img._getexif().items()
        if k in PIL.ExifTags.TAGS
        }

def get_create_time(img):
    return img._getexif()[36867]

def main():
    parent = sys.argv[1]
    minsize = 512
 
    pbase = {}
    for image in photo_generator(parent):
        try:
            img = Image.open(image)
        except:
            e = sys.exc_info()[0]
            warning(image + " open err " + str(e))
            continue
        (width, height) = img.size
        if width < minsize or height < minsize:
            continue
        try:
            if img._getexif() is None:
                warning(image + "no exif")
                continue
            create_time = get_create_time(img)
        except:
            warning(image + "exif error")
            continue

        print('%s, %s, %s' % (image, str(img.size), str(create_time)))
        info = pickle.dumps(img._getexif())
        key = hashlib.md5(info).hexdigest()
        print("hash code: " + key)
        if key not in pbase:
            pbase[key] = []
        pbase[key].append(image)

    pickle.dump(pbase, open("pbase.db", "wb")) 


if __name__ == "__main__":
    main()
