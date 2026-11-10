"""Export the public Korean navigation button only, with all other pixels blank."""
from PIL import Image

if __name__ == '__main__':
    source = Image.open('log/kr_material_detail_1241.png').convert('RGB')
    if source.size != (1280, 720):
        raise ValueError('Unexpected resolution')
    area = (815, 472, 868, 495)
    output = Image.new('RGB', source.size)
    output.paste(source.crop(area), area[:2])
    output.save('assets/kr/island_handler/ISLAND_INFO_GOTO_SHOP.png')
    output = Image.new('RGB', source.size)
    for area in ((351, 157, 452, 192), (902, 156, 937, 192)):
        output.paste(source.crop(area), area[:2])
    output.save('assets/kr/ui/ISLAND_MATERIAL_DETAIL.png')
