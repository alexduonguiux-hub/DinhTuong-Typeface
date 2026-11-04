help:
	@echo "###"
	@echo "# Build targets for Dinh Tuong"
	@echo "###"
	@echo
	@echo "  make build:    Builds the static fonts (sources/config-static.yaml, from sources/ufo) and the variable font"
	@echo "                 (sources/config.yaml, from sources/vf) with gftools builder into fonts/"
	@echo "  make vf:       Remakes sources/vf from sources/ufo (point-compatible masters), builds and checks the variable font"
	@echo "  make generate: Regenerates sources/ufo from the rule-based generators (sources/dinhtuong)"
	@echo "  make compare:  Checks the fontmake build against the generators' reference binaries"
	@echo "  make test:   Tests the fonts with fontspector (Google Fonts profile)"
	@echo "  make qa:     Font Bakery on fonts/ttf + fonts/otf (vs documentation/qa/fontbakery-accepted.txt) + guideline audit on the UFOs"
	@echo "  make proof:  Creates HTML proof documents in out/proof"
	@echo

build: build.stamp

venv: venv/touchfile

venv/touchfile: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt > venv-install.log 2>&1 || (python3 scripts/ci_log.py venv-install.log pip; exit 1)
	touch venv/touchfile

build.stamp: venv sources/config.yaml sources/config-static.yaml $(shell find sources/ufo sources/vf -type f)
	rm -rf fonts; . venv/bin/activate; (gftools builder sources/config-static.yaml && gftools builder sources/config.yaml) > build.log 2>&1 || (python3 scripts/ci_log.py build.log build; exit 1)
	touch build.stamp

# Variable font (Google Fonts onboarding): sources/vf are the masters of sources/ufo made point-compatible (exact
# splits), then the build must draw like the static fonts at 400 / 500 / 700 and interpolate steadily in between.
vf: venv venv-qa/touchfile
	. venv/bin/activate; python3 scripts/make_vf_sources.py && gftools builder sources/config.yaml > build-vf.log 2>&1 || (python3 scripts/ci_log.py build-vf.log build; exit 1)
	. venv-qa/bin/activate; python3 scripts/vf_vs_static.py && python3 scripts/vf_interp_check.py

generate:
	pip install -r requirements-generate.txt; sh sources/generate.sh

compare: build.stamp
	. venv/bin/activate; python3 scripts/compare_build.py sources/reference/fonts fonts

test: build.stamp
	which fontspector || (echo "fontspector not found. Please install it with 'cargo binstall fontspector'." && exit 1)
	TOCHECK=$$(find fonts/ttf -type f 2>/dev/null); mkdir -p out/ out/fontspector; fontspector --profile googlefonts -l warn --full-lists --succinct --html out/fontspector/fontspector-report.html --ghmarkdown out/fontspector/fontspector-report.md --badges out/badges $$TOCHECK  || echo '::warning file=sources/build.sh,title=fontspector failures::The fontspector QA check reported errors in your font. Please check the generated report.'

# Technical QA (Font Bakery). Checks the fonts already in fonts/ (no rebuild); fails on any result that is not
# listed in documentation/qa/fontbakery-accepted.txt. See .claude/skills/dinhtuong-tech-qa/SKILL.md.
venv-qa/touchfile: requirements-qa.txt
	test -d venv-qa || python3 -m venv venv-qa
	. venv-qa/bin/activate; pip install -Ur requirements-qa.txt
	touch venv-qa/touchfile

qa: venv-qa/touchfile
	. venv-qa/bin/activate; python3 scripts/qa_fontbakery.py
	. venv-qa/bin/activate; python3 scripts/qa_alignment.py sources/ufo/DinhTuong-Regular.ufo sources/ufo/DinhTuong-Medium.ufo sources/ufo/DinhTuong-Bold.ufo

proof: venv build.stamp
	which diff3proof || (echo "diff3proof not found. Please install it with 'cargo binstall diffenator3'." && exit 1)
	TOCHECK=$$(find fonts/ttf -type f 2>/dev/null); . venv/bin/activate; mkdir -p out/ out/proof; diff3proof $$TOCHECK --output out/proof

clean:
	rm -rf venv build.stamp sources/out
	find . -name "*.pyc" -delete
