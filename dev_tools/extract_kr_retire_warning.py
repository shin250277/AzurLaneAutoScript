"""Extract only the non-personal KR retirement warning label from an ALAS error frame."""
import argparse
from pathlib import Path
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frame', type=Path)
    parser.add_argument('--quarters-shop', action='store_true',
                        help='Extract the private quarters shop title instead')
    parser.add_argument('--quarters-confirm', action='store_true',
                        help='Extract the gift purchase confirmation and coin icon')
    args = parser.parse_args()
    with Image.open(str(args.frame)) as frame:
        if frame.size != (1280, 720):
            raise ValueError('Expected a 1280x720 ALAS error frame')
        area = (124, 17, 218, 47) if args.quarters_shop else (441, 250, 835, 278)
        if args.quarters_confirm:
            area = (790, 577, 842, 600)
        asset = Image.new('RGB', frame.size)
        asset.paste(frame.crop(area).convert('RGB'), area)
        if args.quarters_confirm:
            coin_area = (394, 426, 425, 455)
            asset.paste(frame.crop(coin_area).convert('RGB'), coin_area)
    relative = ('assets/kr/private_quarters/PRIVATE_QUARTERS_SHOP_CHECK.png'
                if args.quarters_shop else 'assets/kr/retire/KR_RETIRE_RARITY_WARNING.png')
    if args.quarters_confirm:
        relative = 'assets/kr/private_quarters/KR_GIFT_PURCHASE_CONFIRM.png'
    output = Path(__file__).resolve().parents[1] / relative
    asset.save(str(output))
    print(output)


if __name__ == '__main__':
    main()
