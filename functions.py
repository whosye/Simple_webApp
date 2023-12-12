


def resizeImg(img_name):
    from PIL import Image
    import os 
    img = Image.open(os.path.join(os.path.abspath("static"), img_name))
    target_size = (100, 100)
    img_resized = img.resize(target_size, Image.BICUBIC)
    img_resized.save(os.path.join(os.path.abspath("static"), img_name))
    
