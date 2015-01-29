from PIL import Image

import pickle

pbase = pickle.load(open("pbase.db", "rb"))

size = 512, 512
total = 0
show = False
for key in pbase:
    if len(pbase[key]) > 1:
        total += len(pbase[key]) - 1
        print('Possible dup found')
        for v in pbase[key]:
            print(v)
            if show:
                im = Image.open(v)
                im.thumbnail(size)
                im.show(title=v)
        if show:
            raw_input('cont...')
print("Total dup found %d" % total)
