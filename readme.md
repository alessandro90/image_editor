# Simple image editor

Pycture is a simple python 3 image manipulation application. It allows to modify several properties of an image. Single RGB channels as well as color-balance, contrast, brightness and sharpness can be modified. It is possible to apply some pre-defined filters and make all white pixels transparent (the transparency is lost if the image is not saved as a png).
Currently, supported image formats are jpeg, png and tiff. It can also be used to convert an image between such types of formats.
When saving a file, do not specify an extension in the name. The extension will be the one specified below. If you provide a name with an extension (*e.g.,* "img.jpg"), it will be ignored. 
For images with a resolution greater than 1920x1080 pixels the application is considerably slow (especially the sliders).
To start the application from command line type `python pycture.py`.

#### Dependencies
- [pillow](https://python-pillow.org/)
- [PyQt5](https://pypi.org/project/PyQt5/)