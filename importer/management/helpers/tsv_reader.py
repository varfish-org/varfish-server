import gzip


def tsv_reader(path):
    """Read any info file in TSV format with first line as header.

    :param path: Path to the info file.
    :return: Yield dict with column names as keys and the values as values
    """
    if path.endswith(".gz"):
        inputf = gzip.open(path, "rt")
    else:
        inputf = open(path, "rt")
    with inputf as fh:
        keys = next(fh).rstrip("\n").split("\t")
        for line in fh:
            yield dict(zip(keys, line.rstrip("\n").split("\t")))
