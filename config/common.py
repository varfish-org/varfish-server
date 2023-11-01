import pydantic


class InternalStorageConfig(pydantic.BaseModel):
    """Configures access to the internal S3 storage"""

    #: hostname to connect to
    host: str
    #: port to connect to
    port: int
    #: access key to use
    access_key: str
    #: secret key to use
    secret_key: str
    #: bucket to use
    bucket: str = "varfish-server"
    #: whether or not to use HTTPS
    use_https: bool = False


class PrefilterConfig(pydantic.BaseModel):
    """Prefilter configuration on seqvar import."""

    #: maximal population allele frequency
    max_freq: float
    #: maximal distnace to exon
    max_exon_dist: int
    #: output path, not used in configuration
    prefilter_path: str | None = None
