lint:
	uv run black .
	uv run isort .
	uv run ruff check --fix .
	uv run autoflake --in-place -r --remove-all-unused-imports --remove-unused-variables .
	uv run flake8 .

pre-commit:
	uv run pre-commit run --all-files
