"""Extract the observed Korean OpSi EMP icon, excluding account information."""
from pathlib import Path
from PIL import Image


def main():
    target = Path('assets/kr/os/FLEET_EMP_DEBUFF.png')
    fixture = Path('dev_tools/fixtures/kr_os_emp_status.png')
    if target.exists() or fixture.exists():
        raise SystemExit('Refusing to overwrite existing evidence')
    with Image.open('log/kr_os_auto_search_info_end.png') as source:
        if source.size != (1280, 720):
            raise ValueError('Expected game frame')
        for path, area in ((target, (297, 82, 335, 105)),
                           (fixture, (120, 70, 500, 170))):
            frame = Image.new('RGB', source.size)
            frame.paste(source.crop(area).convert('RGB'), area)
            frame.save(str(path))


if __name__ == '__main__':
    main()
