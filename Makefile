.AUTOFLAKE = $(shell autoflake --in-place --recursive --expand-star-imports --remove-duplicate-keys --remove-unused-variables --remove-all-unused-imports --ignore-init-module-imports wordmaze tests)
.UNIMPORT = $(shell unimport --remove --gitignore --ignore-init --include-star-import wordmaze tests)
.BLACK = $(shell black wordmaze tests)
.ISORT = $(shell isort wordmaze tests)
.REFACTOR = $(foreach command,.AUTOFLAKE .UNIMPORT .BLACK .ISORT,$(call $(command)))

.READD = $(shell git update-index --again)
.CHECK = $(shell pre-commit run)

coverage:
	@coverage run --source=wordmaze/ -m pytest tests/
	@coverage report -m

test:
	@pytest

check:
	@$(call $(.CHECK))

refactor:
	@$(call $(.REFACTOR))

autofix:
	@-$(call $(.REFACTOR))
	@$(call $(.READD))
	@-$(call $(.CHECK))
	@$(call $(.READD))

commit: autofix
	@cz commit

release:
# for v1.0.0 and after, the following line should be used to bump the project version:
# 	cz bump
# before v1, use the following command, which maps the following bumps:
# 	MAJOR -> MINOR (v0.2.3 -> v0.3.0)
# 	MINOR or PATCH -> PATCH (v0.2.3 -> v0.2.4)
# effectively avoiding incrementing the MAJOR version number while the first
# stable version (v1.0.0) is not released
	cz bump --dry-run --increment $(shell cz bump --dry-run | grep -q "MAJOR" && echo "MINOR" || echo "PATCH")
	git push
	git push --tags
