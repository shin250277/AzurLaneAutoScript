"""Offline whole-label distance diagnostics, never a game input path."""
from types import SimpleNamespace
from PIL import Image
import numpy as np
import cv2
import module.config.server as server
server.server = 'kr'
from module.base.utils import crop
from module.island_handler.recipe import IslandRecipe
from module.island_handler.korean_ocr import KoreanIslandNameOcr
from module.island_handler.korean_name_mask import glyph_mask


def score(a, b):
    if a is None or b is None or any(abs(x-y)>2 for x,y in zip(a.shape,b.shape)):
        return 0
    height, width = max(a.shape[0],b.shape[0])+4, max(a.shape[1],b.shape[1])+4
    left = np.zeros((height,width),np.uint8)
    left[2:2+a.shape[0],2:2+a.shape[1]] = a
    best = 0
    for dy in range(-2,3):
        for dx in range(-2,3):
            right = np.zeros_like(left)
            right[2+dy:2+dy+b.shape[0],2+dx:2+dx+b.shape[1]] = b
            ld = cv2.dilate(left,np.ones((3,3),np.uint8))
            rd = cv2.dilate(right,np.ones((3,3),np.uint8))
            coverage = min(np.count_nonzero((left>0)&(rd>0))/float(np.count_nonzero(left)),
                           np.count_nonzero((right>0)&(ld>0))/float(np.count_nonzero(right)))
            best = max(best,coverage)
    return best


if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('frame')
    p.add_argument('row',type=int)
    args=p.parse_args()
    im=np.array(Image.open(args.frame).convert('RGB'))
    ui=SimpleNamespace(image_crop=lambda area,copy=True:crop(im,area,copy=copy))
    ui._get_recipe_buttons=lambda:IslandRecipe._get_recipe_buttons(ui)
    grid=IslandRecipe.get_recipe_grid(ui)
    frame=cv2.cvtColor(crop(im,grid.crop((123,19,269,50)).buttons[args.row].area),cv2.COLOR_RGB2GRAY)
    for level in (110,130,150,170):
        ranked={}
        ncc={}
        for name,ref in KoreanIslandNameOcr([]).mask_references:
            a,b=glyph_mask(frame,level),glyph_mask(ref,level)
            ranked[name]=max(ranked.get(name,0),score(a,b))
            if a is not None and b is not None and all(abs(x-y)<=2 for x,y in zip(a.shape,b.shape)):
                v=cv2.minMaxLoc(cv2.matchTemplate(np.pad(a,2,mode='constant'),b,cv2.TM_CCOEFF_NORMED))[1]
                ncc[name]=max(ncc.get(name,0),v)
        print(level,sorted(((v,n) for n,v in ranked.items()),reverse=True)[:5])
        print('NCC',sorted(((v,n) for n,v in ncc.items()),reverse=True)[:5])
