from setuptools import setup, Extension

rawscreen = Extension(
    "rawscreen",
    sources=["rawscreen.c"],
    extra_compile_args=[
        "-O3",
        "-Wall",
        "-Wextra",
    ],
)

setup(
    name="rawscreen",
    version="1.0.0",
    ext_modules=[rawscreen],
)
