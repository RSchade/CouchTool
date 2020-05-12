from setuptools import setup

setup(name="couchtool",
      version="1.0",
      description="Automated CouchDB configuration uploader",
      author="Raymond Schade",
      author_email="rayschade@gmail.com",
      license="MIT",
      packages=["couchtool"],
      dependencies=["requests"])
