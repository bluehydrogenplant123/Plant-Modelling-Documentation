from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "images" / "sep799"


TITLE_SIZE = 24
TEXT_SIZE = 13
SMALL_TEXT_SIZE = 11

LINE_DARK = "#4b4b63"
BLUE_EDGE = "#2c6a93"
BLUE_FILL = "#dceaf5"
GREEN_EDGE = "#2f855a"
GREEN_FILL = "#e3f3ea"
GOLD_EDGE = "#a07a18"
GOLD_FILL = "#fff4cf"
ROSE_EDGE = "#b55c5c"
ROSE_FILL = "#fde7e4"
LANE_FILL = "#f6f7fb"
LANE_EDGE = "#c9ceda"


def add_round_box(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    *,
    fc: str,
    ec: str,
    fontsize: int = TEXT_SIZE,
    lw: float = 2.5,
    radius: float = 0.12,
    weight: str = "regular",
):
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.02,rounding_size={radius}",
        linewidth=lw,
        edgecolor=ec,
        facecolor=fc,
        joinstyle="round",
    )
    ax.add_patch(box)
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        family="DejaVu Sans",
        color="#222222",
        weight=weight,
        wrap=True,
    )
    return box


def add_arrow(
    ax,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = LINE_DARK,
    lw: float = 2.4,
    style: str = "-|>",
    mutation_scale: int = 24,
    connectionstyle: str = "arc3",
):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle=style,
        mutation_scale=mutation_scale,
        linewidth=lw,
        color=color,
        connectionstyle=connectionstyle,
        shrinkA=0,
        shrinkB=0,
    )
    ax.add_patch(arrow)
    return arrow


