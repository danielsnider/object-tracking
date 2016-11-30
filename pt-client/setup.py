import setuptools

try:
    import multiprocessing  # noqa
except ImportError:
    pass

setuptools.setup(
    setup_requires=['pbr'],
    pbr=True)
