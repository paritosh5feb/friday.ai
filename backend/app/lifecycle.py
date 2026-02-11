LIFECYCLE_TEMPLATE = [
    {
        "stage_number": 1,
        "title": "Problem Statement Research",
        "guidance": (
            "Download and review papers (for example from Mendeley), summarize insights, "
            "identify open problem statements, and iterate via review -> proposal -> update cycles."
        ),
    },
    {
        "stage_number": 2,
        "title": "Establish Baseline Experiment",
        "guidance": "Design and run baseline experiments to validate the hypothesis (SEH).",
    },
    {
        "stage_number": 3,
        "title": "Reproduce Current Solutions",
        "guidance": "Reproduce existing approaches to verify implementation correctness and context.",
    },
    {
        "stage_number": 4,
        "title": "Run Smallest Partial Experiment",
        "guidance": "Execute minimal-scope experiments that test core assumptions quickly.",
    },
    {
        "stage_number": 5,
        "title": "Run Benchmark Evaluations",
        "guidance": "Benchmark models/approaches against target datasets and metrics.",
    },
    {
        "stage_number": 6,
        "title": "Create Result Tables",
        "guidance": "Compile outputs of small experiments and benchmark evaluations in structured tables.",
    },
    {
        "stage_number": 7,
        "title": "Scale Experiments",
        "guidance": "Scale successful small experiments when metrics and sanity checks are positive.",
    },
    {
        "stage_number": 8,
        "title": "Final Evaluation and Reporting",
        "guidance": (
            "Perform final evaluation, collation, discussion, and generate a LaTeX-ready report artifact."
        ),
    },
]

LIFECYCLE_STATUSES = ["pending", "in_progress", "completed", "blocked"]
