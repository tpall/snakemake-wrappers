__author__ = "Johannes Köster, Julian de Ruiter"
__copyright__ = "Copyright 2016, Johannes Köster and Julian de Ruiter"
__email__ = "koester@jimmy.harvard.edu, julianderuiter@gmail.com"
__license__ = "MIT"


from os import path

from snakemake.shell import shell


# Extract arguments.
extra = snakemake.params.get("extra", "")

sorting = snakemake.params.get("sorting", "none")
sorting_order = snakemake.params.get("sorting_order", "coordinate")
sorting_extra = snakemake.params.get("sorting_extra", "")

log = snakemake.log_fmt_shell(stdout=False, stderr=True)

# Check inputs/arguments.
if not isinstance(snakemake.input.reads, str) and len(snakemake.input.reads) not in {
    1,
    2,
}:
    raise ValueError("input must have 1 (single-end) or " "2 (paired-end) elements")

if sorting_order not in {"coordinate", "queryname"}:
    raise ValueError("Unexpected value for sorting_order ({})".format(sorting_order))

# Determine which pipe command to use for converting to bam or sorting.
if sorting == "none":

    # Simply convert to bam using samtools view.
    pipe_cmd = "samtools view -Sbh -o {snakemake.output[0]} -"

elif sorting == "samtools":

    # Sort alignments using samtools sort.
    pipe_cmd = "samtools sort {sorting_extra} -o {snakemake.output[0]} -"

    # Add name flag if needed.
    if sorting_order == "queryname":
        sorting_extra += " -n"

    prefix = path.splitext(snakemake.output[0])[0]
    sorting_extra += " -T " + prefix + ".tmp"

elif sorting == "picard":

    # sorting alignments using picard SortSam.
    pipe_cmd = (
        "picard SortSam {sorting_extra} INPUT=/dev/stdin"
        " OUTPUT={snakemake.output[0]} SORT_ORDER={sorting_order}"
    )

else:
    raise ValueError("Unexpected value for params.sorting ({})".format(sorting))

shell(
    "(bwa mem"
    " -t {snakemake.threads}"
    " {extra}"
    " {snakemake.params.db_prefix}"
    " {snakemake.input.reads}"
    " | " + pipe_cmd + ") {log}"
)
