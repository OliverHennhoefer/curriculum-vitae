#!/usr/bin/env python3
"""Prepare a realistic, throw-away source tree for the CI example PDFs."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from textwrap import dedent


DEMO_PERSONAL = r"""
% CI-only demo data. The editable template remains intentionally generic.

\newcommand*{\cvfirstname}{John}
\newcommand*{\cvfamilyname}{Doe}
\newcommand*{\cvfullname}{\cvfirstname\space\cvfamilyname}
\newcommand*{\cvlocation}{Berlin, Germany}

\name{\cvfirstname}{\cvfamilyname}
\address{\cvlocation}
\mobile{+49 30 555 0123}
\email{john.doe@example.com}
\homepage{https://example.com/john-doe}
\github{john-doe}
\linkedin{john-doe}
"""

DEMO_EXPERIENCE = r"""
% CI-only demo content used to make the generated example look realistic.
% Replace this file with your own experience when customizing the template.
\cvsection{Experience}

\begin{cventries}

  \cventry
    {Senior DevOps Engineer}
    {Northstar Systems}
    {Berlin, Germany}
    {2022--Present}
    [
      \begin{cvitems}
        \item {Lorem ipsum dolor sit amet, consectetur adipiscing elit; reduced release lead time by 45\% across 30 production services.}
        \item {Designed a Kubernetes and Terraform platform with automated delivery, observability, and self-service environments.}
      \end{cvitems}
    ]

  % Demonstrates an entry with no optional description or bullet points.
  \cventry
    {Technical Advisor}
    {Independent Consultancy}
    {Remote}
    {2021--2022}

  % Demonstrates one organization with two roles and their own bullets.
  \begin{cvmultirole}{Acme Digital}{Hamburg, Germany}
    \cvrole
      {Senior Platform Engineer}
      {2019--2022}
      [
        \begin{cvitems}
          \item {Led platform reliability and delivery automation.}
        \end{cvitems}
      ]
    \cvrole
      {Platform Engineer}
      {2016--2019}
      [
        \begin{cvitems}
          \item {Built shared infrastructure and developer tooling.}
        \end{cvitems}
      ]
  \end{cvmultirole}

\end{cventries}
"""

DEMO_EDUCATION = r"""
\cvsection{Education}

\begin{cventries}

  \cventry
    {M.Sc. Computer Science}
    {Example University}
    {Berlin, Germany}
    {2017--2019}
    [
      \begin{cvitems}
        \item {Thesis: resilient service orchestration for distributed systems.}
      \end{cvitems}
    ]

\end{cventries}
"""

DEMO_SKILLS = r"""
\cvsection{Skills}

\begin{cvskills}

  \cvskill
    {Cloud}
    {Kubernetes, Terraform, AWS, Azure, Docker, Linux}

  \cvskill
    {Engineering}
    {CI/CD, observability, incident response, platform architecture}

  \cvskill
    {Languages}
    {Python, Go, Bash, SQL; German and English}

\end{cvskills}
"""

DEMO_PROJECTS = r"""
\cvsection{Projects}

\begin{cventries}

  \cventry
    {Lead Developer}
    {Open Source Delivery Platform}
    {github.com/john-doe/delivery-platform}
    {2023--Present}
    [
      \begin{cvitems}
        \item {Lorem ipsum dolor sit amet, consectetur adipiscing elit; built an open-source reference platform with preview environments and documented runbooks.}
      \end{cvitems}
    ]

\end{cventries}
"""

DEMO_CERTIFICATIONS = r"""
\cvsection{Certifications}

\begin{cvhonors}

  \cvhonor
    {Certified Kubernetes Administrator}
    {Cloud Native Computing Foundation}
    {CKA-2024-JD}
    {2024}

  \cvhonor
    {AWS Solutions Architect -- Associate}
    {Amazon Web Services}
    {AWS-2021-JD}
    {2021}

\end{cvhonors}
"""

DEMO_FILES = {
    "sections/_personal.tex": DEMO_PERSONAL,
    "sections/experience.tex": DEMO_EXPERIENCE,
    "sections/education.tex": DEMO_EDUCATION,
    "sections/skills.tex": DEMO_SKILLS,
    "sections/projects.tex": DEMO_PROJECTS,
    "sections/certifications.tex": DEMO_CERTIFICATIONS,
}


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(dedent(content).lstrip())


def replace_once(path: Path, old: str, new: str) -> None:
    content = path.read_text(encoding="utf-8")
    occurrences = content.count(old)
    if occurrences != 1:
        raise RuntimeError(f"Expected one occurrence of {old!r} in {path}, found {occurrences}")
    write_text(path, content.replace(old, new))


def replace_line_once(path: Path, pattern: str, replacement: str) -> None:
    content = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, content, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"Expected one match for {pattern!r} in {path}, found {count}")
    write_text(path, updated)


def prepare_demo(source: Path, destination: Path) -> None:
    source = source.resolve()
    destination = destination.resolve()
    if destination == source:
        raise ValueError("The demo output directory must not be the repository directory")

    destination.mkdir(parents=True, exist_ok=True)
    for relative in ("application.cls", "curriculum-vitae.tex", "cover-letter.tex"):
        shutil.copy2(source / relative, destination / relative)
    shutil.copytree(source / "sections", destination / "sections", dirs_exist_ok=True)

    for relative, content in DEMO_FILES.items():
        write_text(destination / relative, content)

    replace_line_once(
        destination / "curriculum-vitae.tex",
        r"^\\position\{.*\}$",
        r"\\position{DevOps Engineer{\\enskip\\cdotp\\enskip}Software Architect}",
    )
    replace_line_once(
        destination / "cover-letter.tex",
        r"^\\position\{.*\}$",
        r"\\position{DevOps Engineer{\\enskip\\cdotp\\enskip}Software Architect}",
    )
    replace_once(
        destination / "cover-letter.tex",
        r"""\recipient
  {Recipient}
  {Organization\\Address}""",
        r"""\recipient
  {Hiring Team}
  {Acme Cloud GmbH\\Alexanderplatz 1\\10178 Berlin}""",
    )
    replace_once(
        destination / "cover-letter.tex",
        r"\lettertitle{Application for Target Role}",
        r"\lettertitle{Application for DevOps Engineer}",
    )
    replace_once(
        destination / "cover-letter.tex",
        r"""\begin{cvletter}
% Add a concise, target-specific opening, evidence of fit, and closing here.
% Use \lettersection{Section title} when a visually separated section is useful.
\end{cvletter}""",
        r"""\begin{cvletter}
Lorem ipsum dolor sit amet, consectetur adipiscing elit. I am excited to apply
for the DevOps Engineer position at Acme Cloud GmbH, where I can combine
platform engineering with a strong focus on reliable developer experiences.

\lettersection{Relevant experience}
In my current role, I design delivery platforms, improve observability, and
help teams turn complex operational requirements into repeatable workflows.
My work balances pragmatic automation with clear documentation and calm,
blameless incident response.

\lettersection{Motivation}
Acme Cloud's focus on dependable infrastructure and thoughtful engineering is a
strong match for my background. I would welcome the opportunity to contribute
to your platform roadmap and help make reliable delivery the easy path.
\end{cvletter}""",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="directory for the temporary demo source tree",
    )
    args = parser.parse_args()
    prepare_demo(Path(__file__).resolve().parents[1], args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
