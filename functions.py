
def resizeImg(img, name, key):
    from PIL import Image
    import os, re

    pattern = r'\.([a-zA-Z0-9]+)$'
    match = re.search(pattern, name)
    if match:
        img_type = match.group(0)
    else:
        return False
    name = name[:-len(img_type)]
    target_size = (100, 100)
    img =Image.open(img)
    img_resized = img.resize(target_size, Image.BICUBIC)
    print("tohle je to jemnio", name)
    try:
        img_resized.save(f'static/images/{key}_!_{name}{img_type}')
        print(f"Returning {f'static/images/{key}_!_{name}{img_type}'}")
        return f'static/images/{key}_!_{name}{img_type}'
    except:
        return False
    
def resizeMovieImg(img, name, key):
    from PIL import Image
    import os 
    
    name = name[:-4]
    target_size = (100, 100)
    img =Image.open(img)
    img_resized = img.resize(target_size, Image.BICUBIC)
    print("tohle je to jemnio", name)
    try:
        img_resized.save(f'static/movie_images/{key}_!_{name}.jpg')
        print(f"Returning {f'static/movie_images/{key}_!_{name}.jpg'}")
        return f'static/images/{key}_!_{name}.jpg'
    except:
        print(f"Returning {f'static/movie_images/{key}_!_{name}.png'}")
        img_resized.save(f'static/movie_images/{key}_!_{name}.png')
        return f'static/movie_images/{key}_!_{name}.png'
   
