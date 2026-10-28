help:
	@echo "###"
	@echo "# Build targets for Dinh Tuong"
	@echo "###"
	@echo
	@echo "  make build:  Builds the fonts and places them in the fonts/ directory"
	@echo "  make test:   Tests the fonts with fontspector (Google Fonts profile)"
	@echo "  make proof:  Creates HTML proof documents in out/proof"
	@echo

build: build.stamp

venv: venv/touchfile

venv/touchfile: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/touchfile

build.stamp: venv sources/build.sh $(wildcard sources/dinhtuong/*.py) $(wildcard sources/dinhtuong/*.json)
	. venv/bin/activate; sh sources/build.sh && touch build.stamp

test: build.stamp
	which fontspector || (echo "fontspector not found. Please install it with 'cargo binstall fontspector'." && exit 1)
	TOCHECK=$$(find fonts/ttf -type f 2>/dev/null); mkdir -p out/ out/fontspector; fontspector --profile googlefonts -l warn --full-lists --succinct --html out/fontspector/fontspector-report.html --ghmarkdown out/fontspector/fontspector-report.md --badges out/badges $$TOCHECK  || echo '::warning file=sources/build.sh,title=fontspector failures::The fontspector QA check reported errors in your font. Please check the generated report.'

proof: venv build.stamp
	which diff3proof || (echo "diff3proof not found. Please install it with 'cargo binstall diffenator3'." && exit 1)
	TOCHECK=$$(find fonts/ttf -type f 2>/dev/null); . venv/bin/activate; mkdir -p out/ out/proof; diff3proof $$TOCHECK --output out/proof

clean:
	rm -rf venv build.stamp sources/out
	find . -name "*.pyc" -delete
