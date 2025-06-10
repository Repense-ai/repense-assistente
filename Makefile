GIT_COMMIT ?= $(shell git rev-parse --short HEAD)

build:
	echo $(GIT_COMMIT) > app/VERSION
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

run:
	echo $(GIT_COMMIT) > app/VERSION
	docker-compose up --build

lint:
	pre-commit run --all-files

install:
	pip install --upgrade pip
	pip install uv
	uv sync
