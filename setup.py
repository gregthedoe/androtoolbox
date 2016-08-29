import glob
import os
from setuptools import setup, find_packages

# Find all of the console scripts
console_scripts = []
for filename in glob.glob('androtoolbox/commandline/*'):
    filename = os.path.basename(filename)
    filename, ext = os.path.splitext(filename)

    if ext != '.py' or '__init__' in filename:
        continue

    script = '%s=androtoolbox.commandline.%s:main' % (filename, filename)
    console_scripts.append(script)

install_requires = [
    'attrs>=16.0.0'
]

setup(
        name='androtoolbox',
        version='0.1.3',
        packages=find_packages(),
        url='https://github.com/gregthedoe/androtoolbox',
        license='MIT',
        author='greg',
        author_email='',
        description='A set of useful tools (or python wrappers) to work with android devices',
        install_requires=install_requires,
        entry_points={'console_scripts': console_scripts},
)
