from setuptools import setup, find_packages

setup(
    name='i3-dstatus',
    version='0.0.3',
    author='Tony Crisci',
    author_email='tony@dubstepdish.com',
    url='https://github.com/acrisci/i3-dstatus',
    license='BSD',
    description='The ultimate DIY statusline generator for i3',
    long_description=open('README.rst').read(),

    install_requires=['PyYAML', 'netifaces', 'i3ipc', 'ijson'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],

    package_data={'i3dstatus': ['generators/*']},

    scripts=['i3-dstatus'],

    packages=find_packages(),
)
