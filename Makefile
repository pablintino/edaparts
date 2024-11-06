DOCKER_IMAGE_TAG ?= edaparts:latest

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

.PHONY: setup_env
setup_env:
ifeq (,$(wildcard ${ROOT_DIR}/.venv/bin/python))
	$(eval $(call vars,$@))
	rm -rf ${ROOT_DIR}/.venv
	python -m venv ${ROOT_DIR}/.venv
	pip install build
	${ROOT_DIR}/.venv/bin/pip install -e .[dev]
endif

.PHONY: clean
clean:
	rm -rf ${ROOT_DIR}/dist ${ROOT_DIR}/edaparts.egg-info

.PHONY: build
build: setup_env clean
	${ROOT_DIR}/.venv/bin/python3 -m build ${ROOT_DIR}

.PHONY: build_docker
build_docker: build
	docker image build -f container/Containerfile -t ${DOCKER_IMAGE_TAG} --no-cache --progress plain .
