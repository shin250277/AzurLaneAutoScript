"""Extract only the observed KR use label, never account details."""
import argparse
import ast
from pathlib import Path
from PIL import Image
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('screenshot')
    parser.add_argument('--amount-confirm', action='store_true')
    parser.add_argument('--storage-full', action='store_true')
    parser.add_argument('--disassemble-cancel', action='store_true')
    parser.add_argument('--disassemble-confirm', action='store_true')
    parser.add_argument('--disassemble-popup', action='store_true')
    args = parser.parse_args()
    name = 'BOX_AMOUNT_CONFIRM' if args.amount_confirm else 'BOX_USE'
    area = (809, 613, 868, 645) if args.amount_confirm else (750, 494, 823, 528)
    click_area = (752, 600, 927, 660) if args.amount_confirm else (710, 484, 867, 536)
    if args.storage_full:
        name = 'EQUIPMENT_FULL'
        area = (368, 312, 626, 341)
        click_area = (413, 487, 569, 538)
    if args.disassemble_cancel:
        name = 'DISASSEMBLE_CANCEL'
        area = (908, 656, 968, 692)
        click_area = (865, 650, 1011, 700)
    if args.disassemble_confirm:
        name = 'DISASSEMBLE_CONFIRM'
        area = (1112, 656, 1179, 692)
        click_area = (1071, 650, 1221, 700)
    if args.disassemble_popup:
        name = 'DISASSEMBLE_POPUP_CONFIRM'
        # Identify the materials-received dialog, not a generic blue confirm.
        area = (584, 173, 693, 195)
        click_area = (708, 557, 851, 603)
    with Image.open(args.screenshot) as source:
        if source.size != (1280, 720):
            raise ValueError('Expected 1280x720 game screenshot')
        label = source.convert('RGB').crop(area)
    target = Path('assets/kr/storage') / (name + '.png')
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new('RGB', (1280, 720))
    canvas.paste(label, area)
    canvas.save(str(target))
    color = tuple(int(v) for v in np.asarray(label).mean(axis=(0, 1)))
    path = Path('module/storage/assets.py')
    lines = path.read_text(encoding='utf-8').splitlines()
    for i, line in enumerate(lines):
        if line.startswith(name + ' = Button('):
            call = ast.parse(line).body[0].value
            fields = {k.arg: ast.literal_eval(k.value) for k in call.keywords}
            for field, value in [('area', area), ('color', color),
                                 ('button', click_area),
                                 ('file', './' + target.as_posix())]:
                fields[field]['kr'] = value
            lines[i] = name + ' = Button(' + ', '.join(
                '{}={!r}'.format(k, v) for k, v in fields.items()) + ')'
            break
    else:
        raise ValueError(name + ' definition missing')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
