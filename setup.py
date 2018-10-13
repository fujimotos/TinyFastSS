from distutils.core import setup

setup(
    name='TinyFastSS',
    version='v2.0.2',
    py_modules=['fastss'],
    author='Fujimoto Seiji',
    author_email='fujimoto@ceptord.net',
    url='https://github.com/fujimotos/TinyFastSS',
    description='An efficient indexing data structure for string similarity search',
    long_description="""FastSS is an efficient indexing data structure
for string similarity search, invented by researchers at Zurich University
in 2007.

TinyFastSS is a simple Python implementation of FastSS, written in less than
300 LoC.""",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Indexing'
    ]
)
