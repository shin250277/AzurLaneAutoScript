"""Extract observed island page titles, without account or inventory data."""
import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    parser.add_argument('--page', choices=('order', 'season', 'tasks', 'task', 'obtained'), required=True)
    parser.add_argument('--task-id', type=int)
    parser.add_argument('--area', type=int, nargs=4)
    args = parser.parse_args()
    if args.page in ('task', 'obtained'):
        if args.page == 'task' and (not args.task_id or not args.area):
            parser.error('task extraction requires --task-id and --area')
        target = (Path('assets/kr/island_task_name/%s.png' % args.task_id)
                  if args.page == 'task' else
                  Path('assets/kr/island/TEMPLATE_ISLAND_SEASON_TASK_OBTAINED.png'))
        if target.exists():
            raise SystemExit('Refusing to replace a verified asset')
        area = tuple(args.area) if args.area else (708, 320, 779, 346)
        with Image.open(str(args.frame)) as frame:
            if frame.size != (1280, 720):
                raise ValueError('Expected 1280x720 ALAS diagnostic frame')
            target.parent.mkdir(parents=True, exist_ok=True)
            frame.crop(area).convert('RGB').save(str(target))
        return
    if args.page == 'tasks':
        # First visible task grid observed on 2026-10-01; title crops only.
        ids = (80001402, 80001406, 80001407, 80001408, 80001409, 80001410)
        folder = Path('assets/kr/island_task_name')
        targets = [folder / ('%s.png' % code) for code in ids]
        if any(path.exists() for path in targets):
            raise SystemExit('Refusing to replace verified task names')
        with Image.open(str(args.frame)) as frame:
            if frame.size != (1280, 720):
                raise ValueError('Expected 1280x720 ALAS diagnostic frame')
            folder.mkdir(parents=True, exist_ok=True)
            for index, target in enumerate(targets):
                x, y = 71 + (index % 3) * 395, 200 + (index // 3) * 230
                frame.crop((x, y, x + 241, y + 30)).convert('RGB').save(str(target))
        return
    target = Path('assets/kr/ui/ISLAND_%s_CHECK.png' % args.page.upper())
    if target.exists():
        raise SystemExit('Refusing to replace a verified asset')
    area = (125, 19, 220, 46)
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected 1280x720 ALAS diagnostic frame')
        canvas = Image.new('RGB', frame.size)
        canvas.paste(frame.crop(area).convert('RGB'), area)
        canvas.save(str(target))


if __name__ == '__main__':
    main()
