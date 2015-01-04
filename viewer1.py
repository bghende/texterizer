__author__ = 'bghende'
from skimage import data
from skimage.viewer import ImageViewer
from skimage.viewer.plugins.lineprofile import LineProfile

image = data.coins()


viewer = ImageViewer(image)
viewer += LineProfile(viewer)
overlay, data = viewer.show()[0]