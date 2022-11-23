import cv2
from math import ceil

# [3/4 --> 16/9]
def fix_aspect_ratio(img_file):
    """Returns path to new image that better fits the aspect ratio of a single-image post."""
    img = cv2.imread(img_file)
    img_ratio = img.shape[1]/img.shape[0]
    print(f'{img_file}: {img_ratio}')

    if img_ratio > 16/9:
        print('too wide; add height')
        x, y = img.shape[1], (img.shape[1]*9)/16
    elif img_ratio < 3/4:
        print('too skinny; add width')
        x, y = (img.shape[0]*3)/4, img.shape[0]
    else:
        print('ratio is good; no need to readjust')
        return img_file
    
    img_adjusted = cv2.copyMakeBorder(
        img,
        top=ceil((y-img.shape[0])/2),
        bottom=ceil((y-img.shape[0])/2),
        left=ceil((x-img.shape[1])/2),
        right=ceil((x-img.shape[1])/2),
        borderType=cv2.BORDER_REPLICATE
    )
    adjusted_file = f'{img_file.rsplit(".", 1)[0]}_adjusted.png'
    cv2.imwrite(filename=adjusted_file, img=img_adjusted)
    return adjusted_file