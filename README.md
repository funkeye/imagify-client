# imagify-client

Imagify-client is a simple python based scripte, that allows you to optimize (recursive) all images in an folder. It also searches for subfolder and files in it. As the name says, it works with the [Imagify.io](https://imagify.io/docs/api/) API.

# Why?
from time to time i want to optimize all images from an web project. So i just modify the config.ini and run the client. i've just coded it for myself, so sorry for any bad code or comments ;)

# Requirements
- Python 3
- [imagify-python](https://pypi.org/project/imagify-python/)
- an [API Key](https://imagify.io/documentation/where-is-my-api-key/)

# PyInstaller
If you want an .exe file just install [PyInstaller](https://www.pyinstaller.org/downloads.html) and run the following line in your console:

```
pyinstaller --onefile client.py
```
