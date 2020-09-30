.PHONY: format lint
.DEFAULT_GOAL := all

source_dirs = i3dstatus
interface_dir = i3dstatus/interfaces

lint:
	flake8 $(source_dirs)

format:
	yapf -rip $(source_dirs)
	for iface in $(interface_dir)/*.xml ; do \
		formatted=`xmllint --format $$iface` && echo "$$formatted" > $$iface ; \
	done

publish:
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

all: format lint
