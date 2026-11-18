all: nuitka_build

nuitka_build:

	python -m nuitka BibiteLauncher.py --mode=standalone --enable-plugin=tk-inter --include-raw-dir=./included-plugins=included-plugins -oBibiteLauncher

linux:

	python -m nuitka BibiteLauncher.py --mode=standalone --enable-plugin=tk-inter --include-raw-dir=./included-plugins=included-plugins -oBibiteLauncher

windows:

	python -m nuitka BibiteLauncher.py --mode=standalone --enable-plugin=tk-inter --include-raw-dir=./included-plugins=included-plugins -oBibiteLauncher

.PHONY: clean-windows
clean-windows:

	rmdir /s BibiteLauncher.build BibiteLauncher.dist

.PHONY: clean-linux
clean-linux:

	rm -rf BibiteLauncher.build BibiteLauncher.dist
