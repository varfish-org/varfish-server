import gzip


def open_file(path, mode):
    """Open gzip or normal file."""
    if hasattr(path, "open"):
        try:
            return gzip.open(path, "rt")
        except gzip.BadGzipFile:
            return path.open(mode="rt")
    elif path.endswith(".gz"):
        return gzip.open(path, mode)
    else:
        return open(path, mode)


def tsv_reader(path):
    """Read any info file in TSV format with first line as header.

    :param path: Path to the info file.
    :return: Yield dict with column names as keys and the values as values
    """
    if hasattr(path, "open"):
        try:
            inputf = gzip.open(path, "rt")
        except gzip.BadGzipFile:
            inputf = path.open(mode="rt")
    elif path.endswith(".gz"):
        inputf = gzip.open(path, "rt")
    else:
        inputf = open(path, "rt")
    with inputf as fh:
        keys = next(fh).rstrip("\n").split("\t")
        for line in fh:
            if not line.startswith("#"):
                yield dict(zip(keys, line.rstrip("\n").split("\t")))
