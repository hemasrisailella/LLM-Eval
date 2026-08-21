from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_flip_rates_by_condition(flip_csv: Path, out: Path) -> None:
    if not flip_csv.exists():
        return
    df = pd.read_csv(flip_csv)
    agg = df.groupby("prompt_id")["flip_rate"].mean().reset_index()
    order = ["C0", "C1", "C2", "C3", "C4"]
    agg["prompt_id"] = pd.Categorical(agg["prompt_id"], categories=order, ordered=True)
    agg = agg.sort_values("prompt_id")

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=agg, x="prompt_id", y="flip_rate", ax=ax, color="#4c72b0")
    ax.set_xlabel("Prompt condition")
    ax.set_ylabel("Flip rate (among neutral-correct items)")
    ax.set_title("Sycophancy: correct → user-wrong flips by condition")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_wrong_agreement_by_model(flip_csv: Path, out: Path) -> None:
    if not flip_csv.exists():
        return
    df = pd.read_csv(flip_csv)
    pressured = df[df["prompt_id"] != "C0"]
    if pressured.empty:
        return
    agg = pressured.groupby("model")["wrong_agreement_rate"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=agg, x="model", y="wrong_agreement_rate", ax=ax, color="#c44e52")
    ax.set_xlabel("Model")
    ax.set_ylabel("Wrong-agreement rate (non-neutral conditions)")
    ax.set_title("Agreement with user's wrong answer under pressure")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
