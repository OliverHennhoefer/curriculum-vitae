# Curriculum vitae and cover letter

Configurable resume and cover letter. The same files work locally and on [Overleaf](https://www.overleaf.com/project). 

Example outputs: [curriculum-vitae.pdf](examples/curriculum-vitae.pdf) and [cover-letter.pdf](examples/cover-letter.pdf).

## Editable Files

- `curriculum-vitae.tex` - resume entrypoint.
- `cover-letter.tex` - cover-letter entrypoint.
- `sections/_personal.tex` - name, contact details, etc.
- `sections/*.tex` - configurable content sections.
- `application.cls` - shared layout and styling

In `curriculum-vitae.tex`, comment or uncomment sections to create an individual resume, professional CV, or academic CV.

## Overleaf

1. Down the the project (as `.zip`)
2. In Overleaf, choose **New Project -> Upload Project**.
3. In project settings, select:

   - **Compiler:** LuaLaTeX
   - **TeX Live:** 2025, when available, to match the CI build
   - **Main document:** `curriculum-vitae.tex` or `cover-letter.tex`

4. Edit `sections/_personal.tex` and relevant section files

## Local

Install a TeX distribution with LuaLaTeX, GNU Make, and Python 3. Poppler is also needed only for `make check`.

From the project root:

```sh
make                  # Build both PDFs
make curriculum-vitae # Build only the CV/resume
make cover-letter     # Build only the cover letter
make check            # Build and run PDF checks
make fonts            # Optional: install fonts locally
make clean            # Remove generated files
```

The PDFs are written to `build/`. Run `make fonts` once if the local output
falls back to Latin Modern Sans; the command installs Source Sans 3 and Roboto
for the current user and requires an internet connection. Normal compilation
uses LuaLaTeX and does not require the font installer.
