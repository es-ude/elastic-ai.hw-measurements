from setuptools import setup
from Cython.Build import cythonize
from setuptools.extension import Extension

extensions = [
    Extension(
        name="usb_serial",
        sources=["usb_serial.pyx", "src/src_usb_serial.c"],  # Your source files
    )
]

setup(
    name="usb_serial",
    ext_modules=cythonize(extensions),
)
