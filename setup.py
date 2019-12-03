import setuptools

import subsonic_cli


setuptools.setup(
    name='subsonic-cli',
    version=subsonic_cli.__version__,
    author='Andrew Rabert',
    author_email='ar@nullsum.net',
    license='MIT',
    py_modules=['subsonic_cli'],
    entry_points={
        'console_scripts': ['subsonic-cli=subsonic_cli:main']
    },
    url='https://gitlab.com/nvllsvm/subsonic-cli',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3 :: Only'
    ]
)
