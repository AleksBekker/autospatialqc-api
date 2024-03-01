#!/bin/sh

jq 'map({
  "assay": (.["Sample"] | split(" ")[0]),
  "tissue": (.["Sample"] | split(" ")[1]),
	"area": .["Area"],
	"assigned_transcripts": .["AssignedTranscripts"],
	"cell_count": .["NoOfCells"],
	"cell_over25_count": .["NoOfCellsOver25"],
	"complexity": .["Complexity"],
	"false_discovery_rate": .["FDR"],
	"median_counts": .["MedianCounts"],
	"median_genes": .["MedianGenes"],
	"reference_correlation": .["Wu.et.al..PCC"],
	"sparsity": .["Sparsity"],
	"volume": .["Volume"],
	"x_transcript_count": .["Transcripts.x"],
	"y_transcript_count": .["Transcripts.y"],
	"transcripts_per_area": .["TranscriptsOverArea"],
	"transcripts_per_feature": .["TranscriptsOverFeatures"]
})' $1
