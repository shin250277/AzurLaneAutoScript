"""Extract observed Korean daily-supply text from an ALAS diagnostic frame."""
import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    parser.add_argument('--state', choices=('CLAIM', 'COOLDOWN', 'RECEIVE', 'SHARE', 'COLLECT_ENTER',
                        'COLLECT_CONFIRM', 'COLLECT_CANCEL', 'COLLECT_START', 'COLLECT_START_UNAVAILABLE',
                        'DOCK_CHECK', 'DOCK_CONFIRM', 'DOCK_OCCUPIED'), default='CLAIM')
    args = parser.parse_args()
    name = ('ISLAND_COLLECT_SELECT_' + args.state.replace('COLLECT_', '')
            if args.state.startswith('COLLECT_') else 'ISLAND_FREEBIE_' + args.state)
    if args.state in ('COLLECT_START', 'COLLECT_START_UNAVAILABLE'):
        name = 'ISLAND_' + args.state
    if args.state.startswith('DOCK_'):
        name = 'ISLAND_DOCK_CHECK' if args.state == 'DOCK_CHECK' else 'ISLAND_DOCK_CHARACTER_CONFIRM'
    if args.state == 'DOCK_OCCUPIED':
        name = 'TEMPLATE_ISLAND_DOCK_OCCUPIED'
    folder = 'island_handler' if args.state.startswith('DOCK_') else 'island'
    target = Path('assets/kr/{}/{}.png'.format(folder, name))
    if target.exists():
        raise SystemExit('Asset exists; inspect before replacing')
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected 1280x720 diagnostic frame')
        area = {'CLAIM': (895, 380, 978, 405), 'COOLDOWN': (876, 380, 997, 406),
                'RECEIVE': (895, 380, 978, 406),
                'SHARE': (874, 380, 1003, 406),
                'COLLECT_ENTER': (900, 474, 1028, 500),
                'COLLECT_CONFIRM': (755, 543, 804, 571),
                'COLLECT_CANCEL': (478, 543, 528, 571),
                'COLLECT_START_UNAVAILABLE': (1023, 474, 1066, 500),
                'COLLECT_START': (1023, 474, 1066, 500),
                'DOCK_CHECK': (116, 20, 229, 47),
                'DOCK_CONFIRM': (1067, 595, 1114, 623),
                'DOCK_OCCUPIED': (78, 209, 158, 233)}[args.state]
        canvas = Image.new('RGB', frame.size)
        canvas.paste(frame.crop(area).convert('RGB'), area)
        if args.state == 'DOCK_OCCUPIED':
            canvas = frame.crop(area).convert('RGB')
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(target))


if __name__ == '__main__':
    main()
