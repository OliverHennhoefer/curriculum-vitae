# CV and cover-letter template

LaTeX CV and cover-letter templates with a shared, photo-free class.

The repository is intentionally photo-free. All document variants use the same visual design and are built from shared personal information and section templates.

## Documents

- `src/cv.tex` — general, detailed professional CV.
- `src/resume.tex` — shorter industry-oriented resume.
- `src/coverletter.tex` — general professional cover letter.
- `src/academic-cv.tex` — optional academic CV with research, publications, teaching, and service.
- `src/academic-coverletter.tex` — optional academic application letter.

The entrypoints and shared class are kept under `src/`. Use Make or VSCode to
build them so the source search path is configured automatically.

Edit data/personal.tex first. Optional academic links are in data/academic-links.tex.

## Build

Requires LuaLaTeX and the fonts/packages used by the class. Source Sans 3 and Roboto are selected when installed; Latin Modern Sans is used only as a buildable fallback when they are unavailable. Make automatically uses latexmk when Perl is available and falls back to two direct LuaLaTeX passes on minimal Windows installations.

~~~sh
make                 # general CV and cover letter
make profiles        # resume and academic variants
make check           # build everything and run PDF text/image checks
make USE_LATEXMK=1  # force latexmk
make USE_LATEXMK=0  # force the portable two-pass fallback
make clean
~~~

Generated PDFs are written directly to `build/`; each document's auxiliary files
(`.aux`, `.log`, and related build state) are kept in `build/<document>/`.
In VSCode, LaTeX Workshop uses the same layout and two-pass recipe.

The entrypoints default to A4; change their `a4paper` class option to
`letterpaper` when preparing a US Letter application.

## Content conventions

The general professional profile should normally prioritize experience, education, skills, projects, and relevant certifications. Enable additional sections only when they strengthen the application.

The academic profile adds research interests, publications, presentations, teaching, honors, service, and references. Publications use \cvpublication in cv/publications.tex; separate peer-reviewed work, preprints, and other writing when needed.

For multiple roles within one organization, keep one normal \cventry and put
the existing cvsubentries environment inside its fifth argument:

~~~latex
% inside the cventry description
\begin{cvsubentries}
  \cvsubentry{}{Earlier role}{Earlier dates}{}
  \cvsubentry{}{Later role}{Later dates}{}
\end{cvsubentries}
~~~

Replace all placeholders before sending an application. Keep target-specific recipient details and letter text in the relevant cover-letter entrypoint or a private copy of it.

## ATS scope

The PDFs retain the established visual design while keeping important content as selectable text, retaining readable link labels, providing PDF metadata, and adding automated extraction checks. This improves compatibility with ATS parsers but cannot guarantee identical behavior across proprietary systems.
