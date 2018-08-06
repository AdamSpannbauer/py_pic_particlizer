from setuptools import setup

version = {}
with open("particlizer/version.py") as f:
    exec(f.read(), version)

setup(name='particlizer',
      version=version['__version__'],
      description='Turn images into particlized interactive animations',
      author='Adam Spannbauer',
      author_email='spannbaueradam@gmail.com',
      url='https://github.com/AdamSpannbauer/particlizer',
      packages=['particlizer'],
      license='MIT',
      install_requires=[
          'numpy',
          'imutils',
      ],
      extras_require={
          'cv2': ['opencv-contrib-python >= 3.4.0']
      },
      keywords=['computer vision', 'image processing', 'opencv'],
      )
