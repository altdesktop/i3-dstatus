.PHONY: format lint
.DEFAULT_GOAL := all

source_dirs = i3dstatus

lint:
	flake8 $(source_dirs)

format:
	yapf -rip $(source_dirs)

all: format lint
