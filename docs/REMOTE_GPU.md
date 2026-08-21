# Running evaluations on a Slurm GPU cluster

These are generic instructions for running the evaluations on a Slurm-managed
GPU cluster. Substitute your own values throughout:

| Placeholder | Meaning |
|-------------|---------|
| `$GPU_USER` | your username on the cluster |
| `$GPU_HOST` | the cluster login hostname |
| `$PROJECT`  | path to this project on the cluster (e.g. `~/llm-eval`) |

Set them once in your shell so the commands below can be pasted as-is:

```bash
export GPU_USER=your-username
export GPU_HOST=cluster.example.edu
export PROJECT=~/llm-eval
```

**Important:** many clusters forbid long GPU jobs on the login node. Submit
work with `sbatch` or `srun`, and check your site's own Slurm documentation for
the correct partition name.

---

## First login

Once logged in via SSH, run these **on the cluster** (in order):

```bash
# 1) See cluster status and your jobs
sinfo
squeue -u $GPU_USER

# 2) Check if GPUs are on compute nodes (login node may have no GPU)
nvidia-smi

# 3) Go home and confirm project exists (or upload it — see Part A)
ls $PROJECT || echo "Need to rsync or git clone the project first"
```

If `nvidia-smi` fails on login, that is normal — GPUs are allocated when Slurm starts your job.

---

## Part A — From your workstation (first time)

### 1. Connect

```bash
ssh $GPU_USER@$GPU_HOST
```

### 2. Copy the project

```bash
rsync -avz --progress \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude 'studies/*/results' \
  --exclude 'studies/*/analysis/figures' \
  ./ \
  $GPU_USER@$GPU_HOST:$PROJECT/
```

### 3. Copy results back

```bash
rsync -avz --progress \
  $GPU_USER@$GPU_HOST:$PROJECT/studies/prompt_sensitivity/results/ \
  ./studies/prompt_sensitivity/results/
```

---

## Part B — Setup on the cluster (once)

```bash
ssh $GPU_USER@$GPU_HOST
cd $PROJECT

python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .

# If CUDA is missing, ask your admin; often:
# module avail
# module load cuda
# module load python/3.10

python -c "import torch; print('cuda:', torch.cuda.is_available())"
```

Edit `config.yaml`:

```yaml
inference:
  device: cuda
  dtype: bfloat16
```

Hugging Face (for Qwen/Llama):

```bash
source .venv/bin/activate
huggingface-cli login
```

Edit model names in `studies/prompt_sensitivity/config.yaml` (see below).

---

## Part C — Run with Slurm (recommended)

### 1. Check queue and partitions

```bash
sinfo
squeue
```

Read your site's documentation for the correct **partition** name (e.g. `gpu`, `a100`). Add to the script if required:

```bash
#SBATCH --partition=gpu
```

### 2. Smoke test (8 prompts, one GPU)

Edit `slurm/run_eval.slurm`:

- `STUDY=prompt_sensitivity`
- `MODEL=qwen2.5-7b`
- `LIMIT=8`

Submit:

```bash
cd $PROJECT
mkdir -p slurm/logs
sbatch slurm/run_eval.slurm
```

Watch job:

```bash
squeue -u $GPU_USER
# When done:
ls slurm/logs/
tail -f slurm/logs/eval-<JOBID>.out
```

### 3. Full run

Set `LIMIT=` (empty) in `run_eval.slurm`, submit again.  
Run **one model per job** (polite on shared clusters):

```bash
# Job 1
sbatch slurm/run_eval.slurm   # MODEL=qwen2.5-7b

# Job 2 — edit MODEL=llama-3.1-8b first, then:
sbatch slurm/run_eval.slurm
```

### 4. Interactive GPU session (debugging)

If your cluster allows it:

```bash
srun --gres=gpu:1 --cpus-per-task=4 --mem=32G --time=01:00:00 --pty bash
source $PROJECT/.venv/bin/activate
cd $PROJECT
nvidia-smi
python scripts/run_evaluation.py --study prompt_sensitivity --limit 2 --models qwen2.5-7b
```

Cancel a job: `scancel <JOBID>`

---

## Part D — Without Slurm (only if admin allows)

Some sites forbid GPU use outside Slurm. If direct GPU access is allowed on a node:

```bash
export CUDA_VISIBLE_DEVICES=0
python scripts/run_evaluation.py --study prompt_sensitivity --limit 8
```

Prefer Slurm when the banner says to use it.

---

## Recommended models (one A100 per job)

```yaml
# studies/prompt_sensitivity/config.yaml
models:
  behavioral:
    - name: qwen2.5-7b
      hf_id: Qwen/Qwen2.5-7B-Instruct
      max_new_tokens: 512
    - name: llama-3.1-8b
      hf_id: meta-llama/Llama-3.1-8B-Instruct
      max_new_tokens: 512
```

---

## Etiquette on shared Slurm clusters

1. Request **1 GPU** (`--gres=gpu:1`) unless you need more.
2. Set a realistic `--time` (e.g. `08:00:00`).
3. Do not submit dozens of jobs at once without checking local policy.
4. Use `squeue` to see your queue position.

---

## Troubleshooting

| Issue | Action |
|-------|--------|
| `sbatch: command not found` | Load slurm module or use login node that has Slurm |
| Job pending (`PD`) forever | `squeue`; cluster busy — wait or ask admin |
| `CUDA out of memory` | Smaller model or lower `max_new_tokens` |
| Job fails immediately | `cat slurm/logs/eval-*.err` |
| Partition invalid | Check your site's docs; add `#SBATCH --partition=...` |
