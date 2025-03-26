.PHONY: publish tag

tag:
	./scripts/tag


publish:
	pre-commit uninstall
	uv run --extra docs mkdocs gh-deploy
	pre-commit install
	rm -rf site
