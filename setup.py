from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='deployserver',
    version='0.4.0',
    packages = find_packages(),
    description='Deploy your project automatically when git branch was updated.',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    keywords='automatically deploy git project',
    url='https://github.com/codex-team/deployserver',
    author='CodeX Team',
    author_email='team@ifmo.su',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Environment :: Console'
    ],
    install_requires=['aiohttp', 'asyncio'],
    python_requires='>=3.5'
)
