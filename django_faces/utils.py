try:
    from PIL import Image
except ImportError:
    import Image


def makeThumb(image, maxSize, method = 3): 
    'Resize PIL image, to fit into the maxSize'

    orig_size = image.size
    if orig_size[0] > maxSize[0] or orig_size[1] > maxSize[1]:
        min_extent = min( orig_size[0], orig_size[1] )
        left = (orig_size[0] - min_extent) / 2 
        top = (orig_size[1] - min_extent) / 2 
        result = image.crop( (left, top, left + min_extent, top + min_extent) )
        result = result.resize( maxSize, Image.ANTIALIAS )
        return (result, maxSize)
    else:
        return (image, orig_size)
