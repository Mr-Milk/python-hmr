from pathlib import Path

from setuptools import setup

README = Path("README.md").read_text()

setup(name="python-hmr",
      packages=['hmr'],
      description="Hot module reload for python",
      long_description=README,
      long_description_content_type="text/markdown",
      version="0.1.0",
      author="Mr-Milk",
      url="https://github.com/Mr-Milk/python-hmr",
      author_email="zym.zym1220@gmail.com",
      license="MIT License",
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3",
      ],
      python_requires='>=3.6',
      install_requires=['watchdog'],
      )
