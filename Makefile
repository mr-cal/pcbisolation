HUGO ?= hugo
HUGO_VERSION ?= 0.147.1

.PHONY: serve build lint test clean strip-exif setup

serve:
	$(HUGO) serve --buildDrafts --disableFastRender

build:
	$(HUGO) --minify

lint: build
	uvx pre-commit run --all-files
	uvx pymarkdownlnt --config .pymarkdown scan --recurse content/
	lychee --offline --include-fragments public/ --root-dir public

test: build
	BASE_URL=http://localhost:1313 $(HUGO) serve --disableFastRender &
	sleep 2
	BASE_URL=http://localhost:1313 npx playwright test --project=chromium; \
	  kill $$(lsof -ti:1313) 2>/dev/null || true

format:
	$(HUGO) --minify 2>/dev/null; true
	uvx pymarkdownlnt --config .pymarkdown fix --recurse content/

clean:
	rm -rf public/ resources/

strip-exif:
	scripts/strip-exif.sh

setup:
	uvx pre-commit install
	cargo install lychee
	sudo snap install hugo
	npm install
