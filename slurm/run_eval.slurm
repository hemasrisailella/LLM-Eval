#!/bin/bash
# Submit: sbatch slurm/run_eval.slurm
# Check:  squeue -u $USER
# Logs:   slurm/logs/eval-<jobid>.out

#SBATCH --job-name=llm-eval
#SBATCH --output=slurm/logs/eval-%j.out
#SBATCH --error=slurm/logs/eval-%j.err
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=08:00:00
# Add the partition your site requires (check its Slurm documentation):
# #SBATCH --partition=gpu

# --- Edit these before submitting ---
STUDY=prompt_sensitivity
MODEL=qwen2.5-7b
LIMIT=8           # smoke test: 8 | full run: leave empty (LIMIT=)
# ------------------------------------

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$HOME/llm-eval}"
mkdir -p slurm/logs

# Uncomment and adjust if your cluster uses environment modules:
# module load cuda
# module load python/3.10

source .venv/bin/activate

export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"

LIMIT_ARG=""
if [[ -n "${LIMIT}" ]]; then
  LIMIT_ARG="--limit ${LIMIT}"
fi

echo "Node: $(hostname)"
echo "Study: ${STUDY}  Model: ${MODEL}"
nvidia-smi || true

python scripts/build_dataset.py --study "${STUDY}"

python scripts/run_evaluation.py \
  --study "${STUDY}" \
  --models "${MODEL}" \
  ${LIMIT_ARG}

python scripts/compute_metrics.py --study "${STUDY}"
python scripts/plot_results.py --study "${STUDY}"

echo "Done. Results under studies/${STUDY}/results/"