def compat_architecture_figure():
    fig, ax = plt.subplots(figsize=(16, 7.8), dpi=220)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")

    ax.text(
        8,
        8.6,
        "Compatibility Architecture Overview",
        ha="center",
        va="center",
        fontsize=TITLE_SIZE,
        weight="bold",
        family="DejaVu Sans",
    )

    top = add_round_box(
        ax,
        5.65,
        6.65,
        4.7,
        1.25,
        "Compatibility Control Layer",
        fc=GOLD_FILL,
        ec=GOLD_EDGE,
        fontsize=15,
        weight="medium",
    )

    boxes = [
        (
            0.7,
            3.55,
            3.0,
            1.7,
            "Versioned Schema Migration\n\nschemaVersion / snapshot version\nschemaMigrations.ts",
            BLUE_FILL,
            BLUE_EDGE,
        ),
        (
            4.3,
            3.55,
            3.0,
            1.7,
            "Runtime Library Check\n\ndiagramCompatibility.ts\nstale vars / model versions",
            GREEN_FILL,
            GREEN_EDGE,
        ),
        (
            7.9,
            3.55,
            3.0,
            1.7,
            "Compatibility Records\n\nSCHEMA_SNAPSHOT.md\nSCHEMA_HISTORY.md",
            GOLD_FILL,
            GOLD_EDGE,
        ),
        (
            11.5,
            3.55,
            3.0,
            1.7,
            "Backup-first Recovery\n\n_oldversion_x_y_z copy\nupgrade only after backup",
            ROSE_FILL,
            ROSE_EDGE,
        ),
    ]

    for x, y, w, h, label, fc, ec in boxes:
        add_round_box(ax, x, y, w, h, label, fc=fc, ec=ec, fontsize=SMALL_TEXT_SIZE)

    top_bottom = (5.65 + 4.7 / 2, 6.65)
    targets = [
        (0.7 + 3.0 / 2, 3.55 + 1.7),
        (4.3 + 3.0 / 2, 3.55 + 1.7),
        (7.9 + 3.0 / 2, 3.55 + 1.7),
        (11.5 + 3.0 / 2, 3.55 + 1.7),
    ]
    for target in targets:
        add_arrow(ax, top_bottom, target, color=LINE_DARK, lw=2.2)

    add_round_box(
        ax,
        3.15,
        0.95,
        9.7,
        1.0,
        "Saved diagrams stay compatible only when persisted schema, live PostgreSQL library,\n"
        "decision records, and backup-safe upgrade flow are handled together.",
        fc="#ffffff",
        ec="#d6d9e4",
        fontsize=11,
        lw=1.8,
        radius=0.08,
    )

    fig.tight_layout()
    path = OUT_DIR / "sep799_compatibility_architecture_overview.png"
    fig.savefig(path, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return path


def compat_swimlane_figure():
    fig, ax = plt.subplots(figsize=(18, 8), dpi=220)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 9.5)
    ax.axis("off")

    ax.text(
        9,
        9.0,
        "Developer-User Compatibility Control Flow",
        ha="center",
        va="center",
        fontsize=TITLE_SIZE,
        weight="bold",
        family="DejaVu Sans",
    )

    add_round_box(
        ax,
        0.55,
        5.15,
        16.9,
        2.45,
        "",
        fc=LANE_FILL,
        ec=LANE_EDGE,
        fontsize=1,
        lw=1.8,
        radius=0.08,
    )
    add_round_box(
        ax,
        0.55,
        1.55,
        16.9,
        2.45,
        "",
        fc=LANE_FILL,
        ec=LANE_EDGE,
        fontsize=1,
        lw=1.8,
        radius=0.08,
    )

    add_round_box(
        ax,
        0.9,
        6.0,
        1.55,
        0.85,
        "Developer",
        fc=GOLD_FILL,
        ec=GOLD_EDGE,
        fontsize=13,
        weight="medium",
        radius=0.08,
    )
    add_round_box(
        ax,
        0.9,
        2.4,
        1.55,
        0.85,
        "User",
        fc=GREEN_FILL,
        ec=GREEN_EDGE,
        fontsize=13,
        weight="medium",
        radius=0.08,
    )

    dev_boxes = [
        (2.9, 5.7, 2.7, 1.35, "Change schema or\nExcel library"),
        (6.0, 5.7, 2.7, 1.35, "Run compatibility\nreview"),
        (9.1, 5.7, 3.2, 1.35, "Update migration,\nsnapshot, and history"),
        (12.8, 5.7, 2.7, 1.35, "Release\ncompatible code"),
    ]
    user_boxes = [
        (2.9, 2.1, 2.7, 1.35, "Open diagram or\nimport snapshot"),
        (6.0, 2.1, 2.7, 1.35, "System checks\ncompatibility"),
        (9.1, 2.1, 3.2, 1.35, "Create backup and\nupgrade if needed"),
        (12.8, 2.1, 2.7, 1.35, "Re-verify and\ncompute"),
    ]

    for x, y, w, h, label in dev_boxes:
        add_round_box(ax, x, y, w, h, label, fc=BLUE_FILL, ec=BLUE_EDGE, fontsize=12)
    for x, y, w, h, label in user_boxes:
        add_round_box(ax, x, y, w, h, label, fc=GREEN_FILL, ec=GREEN_EDGE, fontsize=12)

    for row in (dev_boxes, user_boxes):
        for i in range(len(row) - 1):
            x1, y1, w1, h1, _ = row[i]
            x2, y2, _, h2, _ = row[i + 1]
            add_arrow(
                ax,
                (x1 + w1, y1 + h1 / 2),
                (x2, y2 + h2 / 2),
                color="#2f855a",
                lw=2.2,
            )

    add_arrow(
        ax,
        (14.15, 5.7),
        (14.15, 3.45),
        color=LINE_DARK,
        lw=2.1,
    )

    add_round_box(
        ax,
        5.2,
        0.45,
        7.6,
        0.8,
        "Developer defines the compatibility boundary; user applies upgrade through the product workflow.",
        fc="#ffffff",
        ec="#d6d9e4",
        fontsize=10,
        lw=1.6,
        radius=0.08,
    )

    fig.tight_layout()
    path = OUT_DIR / "sep799_compatibility_control_swimlane.png"
    fig.savefig(path, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return path


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = [
        compat_architecture_figure(),
        compat_swimlane_figure(),
    ]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
