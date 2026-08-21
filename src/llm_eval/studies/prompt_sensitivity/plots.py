from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_accuracy_by_style(csv_path: Path, out: Path, style_order: list[str] | None = None) -> None:
    if not csv_path.exists():
        return
    df = pd.read_csv(csv_path)
    agg = df.groupby("prompt_style")["accuracy"].mean().reset_index()
    if style_order:
        agg["prompt_style"] = pd.Categorical(
            agg["prompt_style"], categories=style_order, ordered=True
        )
        agg = agg.sort_values("prompt_style")

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=agg, x="prompt_style", y="accuracy", ax=ax, color="#4c72b0")
    ax.set_xlabel("Prompt style")
    ax.set_ylabel("Accuracy")
    ax.set_title("Accuracy under prompt paraphrases")
    plt.xticks(rotation=35, ha="right")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_fragility_by_category(csv_path: Path, out: Path) -> None:
    if not csv_path.exists():
        return
    df = pd.read_csv(csv_path)
    agg = df.groupby("category")["mean_fragility"].mean().reset_index()
    agg = agg.sort_values("mean_fragility", ascending=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(agg["category"], agg["mean_fragility"], color="#c44e52")
    ax.set_xlabel("Mean fragility (1 − answer consistency)")
    ax.set_title("Prompt sensitivity by problem category")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_fragility_histogram(csv_path: Path, out: Path) -> None:
    if not csv_path.exists():
        return
    df = pd.read_csv(csv_path)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(df["fragility"], bins=15, color="#55a868", edgecolor="white")
    ax.set_xlabel("Fragility per problem")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of reasoning fragility")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_sensitivity_heatmap(csv_path: Path, out: Path, style_order: list[str] | None = None) -> None:
    if not csv_path.exists():
        return
    df = pd.read_csv(csv_path)
    if "model" in df.columns:
        models = df["model"].unique()
        if len(models) == 1:
            df = df[df["model"] == models[0]]

    style_cols = [
        c
        for c in df.columns
        if c not in ("model", "problem_id", "category")
    ]
    if style_order:
        style_cols = [c for c in style_order if c in style_cols]

    mat = df.set_index("problem_id")[style_cols]
    fig_h = max(6, len(mat) * 0.15)
    fig, ax = plt.subplots(figsize=(10, fig_h))
    sns.heatmap(
        mat.astype(float),
        cmap="RdYlGn",
        vmin=0,
        vmax=1,
        ax=ax,
        cbar_kws={"label": "Correct"},
        linewidths=0.3,
    )
    ax.set_title("Prompt Sensitivity Map (problem × style)")
    ax.set_xlabel("Prompt style")
    ax.set_ylabel("Problem")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_explanation_vs_consistency(csv_path: Path, out: Path) -> None:
    if not csv_path.exists():
        return
    df = pd.read_csv(csv_path)
    if df.empty:
        return

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(
        df["answer_consistency"],
        df["explanation_similarity"],
        alpha=0.7,
        c=df["fragility"],
        cmap="coolwarm",
    )
    ax.set_xlabel("Answer consistency across paraphrases")
    ax.set_ylabel("Explanation similarity (Jaccard)")
    ax.set_title("Answer vs explanation stability")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
