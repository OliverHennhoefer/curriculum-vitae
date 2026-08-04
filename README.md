# Curriculum Vitae

This repository contains a single, detailed CV built with the [Awesome CV](https://github.com/posquit0/Awesome-CV) LaTeX class.

## Structure

- `cv.tex` is the document entry point.
- `cv/` contains the CV sections, split into small editable files.
- The documents are intentionally photo-free; no image assets are required.
- `awesome-cv.cls` provides the layout and styling; its single `awesome-color` definition controls the accent color.
- `coverletter.tex` is an optional companion document using the same class.
- `Makefile` provides repeatable build and clean commands.

The document fields contain concise placeholders. Replace them before using or publishing the generated document.

## CV vs. resume

A CV is generally the more comprehensive record of a person's education, experience, skills, publications, and other work. A resume is usually a shorter, targeted summary for a specific job. In Europe, including Germany, “CV” is also commonly used for the standard job-application document, so the terms often overlap in practice.

The upstream template included both examples. This repository keeps the fuller `cv` variant as its single canonical document; the alternate `resume` sample was not needed to build it.

## Build

Install a full TeX distribution with `lualatex`, then run:

```sh
make
```

This creates `cv.pdf`. To build the optional cover letter, run `make coverletter`. Generated PDFs and TeX build artifacts are ignored by Git.
