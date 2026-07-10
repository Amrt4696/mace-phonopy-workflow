#!/usr/bin/env bash
# Downloads the pretrained MACE potential used in this repo's real (non-toy)
# examples. Fill in MODEL_URL once the model is uploaded to Zenodo/HuggingFace
# (a Zenodo DOI link or an HF `hf_hub_download` resolve URL both work with
# plain curl/wget).
#
# TODO: replace this placeholder with your actual model's download link.
set -euo pipefail

MODEL_URL="https://TODO-add-your-zenodo-or-huggingface-link/model.model"
OUT="$(dirname "$0")/bridgmanite_allgpa_smalllight_v1_compiled.model"

if [ "$MODEL_URL" = "https://TODO-add-your-zenodo-or-huggingface-link/model.model" ]; then
    echo "MODEL_URL is still a placeholder. Edit models/download_model.sh and set" >&2
    echo "it to your Zenodo/HuggingFace download link, then re-run this script." >&2
    exit 1
fi

echo "Downloading model to $OUT ..."
curl -L "$MODEL_URL" -o "$OUT"
echo "Done."
