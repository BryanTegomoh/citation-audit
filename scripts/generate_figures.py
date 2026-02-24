#!/usr/bin/env python3
"""
Figure Generator for Citation Verification Paper

Generates publication-quality figures for the research paper.

Requires: matplotlib, seaborn, pandas
Install: pip install matplotlib seaborn pandas
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import seaborn as sns
    import pandas as pd
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("Warning: matplotlib/seaborn not installed. Install with: pip install matplotlib seaborn pandas")


# Publication-quality settings
FIGURE_DPI = 300
FIGURE_FORMAT = 'png'  # or 'pdf', 'svg'

# Color palette (colorblind-friendly)
COLORS = {
    'broken_url': '#E74C3C',      # Red
    'wrong_paper': '#9B59B6',     # Purple
    'author_error': '#3498DB',    # Blue
    'year_error': '#2ECC71',      # Green
    'claim_mismatch': '#F39C12',  # Orange
    'journal_error': '#1ABC9C',   # Teal
    'metric_error': '#E91E63',    # Pink
    'fabricated': '#34495E',      # Dark gray
    'verified': '#27AE60',        # Green
}


def load_report(report_path: str) -> Dict:
    """Load verification report from JSON."""
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def figure_1_pipeline_diagram(output_dir: Path) -> None:
    """
    Figure 1: Four-Phase Pipeline Diagram

    Creates a flowchart showing the verification pipeline.
    """
    if not PLOTTING_AVAILABLE:
        return

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Phase boxes
    phases = [
        (1.5, 8, 'Phase 1\nURL/DOI Resolution', '#3498DB'),
        (1.5, 6, 'Phase 2\nContent-Claim Alignment', '#9B59B6'),
        (1.5, 4, 'Phase 3\nMetadata Verification', '#2ECC71'),
        (1.5, 2, 'Phase 4\nCorrection & Replacement', '#E74C3C'),
    ]

    # Error outputs
    errors = [
        (5.5, 8, 'Broken URL\n(21.4%)', '#E74C3C'),
        (5.5, 6, 'Wrong Paper\nClaim Mismatch\n(44.3%)', '#9B59B6'),
        (5.5, 4, 'Author/Year/\nJournal Error\n(34.3%)', '#2ECC71'),
    ]

    # Draw phase boxes
    for x, y, text, color in phases:
        box = mpatches.FancyBboxPatch(
            (x-1, y-0.6), 2.5, 1.2,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor='black', alpha=0.7
        )
        ax.add_patch(box)
        ax.text(x+0.25, y, text, ha='center', va='center', fontsize=10, fontweight='bold', color='white')

    # Draw error output boxes
    for x, y, text, color in errors:
        box = mpatches.FancyBboxPatch(
            (x-1, y-0.6), 2.5, 1.2,
            boxstyle="round,pad=0.1",
            facecolor='white', edgecolor=color, linewidth=2
        )
        ax.add_patch(box)
        ax.text(x+0.25, y, text, ha='center', va='center', fontsize=9, color=color)

    # Draw arrows between phases
    for i in range(3):
        ax.annotate('', xy=(1.5, phases[i+1][1]+0.6), xytext=(1.5, phases[i][1]-0.6),
                    arrowprops=dict(arrowstyle='->', color='black', lw=1.5))

    # Draw arrows to error outputs
    for i in range(3):
        ax.annotate('', xy=(errors[i][0]-1, errors[i][1]), xytext=(phases[i][0]+1.5, phases[i][1]),
                    arrowprops=dict(arrowstyle='->', color='gray', lw=1, ls='--'))

    # Title
    ax.text(5, 9.5, 'Four-Phase Citation Verification Pipeline', ha='center', fontsize=14, fontweight='bold')

    # Input/Output labels
    ax.text(1.5, 9.2, 'INPUT:\nCitation + Claim', ha='center', fontsize=9, style='italic')
    ax.text(1.5, 0.8, 'OUTPUT:\nVerified/Corrected', ha='center', fontsize=9, style='italic')

    plt.tight_layout()
    plt.savefig(output_dir / 'figure1_pipeline.png', dpi=FIGURE_DPI, bbox_inches='tight')
    plt.close()
    print(f"  Saved: figure1_pipeline.png")


def figure_2_error_distribution(report: Dict, output_dir: Path) -> None:
    """
    Figure 2: Error Distribution Bar Chart

    Shows the distribution of error types.
    """
    if not PLOTTING_AVAILABLE:
        return

    # Extract data from report or use provided data
    categories = ['Wrong\nPaper', 'Broken\nURL', 'Year\nError', 'Author\nError',
                  'Claim\nMismatch', 'Journal\nError', 'Metric\nError', 'Fabricated']
    counts = [18, 15, 9, 8, 7, 7, 6, 1]
    percentages = [25.7, 21.4, 12.9, 11.4, 10.0, 10.0, 8.6, 1.4]

    colors = [COLORS['wrong_paper'], COLORS['broken_url'], COLORS['year_error'],
              COLORS['author_error'], COLORS['claim_mismatch'], COLORS['journal_error'],
              COLORS['metric_error'], COLORS['fabricated']]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(categories, counts, color=colors, edgecolor='black', alpha=0.8)

    # Add percentage labels on bars
    for bar, pct in zip(bars, percentages):
        height = bar.get_height()
        ax.annotate(f'{pct}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

    ax.set_ylabel('Number of Errors', fontsize=12)
    ax.set_xlabel('Error Category', fontsize=12)
    ax.set_title('Distribution of Citation Errors by Category (n=70)', fontsize=14, fontweight='bold')

    # Add gridlines
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure2_error_distribution.png', dpi=FIGURE_DPI, bbox_inches='tight')
    plt.close()
    print(f"  Saved: figure2_error_distribution.png")


def figure_3_detection_comparison(output_dir: Path) -> None:
    """
    Figure 3: Detection Capability Comparison

    Compares what different verification methods can detect.
    """
    if not PLOTTING_AVAILABLE:
        return

    methods = ['Automated\nLink Check', 'DOI Syntax\nValidation', 'Reference\nManager',
               'Phase 1-2\n(+Content)', 'Full Pipeline\n(1-3)']
    detected = [15, 3, 0, 46, 70]
    missed = [55, 67, 70, 24, 0]

    x = range(len(methods))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))

    bars1 = ax.bar([i - width/2 for i in x], detected, width, label='Detected', color='#27AE60', edgecolor='black')
    bars2 = ax.bar([i + width/2 for i in x], missed, width, label='Missed', color='#E74C3C', edgecolor='black')

    # Add labels
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10)

    ax.set_ylabel('Number of Errors', fontsize=12)
    ax.set_xlabel('Verification Method', fontsize=12)
    ax.set_title('Error Detection Capability by Verification Method', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.legend(loc='upper right')

    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure3_detection_comparison.png', dpi=FIGURE_DPI, bbox_inches='tight')
    plt.close()
    print(f"  Saved: figure3_detection_comparison.png")


def figure_4_chapter_heatmap(output_dir: Path) -> None:
    """
    Figure 4: Error Rate Heatmap by Chapter

    Shows error rates across chapters as a heatmap.
    """
    if not PLOTTING_AVAILABLE:
        return

    # Chapter data
    chapters = ['history', 'ai-basics', 'clinical-data', 'obgyn', 'critical-care',
                'infectious-diseases', 'oncology', 'neurology', 'psychiatry',
                'primary-care', 'pathology', 'dermatology', 'ophthalmology']

    error_rates = [21.4, 25.0, 14.3, 81.8, 66.7, 80.0, 40.0, 77.8, 71.4, 71.4, 83.3, 40.0, 83.3]

    # Create DataFrame
    df = pd.DataFrame({'Chapter': chapters, 'Error Rate (%)': error_rates})
    df = df.sort_values('Error Rate (%)', ascending=False)

    fig, ax = plt.subplots(figsize=(10, 8))

    # Horizontal bar chart with color gradient
    colors = plt.cm.RdYlGn_r(df['Error Rate (%)'].values / 100)

    bars = ax.barh(df['Chapter'], df['Error Rate (%)'], color=colors, edgecolor='black')

    # Add percentage labels
    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'{width:.1f}%',
                    xy=(width, bar.get_y() + bar.get_height()/2),
                    xytext=(3, 0),
                    textcoords="offset points",
                    ha='left', va='center', fontsize=10)

    ax.set_xlabel('Error Rate (%)', fontsize=12)
    ax.set_ylabel('Chapter', fontsize=12)
    ax.set_title('Citation Error Rate by Chapter', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 100)

    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure4_chapter_heatmap.png', dpi=FIGURE_DPI, bbox_inches='tight')
    plt.close()
    print(f"  Saved: figure4_chapter_heatmap.png")


def figure_5_phase_detection_matrix(output_dir: Path) -> None:
    """
    Figure 5: Error Type Detection by Phase Matrix

    Shows which phase detects which error types.
    """
    if not PLOTTING_AVAILABLE:
        return

    error_types = ['Broken URL', 'Wrong Paper', 'Claim Mismatch', 'Metric Error',
                   'Author Error', 'Year Error', 'Journal Error', 'Fabricated']
    phases = ['Phase 1\n(URL)', 'Phase 2\n(Content)', 'Phase 3\n(Metadata)']

    # Detection matrix: 1 = primary detection, 0.5 = partial, 0 = not detected
    matrix = [
        [1, 0, 0],      # Broken URL
        [0, 1, 0],      # Wrong Paper
        [0, 1, 0],      # Claim Mismatch
        [0, 1, 0],      # Metric Error
        [0, 0, 1],      # Author Error
        [0, 0, 1],      # Year Error
        [0, 0, 1],      # Journal Error
        [0.5, 0.5, 0.5],  # Fabricated (can be detected at multiple phases)
    ]

    fig, ax = plt.subplots(figsize=(8, 6))

    cmap = plt.cm.Blues
    im = ax.imshow(matrix, cmap=cmap, aspect='auto', vmin=0, vmax=1)

    ax.set_xticks(range(len(phases)))
    ax.set_xticklabels(phases, fontsize=11)
    ax.set_yticks(range(len(error_types)))
    ax.set_yticklabels(error_types, fontsize=11)

    # Add text annotations
    for i in range(len(error_types)):
        for j in range(len(phases)):
            val = matrix[i][j]
            text = '●' if val == 1 else ('◐' if val == 0.5 else '○')
            color = 'white' if val > 0.5 else 'black'
            ax.text(j, i, text, ha='center', va='center', fontsize=16, color=color)

    ax.set_title('Error Type Detection by Verification Phase', fontsize=14, fontweight='bold')

    # Legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#2E86AB',
                   markersize=12, label='Primary detection'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#87CEEB',
                   markersize=12, label='Partial detection'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='white',
                   markeredgecolor='black', markersize=12, label='Not detected'),
    ]
    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3)

    plt.tight_layout()
    plt.savefig(output_dir / 'figure5_detection_matrix.png', dpi=FIGURE_DPI, bbox_inches='tight')
    plt.close()
    print(f"  Saved: figure5_detection_matrix.png")


def figure_6_pie_chart(output_dir: Path) -> None:
    """
    Figure 6: Overall Results Pie Chart

    Shows proportion of correct vs error citations.
    """
    if not PLOTTING_AVAILABLE:
        return

    labels = ['Verified Correct\n(53.3%)', 'Errors Found\n(46.7%)']
    sizes = [53.3, 46.7]
    colors = ['#27AE60', '#E74C3C']
    explode = (0, 0.05)

    fig, ax = plt.subplots(figsize=(8, 8))

    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, colors=colors,
        autopct='', startangle=90, shadow=True,
        wedgeprops=dict(edgecolor='black', linewidth=1.5)
    )

    # Customize text
    for text in texts:
        text.set_fontsize(14)
        text.set_fontweight('bold')

    ax.set_title('Citation Verification Results (n=150)', fontsize=16, fontweight='bold', pad=20)

    # Add center text
    ax.text(0, 0, '150\ncitations', ha='center', va='center', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_dir / 'figure6_pie_chart.png', dpi=FIGURE_DPI, bbox_inches='tight')
    plt.close()
    print(f"  Saved: figure6_pie_chart.png")


def generate_all_figures(report_path: Optional[str], output_dir: str) -> None:
    """Generate all figures for the paper."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load report if provided
    report = load_report(report_path) if report_path else {}

    print("Generating figures...")

    figure_1_pipeline_diagram(output_path)
    figure_2_error_distribution(report, output_path)
    figure_3_detection_comparison(output_path)
    figure_4_chapter_heatmap(output_path)
    figure_5_phase_detection_matrix(output_path)
    figure_6_pie_chart(output_path)

    print(f"\nAll figures saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Generate figures for citation verification paper')
    parser.add_argument('-r', '--report', help='Verification report JSON file (optional)')
    parser.add_argument('-o', '--output', default='figures', help='Output directory for figures')

    args = parser.parse_args()

    if not PLOTTING_AVAILABLE:
        print("Error: matplotlib and seaborn are required.")
        print("Install with: pip install matplotlib seaborn pandas")
        return

    generate_all_figures(args.report, args.output)


if __name__ == '__main__':
    main()
