#!/bin/sh

TOKEN=$(scripts/login.sh)
curl "http://localhost:5000/sample?assay=cosmx&tissue=LMet2" -X POST -s \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{ "assay": "cosmx", "tissue": "LMet2", "area": 19.8163, "assigned_transcripts": 89.0296, "cell_count": 37000,
    "cell_over25_count": 36568, "complexity": 0.805, "false_discovery_rate": 0.0025, "median_counts": 99,
    "median_genes": 99, "reference_correlation": 0.0378, "sparsity": 0.3446, "volume": 572.2,
    "x_transcript_count": 13747088, "y_transcript_count": 13747088, "transcripts_per_area": 693726.281,
    "transcripts_per_feature": 14319.8833 }'
