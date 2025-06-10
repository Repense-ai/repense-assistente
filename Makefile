build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

run:
	docker-compose up --build

lint:
	pre-commit run --all-files

install:
	pip install --upgrade pip
	pip install uv
	uv sync
