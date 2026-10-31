help:
	@echo "###"
	@echo "# Build targets for Dinh Tuong"
	@echo "###"
	@echo
	@echo "  make build:    Builds the fonts from sources/ufo with gftools builder (fontmake) into fonts/"
	@echo "  make vf: venv
	. venv/bin/activate; python3 scripts/make_vf_sources.py && fontmake -m "sources/vf/DinhTuong[wght].designspace" -o variable --output-path "fonts/variable/DinhTuong[wght].ttf" && python3 scripts/vf_vs_static.py

generate: Regenerates sources/ufo from the rule-based generators (sources/dinhtuong)"
	@echo "  make compare:  Checks the fontmake build against the generators' reference binaries"
	@echo "  make test:   Tests the fonts with fontspector (Google Fonts profile)"
	@echo "  make proof:  Creates HTML proof documents in out/proof"
	@echo

build: build.stamp

venv: venv/touchfile

venv/touchfile: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt > venv-install.log 2>&1 || (python3 scripts/ci_log.py venv-install.log pip; exit 1)
	touch venv/touchfile

build.stamp: venv sources/config.yaml $(shell find sources/ufo -type f)
	rm -rf fonts; . venv/bin/activate; gftools builder sources/config.yaml > build.log 2>&1 || (python3 scripts/ci_log.py build.log build; exit 1)
	touch build.stamp

generate:
	pip install -r requirements-generate.txt; sh sources/generate.sh

compare: build.stamp
	. venv/bin/activate; python3 scripts/compare_build.py sources/reference/fonts fonts

test: build.stamp
	which fontspector || (echo "fontspector not found. Please install it with 'cargo binstall fontspector'." && exit 1)
	TOCHECK=$$(find fonts/ttf -type f 2>/dev/null); mkdir -p out/ out/fontspector; fontspector --profile googlefonts -l warn --full-lists --succinct --html out/fontspector/fontspector-report.html --ghmarkdown out/fontspector/fontspector-report.md --badges out/badges $$TOCHECK  || echo '::warning file=sources/build.sh,title=fontspector failures::The fontspector QA check reported errors in your font. Please check the generated report.'

proof: venv build.stamp
	which diff3proof || (echo "diff3proof not found. Please install it with 'cargo binstall diffenator3'." && exit 1)
	TOCHECK=$$(find fonts/ttf -type f 2>/dev/null); . venv/bin/activate; mkdir -p out/ out/proof; diff3proof $$TOCHECK --output out/proof

clean:
	rm -rf venv build.stamp sources/out
	find . -name "*.pyc" -delete
