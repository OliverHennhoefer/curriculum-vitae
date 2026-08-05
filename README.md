# CV and Cover-Letter Templates

A LaTeX template for professional and academic CVs, resumes, and
cover letters. The documents share one class, layout, and data model.

## Preview

Download the generated example documents:

| Document | PDF |
| --- | --- |
| Professional CV | [cv.pdf](build/cv.pdf) |
| Short resume | [resume.pdf](build/resume.pdf) |
| Academic CV | [academic-cv.pdf](build/academic-cv.pdf) |
| Professional cover letter | [coverletter.pdf](build/coverletter.pdf) |
| Academic cover letter | [academic-coverletter.pdf](build/academic-coverletter.pdf) |

## Included documents

- `src/cv.tex` — detailed professional CV
- `src/resume.tex` — shorter industry-oriented resume
- `src/academic-cv.tex` — academic CV with research and teaching sections
- `src/coverletter.tex` — professional cover letter
- `src/academic-coverletter.tex` — academic cover letter

Generated PDFs are published in [`build/`](build/) after successful pushes to
the default branch.

## Requirements

- LuaLaTeX
- A TeX distribution containing the packages used by the class
- Python 3 for the validation script
- Poppler utilities for `make check`

The class uses Source Sans 3 and Roboto when available, and falls back to
Latin Modern Sans when they are not installed.

## Build

```sh
make                 # Build the general CV and cover letter
make profiles        # Build the resume and academic variants
make check           # Build all documents and run PDF checks
make USE_LATEXMK=1  # Force latexmk
make USE_LATEXMK=0  # Use the portable two-pass fallback
make clean
```

PDFs are written to `build/`. Auxiliary files are kept in
`build/<document>/`. The GitHub Actions workflow builds every profile, runs the
ATS-oriented checks, uploads the PDFs as an artifact, and refreshes the
canonical PDFs on the default branch.

## Automated builds

GitHub Actions provides a convenient build environment for contributors who do
not have a local TeX installation. Every push automatically compiles all
profiles, writes the generated PDFs to `build/`, and runs the validation checks.
Pull requests receive the generated PDFs as an artifact. Successful pushes to
the default branch also commit the refreshed canonical PDFs to `build/`.

## Customization

1. Edit [`data/personal.tex`](data/personal.tex) and replace its placeholders.
2. Update the relevant files in [`cv/`](cv/).
3. Choose the appropriate entrypoint in [`src/`](src/).
4. Replace all sample recipient, organization, role, and date values before
   sending an application.

The entrypoints use A4 paper by default. Select the `letterpaper` class option
when preparing a US Letter document.

## Content structure

The general profiles cover experience, education, skills, projects, and
certifications. The academic profiles additionally support research interests,
publications, presentations, teaching, honors, service, and references.

## License and attribution

The project is distributed under the LaTeX Project Public License, version
1.3c. The shared class contains portions derived from
[Awesome-CV](https://github.com/posquit0/Awesome-CV), also distributed under
LPPL 1.3c. See [`LICENSE`](LICENSE) for the license text.
