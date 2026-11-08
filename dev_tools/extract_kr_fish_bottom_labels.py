"""Extract only four public labels from the observed 1280x720 bottom list."""
import argparse
from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', help='Observed bottom list: bream, porgy, tuna, cucumber')
    parser.add_argument('--up', action='store_true', help='Observed upward scroll: tuna/salmon/bream/porgy')
    parser.add_argument('--middle', action='store_true', help='Observed squid/mackerel rows')
    parser.add_argument('--salmon-top', action='store_true', help='Observed salmon top decoration')
    parser.add_argument('--mackerel-replay', action='store_true', help='Public failed OCR crop, not a matching template')
    parser.add_argument('--tuna-replay', action='store_true', help='Public decorated tuna OCR crop')
    parser.add_argument('--tuna-selected', action='store_true', help='Observed selected tuna at y159')
    parser.add_argument('--tuna-ambiguous', action='store_true', help='Public ambiguous tuna crop at y201')
    parser.add_argument('--tuna-dot', action='store_true', help='Observed tuna with threshold-dependent background dot')
    parser.add_argument('--mackerel-decoration', action='store_true', help='Observed mackerel at detected y278')
    parser.add_argument('--mackerel-localized', action='store_true', help='Public failed mackerel crop at y231')
    args = parser.parse_args()
    with Image.open(args.frame) as source:
        if source.size != (1280, 720):
            raise ValueError('Unexpected frame size')
        if args.mackerel_localized:
            source.convert('RGB').crop((304, 231, 450, 254)).save(
                'dev_tools/fixtures/kr_mackerel_localized_name.png')
            raise SystemExit(0)
        if args.mackerel_decoration:
            source.convert('RGB').crop((304, 278, 450, 301)).save(
                'assets/kr/island_item_name/5102_recipe_decoration_selected.png')
            raise SystemExit(0)
        if args.tuna_dot:
            source.convert('RGB').crop((304, 456, 450, 479)).save(
                'dev_tools/fixtures/kr_tuna_dot_name.png')
            raise SystemExit(0)
        if args.mackerel_replay:
            source.convert('RGB').crop((304, 266, 450, 289)).save(
                'dev_tools/fixtures/kr_mackerel_name.png')
            raise SystemExit(0)
        if args.tuna_replay:
            source.convert('RGB').crop((304, 84, 450, 107)).save(
                'dev_tools/fixtures/kr_tuna_decoration_name.png')
            raise SystemExit(0)
        if args.tuna_ambiguous:
            source.convert('RGB').crop((304, 201, 450, 224)).save(
                'dev_tools/fixtures/kr_tuna_ambiguous_name.png')
            raise SystemExit(0)
        rows = ([(5103, 78), (5104, 227), (5105, 376), (5106, 525)] if args.up
                else [(5105, 94), (5106, 243), (5107, 392), (5108, 541)])
        suffix = 'up' if args.up else 'bottom'
        if args.middle:
            rows, suffix = [(5101, 384), (5102, 533)], 'middle'
        if args.salmon_top:
            rows, suffix = [(5104, 82)], 'top'
        if args.tuna_selected:
            rows, suffix = [(5103, 159)], 'selected'
        for item, y in rows:
            source.convert('RGB').crop((304, y, 450, y + 23)).save(
                'assets/kr/island_item_name/{}_recipe_{}.png'.format(item, suffix))
