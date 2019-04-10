import setuptools
from distutils.core import setup
from Cython.Build import cythonize
import os

BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
            )
        )

print(BASE_DIR)

HARD_COMPILE_FILES = [
    'common_data\\middleware\\license.py',
    'common_data\\middleware\\users.py',
    'latrom\\settings\\base.py'
]

setup(
    ext_modules=cythonize([os.path.join(BASE_DIR, i) for i in HARD_COMPILE_FILES])
)