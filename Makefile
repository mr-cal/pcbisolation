HUGO ?= hugo

.PHONY: serve build validate lint format clean strip-exif setup

serve:
	$(HUGO) serve --buildDrafts --disableFastRender

build:
	$(HUGO) --minify

validate:
	python3 scripts/validate_content.py

lint: build
	uvx pre-commit run --all-files
	uvx pymarkdownlnt --config .pymarkdown scan --recurse content/
	lychee --offline --include-fragments public/ --root-dir public

format:
	$(HUGO) --minify 2>/dev/null; true

clean:
	rm -rf public/ resources/

strip-exif:
	scripts/strip-exif.sh

setup:
	uvx pre-commit install
	cargo install lychee
	sudo snap install hugo
