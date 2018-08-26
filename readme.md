# Pycture

Pycture is a simple python 3 image manipulation application. It allows to modify several properties of an image, from color-balance to brightness; apply pre-defined filters and make all white pixels transparent (the transparency is lost if the image is not saved as a png).
Currently, supported image formats are jpeg, png and tiff. It can also be used to convert an image between such types of formats.
For images with a resolution greater than 1920x1080 pixels the application is considerably slow.
To start the application from command line type `python pycture.py`.

### Dependencies
- [pillow](https://python-pillow.org/)
- [PyQt5](https://pypi.org/project/PyQt5/)