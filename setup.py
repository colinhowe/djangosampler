from setuptools import setup
    
import os

root_dir = os.path.dirname(__file__)
if not root_dir:
    root_dir = '.'
long_desc = open(root_dir + '/README.rst').read()

setup(
	name='djangosqlsampler',
	version='0.2.0',
	description='Samples a percentage of SQL queries and groups them together for easy viewing',
	url='https://github.com/colinhowe/djangosqlsampler',
	author='Colin Howe',
	author_email='colin@colinhowe.co.uk',
	packages=['djangosqlsampler'],
    package_data={'djangosqlsampler': ['templates/djangosqlsampler/*','static/djangosqlsampler/*']},
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
	license='Apache 2.0',
	long_description=long_desc,
)
