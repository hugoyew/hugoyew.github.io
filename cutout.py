#!/usr/bin/env python3
"""Batch cutout life photos using rembg."""
import os, ssl
ssl._create_default_https_context = ssl._create_unverified_context
from rembg import remove, new_session
from PIL import Image

SRC = '/home/user/.super_doubao/super-doubao-runtime/workspace/site/assets/photos'
DST = os.path.join(SRC, 'cutout')
os.makedirs(DST, exist_ok=True)

photos = ['gym.jpg', 'nyc.jpg', 'coffee.jpg', 'referee.jpg', 'captain.jpg']
session = new_session('u2net')

for name in photos:
    src = os.path.join(SRC, name)
    dst = os.path.join(DST, name.replace('.jpg', '.png'))
    if os.path.exists(dst):
        print(f'skip {name} (exists)')
        continue
    print(f'cutout {name}...')
    img = Image.open(src)
    out = remove(img, session=session)
    out.save(dst, 'PNG')
    print(f'  -> {dst} ({out.size})')

print('done')
