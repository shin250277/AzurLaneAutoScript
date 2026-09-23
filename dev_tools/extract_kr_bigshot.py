"""Extract Korean raid labels from a 1280x720 ALAS diagnostic frame."""
import argparse
from pathlib import Path
from PIL import Image


AREAS = {
    'ui/RAID_CHECK_20260827': (130, 23, 208, 44),
    'raid/BIGSHOT_RAID_HARD': (1023, 397, 1077, 425),
    'raid/BIGSHOT_RAID_NORMAL': (980, 468, 1031, 495),
    'raid/BIGSHOT_RAID_EASY': (935, 548, 987, 577),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    parser.add_argument('--fleet-modal', action='store_true')
    parser.add_argument('--fleet-shortcut', action='store_true')
    parser.add_argument('--rewards', action='store_true')
    parser.add_argument('--ex-result', action='store_true')
    parser.add_argument('--ex-exp', action='store_true')
    args = parser.parse_args()
    areas = ({'raid/BIGSHOT_FLEET_HEADER': (126, 76, 255, 109),
              'raid/BIGSHOT_FLEET_CLOSE': (1145, 74, 1178, 108)}
             if args.fleet_modal else AREAS)
    if args.fleet_shortcut:
        areas = {'raid/RAID_FLEET_PREPARATION': (983, 579, 1180, 635)}
    if args.rewards:
        areas = {'raid/BIGSHOT_REWARDS_HEADER': (390, 135, 515, 166),
                 'raid/BIGSHOT_REWARDS_CLAIM': (794, 576, 852, 603)}
    if args.ex_result:
        areas = {'raid/KR_RAID_EX_RESULT': (132, 197, 497, 286)}
    if args.ex_exp:
        areas = {'raid/KR_RAID_EX_EXP': (62, 64, 282, 121),
                 'raid/KR_RAID_EX_CONFIRM': (1147, 649, 1208, 680)}
    targets = [(Path('assets/kr/' + name + '.png'), area) for name, area in areas.items()]
    if any(path.exists() for path, _ in targets):
        raise SystemExit('Asset exists; inspect before replacing')
    with Image.open(str(args.frame)) as source:
        if source.size != (1280, 720):
            raise ValueError('Expected 1280x720 diagnostic frame')
        for path, area in targets:
            canvas = Image.new('RGB', source.size)
            canvas.paste(source.crop(area).convert('RGB'), area)
            path.parent.mkdir(parents=True, exist_ok=True)
            canvas.save(str(path))


if __name__ == '__main__':
    main()
