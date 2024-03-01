import pydantic


class Sample(pydantic.BaseModel):
    """Represents a sample."""

    id: int | None = None

    assay: str
    tissue: str

    area: float
    assigned_transcripts: float
    cell_count: int
    cell_over25_count: int
    complexity: float
    false_discovery_rate: float
    median_counts: float
    median_genes: float
    reference_correlation: float
    sparsity: float
    volume: float
    x_transcript_count: int
    y_transcript_count: int

    # Might be inferable
    transcripts_per_area: float
    transcripts_per_feature: float
