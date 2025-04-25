format:
	uv run autoflake --in-place -r --remove-all-unused-imports --remove-unused-variables .
	uv run autopep8 --recursive --in-place --select W292,W293,W391,E121,E122,E123,E126,E128,E129,E131,E202,E225,E226,E241,E301,E302,E303,E704,E731 .
	uv run ruff check --config pyproject.toml --fix .
	# Same line length as Black
	uv run isort --line-length 88 .

lint:
	uv run autoflake --check-diff -r --quiet \
		--remove-all-unused-imports --remove-unused-variables --remove-duplicate-keys .
	# W503 has been deprecated in favor of W504 - https://www.flake8rules.com/rules/W503.html
	uv run flake8 . --extend-exclude .venv --count --show-source --statistics --max-line-length=88 --ignore=E501,W503
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	uv run flake8 . --extend-exclude .venv --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	# Config file is specified for brevity
	uv run ruff check --config pyproject.toml .
	# Same line length as Black
	uv run isort --check --diff --line-length 88 .