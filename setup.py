from setuptools import setup, find_packages

setup(
    name='PeakSense',
    version='0.0.0',
    author='Eric Cherny',
    author_email='ericlevcherny@gmail.com',
    description='PeakSense is a powerful tool for identifying peaks in transcription factor binding data, leveraging the capabilities of deep learning.',
    packages=find_packages(),
    install_requires=[
        'pysam==0.21.0',
        'pybedtools==0.9.0',
        'tqdm==4.61.2',
        'matplotlib==3.4.2',
        'pandas==1.5.3',
        'numpy',
        'scipy',
    ],
    python_requires='>3',
    entry_points={
        'console_scripts': [
            'peaksense=peaksense.peaksense:main'
        ]
    }
)