"""Offline-only: replay live KR dock labels and keep only their masked crops."""
from pathlib import Path
import ast
import argparse
from PIL import Image
import numpy as np
from module.base.button import Button


def run(directory, apply):
    def snap(name):
        with Image.open(str(directory/(name+'.png'))) as img:
            assert img.size==(1282,761), img.size
            return np.asarray(img.convert('RGB').crop((1,40,1281,760)))
    src=Path('module/retire/assets.py')
    lines=src.read_text(encoding='utf8').splitlines(True)
    for name,area,source,second,neg in [
        ('DOCK_FILTER',(1100,7,1190,57),'dock','dock2','dockfilter'),
        ('DOCK_FILTER_CONFIRM',(712,642,888,703),'dockfilter','dockfilter2','dock2')]:
        ix=next(i for i,line in enumerate(lines) if line.startswith(name+' = '))
        call=ast.parse(lines[ix]).body[0].value
        f={k.arg:ast.literal_eval(k.value) for k in call.keywords}
        def det(region): return Button(**{k:v[region] for k,v in f.items()})
        old=det('jp')
        offset=(20,60)
        before=[old.match(snap(n),offset=offset) for n in (source,second)]
        print(name,'foreign:',before)
        if all(before):continue
        if any(before):raise ValueError('inconsistent baseline')
        im=Image.fromarray(snap(source))
        patch=im.crop(area)
        filename='./assets/kr/retire/'+name+'.png'
        masked=Image.new('RGB',im.size)
        masked.paste(patch,area[:2])
        color=tuple(int(x) for x in np.rint(np.asarray(patch).mean(axis=(0,1))))
        detector=Button(area,color,area,filename)
        detector.image=np.asarray(patch);detector._match_init=True
        results=[detector.match(snap(n),offset=offset) for n in (second,neg,'main2')]
        print(name,'KR positive, two negatives:',results)
        if results!=[True,False,False]:raise ValueError('label not distinctive')
        if apply:
            if Path(filename).exists():
                with Image.open(filename) as existing:
                    assert existing.convert('RGB').tobytes()==masked.tobytes()
            else:masked.save(filename)
            for k,v in dict(area=area,color=color,button=area,file=filename).items(): f[k]['kr']=v
            lines[ix]=name+' = Button('+', '.join(k+'='+repr(v) for k,v in f.items())+')\n'
    if apply:src.write_text(''.join(lines),encoding='utf8')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('directory',type=Path)
    p.add_argument('--apply',action='store_true')
    args=p.parse_args()
    run(args.directory,args.apply)
