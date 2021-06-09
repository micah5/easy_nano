from distutils.core import setup

setup(
    name="easy_nano",
    packages=["easy_nano"],
    version="6",
    license="MIT",
    description="Send & recieve nano without the fuss",
    author="Micah Price",
    author_email="98mprice@gmail.com",
    url="https://github.com/micah5",
    download_url="https://github.com/micah5/easy_nano/archive/refs/tags/v_6.tar.gz",
    keywords=["nano"],
    install_requires=["requests", "PyQRCode", "click", "nanolib"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={"console_scripts": ["easy_nano=easy_nano:run"]},
)
