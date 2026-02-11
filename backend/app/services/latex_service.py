"""LaTeX report generation service.

Generates publication-ready LaTeX documents from project data
including experiments, benchmarks, result tables, and research papers.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.lifecycle import (
    ResearchPaper, Experiment, BenchmarkResult, ResultTable, LatexReport,
    LIFECYCLE_STEP_NAMES,
)


class LatexService:
    """Service for generating LaTeX reports from project data."""

    TEMPLATES = {
        "ieee": {
            "documentclass": "\\documentclass[conference]{IEEEtran}",
            "packages": [
                "\\usepackage{cite}",
                "\\usepackage{amsmath,amssymb,amsfonts}",
                "\\usepackage{algorithmic}",
                "\\usepackage{graphicx}",
                "\\usepackage{textcomp}",
                "\\usepackage{xcolor}",
                "\\usepackage{booktabs}",
                "\\usepackage{hyperref}",
            ],
        },
        "acm": {
            "documentclass": "\\documentclass[sigconf]{acmart}",
            "packages": [
                "\\usepackage{booktabs}",
                "\\usepackage{graphicx}",
                "\\usepackage{hyperref}",
            ],
        },
        "neurips": {
            "documentclass": "\\documentclass{article}",
            "packages": [
                "\\usepackage[final]{neurips_2024}",
                "\\usepackage{booktabs}",
                "\\usepackage{graphicx}",
                "\\usepackage{hyperref}",
                "\\usepackage{amsmath}",
            ],
        },
        "custom": {
            "documentclass": "\\documentclass[12pt]{article}",
            "packages": [
                "\\usepackage[margin=1in]{geometry}",
                "\\usepackage{booktabs}",
                "\\usepackage{graphicx}",
                "\\usepackage{hyperref}",
                "\\usepackage{amsmath}",
                "\\usepackage{natbib}",
            ],
        },
    }

    @staticmethod
    def generate_full_report(db: Session, project: Project, template_type: str = "ieee") -> str:
        """Generate a complete LaTeX report from all project data."""
        template = LatexService.TEMPLATES.get(template_type, LatexService.TEMPLATES["custom"])

        # Gather all project data
        papers = db.query(ResearchPaper).filter(ResearchPaper.project_id == project.id).all()
        experiments = db.query(Experiment).filter(Experiment.project_id == project.id).all()
        benchmarks = db.query(BenchmarkResult).filter(BenchmarkResult.project_id == project.id).all()
        result_tables = db.query(ResultTable).filter(ResultTable.project_id == project.id).all()

        sections = []

        # Document header
        sections.append(template["documentclass"])
        sections.append("\n".join(template["packages"]))
        sections.append("")
        sections.append(f"\\title{{{LatexService._escape_latex(project.title)}}}")
        sections.append("\\author{AI Research Team}")
        sections.append("")
        sections.append("\\begin{document}")
        sections.append("\\maketitle")
        sections.append("")

        # Abstract
        sections.append("\\begin{abstract}")
        if project.description:
            sections.append(LatexService._escape_latex(project.description))
        else:
            sections.append("This paper presents the research findings and experimental results.")
        sections.append("\\end{abstract}")
        sections.append("")

        # Introduction
        sections.append("\\section{Introduction}")
        sections.append(f"This report documents the research project: \\textit{{{LatexService._escape_latex(project.title)}}}.")
        if project.domain:
            sections.append(f"The project focuses on the domain of {LatexService._escape_latex(project.domain)}.")
        sections.append("")

        # Literature Review (from research papers)
        if papers:
            sections.append("\\section{Literature Review}")
            for paper in papers:
                sections.append(f"\\subsection{{{LatexService._escape_latex(paper.title)}}}")
                if paper.authors:
                    sections.append(f"\\textit{{Authors: {LatexService._escape_latex(paper.authors)}}}")
                    sections.append("")
                if paper.summary:
                    sections.append(LatexService._escape_latex(paper.summary))
                    sections.append("")
                if paper.open_problems:
                    sections.append("\\textbf{Open Problems:}")
                    sections.append(LatexService._escape_latex(paper.open_problems))
                    sections.append("")

        # Methodology
        sections.append("\\section{Methodology}")
        baseline_exps = [e for e in experiments if e.experiment_type == "baseline"]
        if baseline_exps:
            sections.append("\\subsection{Baseline Experiments}")
            for exp in baseline_exps:
                sections.append(f"\\subsubsection{{{LatexService._escape_latex(exp.name)}}}")
                if exp.hypothesis:
                    sections.append(f"\\textbf{{Hypothesis:}} {LatexService._escape_latex(exp.hypothesis)}")
                    sections.append("")
                if exp.methodology:
                    sections.append(LatexService._escape_latex(exp.methodology))
                    sections.append("")

        reproduction_exps = [e for e in experiments if e.experiment_type == "reproduction"]
        if reproduction_exps:
            sections.append("\\subsection{Reproduction of Existing Solutions}")
            for exp in reproduction_exps:
                sections.append(f"\\subsubsection{{{LatexService._escape_latex(exp.name)}}}")
                if exp.methodology:
                    sections.append(LatexService._escape_latex(exp.methodology))
                    sections.append("")

        # Experiments
        sections.append("\\section{Experiments}")

        partial_exps = [e for e in experiments if e.experiment_type == "partial"]
        if partial_exps:
            sections.append("\\subsection{Preliminary Experiments}")
            for exp in partial_exps:
                sections.append(f"\\subsubsection{{{LatexService._escape_latex(exp.name)}}}")
                if exp.dataset:
                    sections.append(f"\\textbf{{Dataset:}} {LatexService._escape_latex(exp.dataset)}")
                    sections.append("")
                if exp.model_architecture:
                    sections.append(f"\\textbf{{Model:}} {LatexService._escape_latex(exp.model_architecture)}")
                    sections.append("")
                if exp.conclusion:
                    sections.append(LatexService._escape_latex(exp.conclusion))
                    sections.append("")

        scaled_exps = [e for e in experiments if e.experiment_type == "scaled"]
        if scaled_exps:
            sections.append("\\subsection{Scaled Experiments}")
            for exp in scaled_exps:
                sections.append(f"\\subsubsection{{{LatexService._escape_latex(exp.name)}}}")
                if exp.methodology:
                    sections.append(LatexService._escape_latex(exp.methodology))
                    sections.append("")
                if exp.conclusion:
                    sections.append(LatexService._escape_latex(exp.conclusion))
                    sections.append("")

        # Results
        sections.append("\\section{Results}")

        # Benchmark results
        if benchmarks:
            sections.append("\\subsection{Benchmark Evaluations}")
            for bench in benchmarks:
                sections.append(f"\\subsubsection{{{LatexService._escape_latex(bench.benchmark_name)}}}")
                if bench.dataset:
                    sections.append(f"Dataset: {LatexService._escape_latex(bench.dataset)}")
                if bench.model_name:
                    sections.append(f", Model: {LatexService._escape_latex(bench.model_name)}")
                sections.append("")
                if bench.metrics:
                    for metric_name, metric_val in bench.metrics.items():
                        sections.append(f"\\textbf{{{LatexService._escape_latex(metric_name)}:}} {metric_val}")
                    sections.append("")

        # Result tables
        if result_tables:
            sections.append("\\subsection{Result Tables}")
            for table in result_tables:
                sections.append(LatexService._generate_latex_table(table))
                sections.append("")

        # Discussion
        sections.append("\\section{Discussion}")
        completed_exps = [e for e in experiments if e.status == "completed" and e.conclusion]
        if completed_exps:
            for exp in completed_exps:
                sections.append(f"\\textbf{{{LatexService._escape_latex(exp.name)}:}} {LatexService._escape_latex(exp.conclusion)}")
                sections.append("")
        else:
            sections.append("Discussion of results and findings to be added.")
        sections.append("")

        # Conclusion
        sections.append("\\section{Conclusion}")
        sections.append(f"This report summarizes the research conducted for the project \\textit{{{LatexService._escape_latex(project.title)}}}.")
        sections.append("")

        # References
        if papers:
            sections.append("\\begin{thebibliography}{99}")
            for i, paper in enumerate(papers, 1):
                bib_entry = f"\\bibitem{{ref{i}}} "
                if paper.authors:
                    bib_entry += f"{LatexService._escape_latex(paper.authors)}, "
                bib_entry += f"``{LatexService._escape_latex(paper.title)},''"
                if paper.venue:
                    bib_entry += f" in \\textit{{{LatexService._escape_latex(paper.venue)}}}"
                if paper.year:
                    bib_entry += f", {paper.year}"
                bib_entry += "."
                sections.append(bib_entry)
            sections.append("\\end{thebibliography}")
        sections.append("")

        sections.append("\\end{document}")

        return "\n".join(sections)

    @staticmethod
    def _generate_latex_table(table: ResultTable) -> str:
        """Generate a LaTeX table from ResultTable data."""
        if not table.table_data:
            return f"% Table: {table.title} - No data available"

        headers = table.table_data.get("headers", [])
        rows = table.table_data.get("rows", [])

        if not headers:
            return f"% Table: {table.title} - No headers"

        num_cols = len(headers)
        col_spec = "l" + "c" * (num_cols - 1)

        lines = []
        lines.append(f"\\begin{{table}}[htbp]")
        lines.append(f"\\caption{{{LatexService._escape_latex(table.title)}}}")
        lines.append(f"\\centering")
        lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
        lines.append("\\toprule")

        # Headers
        header_line = " & ".join(
            f"\\textbf{{{LatexService._escape_latex(str(h))}}}" for h in headers
        )
        lines.append(f"{header_line} \\\\")
        lines.append("\\midrule")

        # Rows
        for row in rows:
            row_line = " & ".join(LatexService._escape_latex(str(cell)) for cell in row)
            lines.append(f"{row_line} \\\\")

        lines.append("\\bottomrule")
        lines.append("\\end{tabular}")
        lines.append("\\end{table}")

        return "\n".join(lines)

    @staticmethod
    def _escape_latex(text: str) -> str:
        """Escape special LaTeX characters."""
        if not text:
            return ""
        special_chars = {
            "&": "\\&",
            "%": "\\%",
            "$": "\\$",
            "#": "\\#",
            "_": "\\_",
            "{": "\\{",
            "}": "\\}",
            "~": "\\textasciitilde{}",
            "^": "\\textasciicircum{}",
        }
        for char, replacement in special_chars.items():
            text = text.replace(char, replacement)
        return text
