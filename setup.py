from pathlib import Path

from setuptools import setup


def load_module_dict(filename: str) -> dict:
    import importlib.util as ilu
    filename = str(Path(__file__).parent / filename)
    spec = ilu.spec_from_file_location('', filename)
    module = ilu.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__dict__


name = "linecompress"

setup(
    name=name,
    version='0.2.0',
    author="Artёm IG",
    author_email="ortemeo@gmail.com",
    url='https://github.com/rtmigo/spacy_installer_py#readme',

    python_requires='>=3.7',  # from future import annotations
    install_requires=[""],
    packages=['linecompress'],

    description="",

    keywords="".split(),

    long_description=(Path(__file__).parent / 'README.md').read_text(),
    long_description_content_type='text/markdown',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ])

