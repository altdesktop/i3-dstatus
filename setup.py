from setuptools import setup, find_packages

setup(
    name='i3dstatus',
    version='0.0.1',
    author='Tony Crisci',
    author_email='tony@dubstepdish.com',
    url='https://github.com/acrisci/i3-dstatus',
    license='BSD',
    description='The ultimate DIY statusline generator for i3',
    long_description=open('README.rst').read(),

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],

    package_data={'i3dstatus': ['generators/*']},

    scripts=['i3-dstatus'],

    packages=find_packages(),
)
