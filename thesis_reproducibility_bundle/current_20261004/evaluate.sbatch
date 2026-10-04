#!/bin/bash
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=evaluation_%j.out
# Example only: select measured memory for the domain/workers; FO uses96GiB.
set -euo pipefail
: "${ASNET_REPO:?Set the clone path}"
: "${ASNET_PYTHON:?Set Python inside the installed environment}"
"$ASNET_PYTHON" "$ASNET_REPO/thesis_reproducibility_bundle/current_20261004/evaluate_checkpoint.py" --repo "$ASNET_REPO" "$@" --execute
