import setuptools


setuptools.setup(
    name='subsonic-cli',
    version='0.1.0',
    author='Andrew Rabert',
    author_email='ar@nullsum.net',
    license='Apache 2.0',
    py_modules=['subsonic_cli'],
    install_requires=['requests'],
    entry_points={
        'console_scripts': ['subsonic-cli=subsonic_cli:main']
    }
)
