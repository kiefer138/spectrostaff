from setuptools import setup, find_packages

setup(
    name='spectrostaff',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'spectrostaff=spectrostaff.gui:main',
        ],
    },
    install_requires=[
        'numpy~=1.26.2',
        'PyAudio~=0.2.14',
        'setuptools~=68.2.2',
        'Wave~=0.0.2',
        'pyqtgraph~=0.13.3',
        'PyQt6~=6.6.0',
        'scipy~=1.11.4',
    ],
)