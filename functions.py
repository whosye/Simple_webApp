


def resizeImg(img, name, key):
    from PIL import Image
    import os 
    
    name = name[:-4]
    target_size = (100, 100)
    img =Image.open(img)
    img_resized = img.resize(target_size, Image.BICUBIC)
    print("tohle je to jemnio", name)
    img_resized.save(f'images/{key}_!_{name}.jpg')
   
