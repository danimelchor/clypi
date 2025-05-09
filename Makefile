.PHONY: publish tag docs

tag:
	./scripts/tag


docs:
	scripts/gen_readme
	pre-commit uninstall
	uv run --extra docs mkdocs gh-deploy
	pre-commit install
	rm -rf site

local-docs:
	uv run --extra docs mkdocs serve

publish: tag docs
