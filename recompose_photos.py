#!/usr/bin/env python3
"""Rebuild life photos: blurred original background + sharp original foreground (rounded).
No more cutout — keeps full figure, avoids 'no head/no feet' problem."""
from PIL import Image, ImageFilter, ImageDraw
import os

SITE = '/home/user/.super_doubao/super-doubao-runtime/workspace/site'
SRC = os.path.join(SITE, 'assets/photos')
OUT = os.path.join(SITE, 'assets/photos/composed')
os.makedirs(OUT, exist_ok=True)

CANVAS = (1024, 1280)
BLUR_RADIUS = 28
FG_RATIO = 0.68  # foreground width as fraction of canvas width

def cover_crop(img, tw, th):
    """Center-crop image to exactly tw x th (cover fit)."""
    w, h = img.size
    scale = max(tw / w, th / h)
    nw, nh = int(w * scale), int(h * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))

def rounded_mask(size, radius):
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, size[0]-1, size[1]-1], radius=radius, fill=255)
    return mask

items = ['gym', 'nyc', 'coffee', 'referee', 'captain']

for name in items:
    src_path = os.path.join(SRC, f'{name}.jpg')
    if not os.path.exists(src_path):
        print(f'skip {name}: not found'); continue
    img = Image.open(src_path).convert('RGB')
    
    # background: cover-crop to canvas, heavy blur, darken slightly
    bg = cover_crop(img, CANVAS[0], CANVAS[1])
    bg = bg.filter(ImageFilter.GaussianBlur(radius=BLUR_RADIUS))
    # darken bg for text readability
    from PIL import ImageEnhance
    bg = ImageEnhance.Brightness(bg).enhance(0.55)
    
    # foreground: scale to FG_RATIO of canvas width, keep aspect
    fw = int(CANVAS[0] * FG_RATIO)
    fh = int(fw * img.size[1] / img.size[0])
    fg = img.resize((fw, fh), Image.LANCZOS)
    
    # round corners
    radius = 28
    mask = rounded_mask((fw, fh), radius)
    
    # compose: bg full, fg centered horizontally, slightly above center
    canvas = bg.copy()
    fx = (CANVAS[0] - fw) // 2
    fy = int(CANVAS[1] * 0.46) - fh // 2  # slightly above center
    canvas.paste(fg, (fx, fy), mask)
    
    out_path = os.path.join(OUT, f'{name}.jpg')
    canvas.save(out_path, 'JPEG', quality=88)
    print(f'composed {name}: {fw}x{fh} fg on {CANVAS} canvas -> {out_path}')

print('done')
