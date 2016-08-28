import glob
import os
from distutils.core import setup


scripts = [f for f in glob.glob(os.path.join(__file__, "scripts/*.py")) if  f != '__init__.py']



setup(
        name='androtoolbox',
        version='0.1.1',
        packages=['androtoolbox'],
        url='https://github.com/gregthedoe/androtoolbox',
        license='MIT',
        author='greg',
        author_email='',
        description='A set of useful tools (or python wrappers) to work with android devices',
        scripts=scripts,
)
