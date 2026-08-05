.PHONY: all curriculum-vitae cover-letter fonts check clean

LATEX ?= lualatex
LATEXMK ?= latexmk
USE_LATEXMK ?= auto
PYTHON ?= python
BUILD_DIR ?= build
FONT_INSTALLER ?= tools/install_fonts.py

# Prefer latexmk where its Perl runtime is available; keep the direct
# two-pass recipe usable on minimal Windows TeX installations.
ifeq ($(USE_LATEXMK),auto)
ifeq ($(OS),Windows_NT)
LATEXMK_READY := $(shell where perl >NUL 2>NUL && echo 1 || echo 0)
else
LATEXMK_READY := $(shell command -v perl >/dev/null 2>&1 && echo 1 || echo 0)
endif
ifeq ($(LATEXMK_READY),1)
USE_LATEXMK := 1
else
USE_LATEXMK := 0
endif
endif

DOCUMENTS := curriculum-vitae cover-letter
COMMON_SOURCES := application.cls $(wildcard sections/*.tex)
LATEX_FLAGS ?= -interaction=nonstopmode -halt-on-error -file-line-error
LATEXMK_FLAGS ?= -lualatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=$(BUILD_DIR)

ifeq ($(OS),Windows_NT)
MOVE_PDF = powershell.exe -NoProfile -Command "Move-Item -LiteralPath '$(BUILD_DIR)/$*/$*.pdf' -Destination '$@' -Force"
CLEAN_BUILD = powershell.exe -NoProfile -Command "if (Test-Path -LiteralPath '$(BUILD_DIR)') { Remove-Item -LiteralPath '$(BUILD_DIR)' -Recurse -Force }"
CLEAN_ROOT_AUX = powershell.exe -NoProfile -Command "Get-ChildItem -Path *.aux,*.log,*.out,*.fls,*.fdb_latexmk,*.synctex.gz -File -ErrorAction SilentlyContinue | Remove-Item -Force"
else
MOVE_PDF = mv -f "$(BUILD_DIR)/$*/$*.pdf" "$@"
CLEAN_BUILD = rm -rf "$(BUILD_DIR)"
CLEAN_ROOT_AUX = rm -f *.aux *.log *.out *.fls *.fdb_latexmk *.synctex.gz
endif

all: $(DOCUMENTS)

curriculum-vitae: $(BUILD_DIR)/curriculum-vitae.pdf

cover-letter: $(BUILD_DIR)/cover-letter.pdf

fonts:
	$(PYTHON) $(FONT_INSTALLER)

ifeq ($(USE_LATEXMK),1)
$(BUILD_DIR)/%.pdf: %.tex $(COMMON_SOURCES) | $(BUILD_DIR)
	-mkdir "$(BUILD_DIR)/$*"
	$(LATEXMK) $(LATEXMK_FLAGS) -auxdir=$(BUILD_DIR)/$* -jobname=$* $<
else
$(BUILD_DIR)/%.pdf: %.tex $(COMMON_SOURCES) | $(BUILD_DIR)
	-mkdir "$(BUILD_DIR)/$*"
	$(LATEX) $(LATEX_FLAGS) -output-directory=$(BUILD_DIR)/$* -jobname=$* $<
	$(LATEX) $(LATEX_FLAGS) -output-directory=$(BUILD_DIR)/$* -jobname=$* $<
	$(MOVE_PDF)
endif

$(BUILD_DIR):
	-mkdir $(BUILD_DIR)

check: all
	$(PYTHON) tools/check_ats.py $(BUILD_DIR)

clean:
	-$(CLEAN_BUILD)
	-$(CLEAN_ROOT_AUX)
