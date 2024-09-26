from setuptools import setup, find_packages

setup(
    name="my_eeg_visualizer",
    version="0.1.0",
    description="A real-time EEG visualizer using Lab Streaming Layer",
    author="Your Name",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "mne",
        "pylsl",
        "matplotlib",
        "pyqt5",
    ],
    entry_points={
        'console_scripts': [
            'eeg_visualizer=src.visualizer:main',
        ],
    },
)
