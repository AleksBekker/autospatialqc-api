from typing import List, Optional

import pydantic


class Sample(pydantic.BaseModel):
    """Represents a sample."""

    id: Optional[int] = None

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

    @classmethod
    def data_fields(cls) -> List[str]:
        """Gets the list of the names of the most important data fields of a Sample."""

        return [
            "assay",
            "tissue",
            "area",
            "assigned_transcripts",
            "cell_count",
            "cell_over25_count",
            "complexity",
            "false_discovery_rate",
            "median_counts",
            "median_genes",
            "reference_correlation",
            "sparsity",
            "volume",
            "x_transcript_count",
            "y_transcript_count",
            "transcripts_per_area",
            "transcripts_per_feature",
        ]
