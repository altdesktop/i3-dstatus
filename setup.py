from setuptools import setup, find_packages

setup(
    name='i3-dstatus',
    version='0.1.1',
    author='Tony Crisci',
    author_email='tony@dubstepdish.com',
    url='https://github.com/altdesktop/i3-dstatus',
    license='BSD',
    description='The ultimate DIY statusline generator for i3',
    long_description=open('README.rst').read(),

    install_requires=['PyYAML', 'netifaces', 'i3ipc', 'requests', 'dbus-next', 'python-xlib'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],

    package_data={'i3dstatus': ['generators/*', 'interfaces/*']},

    scripts=['i3-dstatus'],

    packages=find_packages(),
)
