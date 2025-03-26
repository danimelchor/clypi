.PHONY: publish tag docs

tag:
	./scripts/tag


docs:
	pre-commit uninstall
	uv run --extra docs mkdocs gh-deploy
	pre-commit install
	rm -rf site


publish: tag docs
