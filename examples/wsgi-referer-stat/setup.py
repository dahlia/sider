try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(name='Sider-wsgi-referer-stat',
      packages=['sider_wsgi_referer_stat'],
      include_package_data=True,
      package_data={'sider_wsgi_referer_stat': ['templates/stat.html']},
      version='20120426',
      license='Public Domain',
      author='Hong Minhee',
      author_email='minhee' '@' 'dahlia.kr',
      install_requires=['Sider', 'Jinja2>=2.6'])

