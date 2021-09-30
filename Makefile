coverage:
	@coverage run --source=wordmaze/ -m pytest tests/
	@coverage report -m

test:
	@pytest

refactor:
	@unimport --gitignore --ignore-init --include-star-import --remove wordmaze tests
	@black wordmaze tests
	@isort wordmaze tests
