import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# File paths for input TSV files
input_files = [
    "output_statistics/total_views_per_player.tsv",
    "output_statistics/average_views_per_player.tsv",
    "output_statistics/likes_per_view_per_player.tsv",
    "output_statistics/comments_per_view_per_player.tsv",
    "output_statistics/total_views_per_character.tsv",
    "output_statistics/average_views_per_character.tsv",
    "output_statistics/likes_per_view_per_character.tsv",
    "output_statistics/comments_per_view_per_character.tsv",
    "output_statistics/likes_per_view_per_player.tsv",
    "output_statistics/likes_per_view_per_character.tsv",
    "output_statistics/comments_per_view_per_player.tsv",
    "output_statistics/comments_per_view_per_character.tsv"
]

# Output directory for PDFs
output_pdf_files = [
    "output_graphs/total_views_per_player.pdf",
    "output_graphs/average_views_per_player.pdf",
    "output_graphs/likes_per_view_per_player.pdf",
    "output_graphs/comments_per_view_per_player.pdf",
    "output_graphs/total_views_per_character.pdf",
    "output_graphs/average_views_per_character.pdf",
    "output_graphs/likes_per_view_per_character.pdf",
    "output_graphs/comments_per_view_per_character.pdf",
    "output_graphs/total_likes_per_player.pdf",
    "output_graphs/total_likes_per_character.pdf",
    "output_graphs/total_comments_per_player.pdf",
    "output_graphs/total_comments_per_character.pdf"
]

# Function to create a horizontal bar chart
def create_horizontal_bar_chart(input_file, output_pdf, main_metric_col, label_col, title):
    """
    Creates a horizontal bar chart with modern styling.
    """
    # Load data
    data = pd.read_csv(input_file, sep="\t")

    # Sort data by the main metric column in descending order
    data = data.sort_values(by=main_metric_col, ascending=False).reset_index(drop=True)

    # Limit the number of bars to 100
    max_bars = 100
    data = data.head(max_bars)

    # Set up the figure
    bar_height = 1  # Each bar is 1 cm tall
    figsize = (8.27, max_bars * bar_height / 2.54)  # A4 width in inches, height depends on bar count
    fig, ax = plt.subplots(figsize=figsize, facecolor="#1A1A2E")  # Dark background

    # Plot bars with transparency and updated color
    bar_color = "#68D9D3"  # Light teal color
    bar_alpha = 0.8  # Transparency
    bars = ax.barh(data.index, data[main_metric_col], color=bar_color, alpha=bar_alpha)

    # Add text labels next to the bars with some spacing
    for i, (value, label) in enumerate(zip(data[main_metric_col], data[label_col])):
        ax.text(value + max(data[main_metric_col]) * 0.01, i, f"{label}", va='center', ha='left', color="white", fontsize=8)

    # Add values inside the top 10 bars
    for i, value in enumerate(data[main_metric_col]):
        if i < 10:  # Top 10 only
            ax.text(
                value / 2,
                i,
                f"{round(value, 4) if value < 1 else int(value) if isinstance(value, int) else round(value, 2)}",
                va='center',
                ha='center',
                color="white",
                fontsize=8
            )

    # Customize the axes
    ax.set_yticks(data.index)
    ax.set_yticklabels(range(1, len(data) + 1), color="white", fontsize=8)  # Rank as Y-labels
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(
        [
            round(x, 4) if x < 1 else int(x) if x.is_integer() else round(x, 2)
            for x in ax.get_xticks()
        ],
        color="white",
        fontsize=8
    )
    ax.invert_yaxis()  # Highest rank on top
    ax.set_facecolor("#1A1A2E")  # Dark plot background

    # Remove extra spacing between bars and plot frame
    ax.margins(y=0.01)  # Tighten space between bars and edges

    # Add vertical dashed lines at each tick and between ticks
    for x_tick in ax.get_xticks():
        ax.axvline(x=x_tick, color="#D3D3D3", linestyle="--", linewidth=0.5, alpha=0.5)  # Dashed line at tick

    # Add dashed lines between ticks (midpoints)
    xticks = ax.get_xticks()
    midpoints = [(xticks[i] + xticks[i + 1]) / 2 for i in range(len(xticks) - 1)]
    for midpoint in midpoints:
        ax.axvline(x=midpoint, color="#D3D3D3", linestyle="--", linewidth=0.5, alpha=0.3)  # Fainter dashed line between ticks

    # Frame styling: white color with reduced thickness
    frame_line_width = 0.5  # Reduce frame thickness
    for spine in ax.spines.values():
        spine.set_color("white")
        spine.set_linewidth(frame_line_width)

    # Tick styling: white ticks with reduced width
    tick_width = 0.5  # Reduced tick width
    ax.tick_params(axis="x", colors="white", width=tick_width, length=4)  # X-axis ticks
    ax.tick_params(axis="y", colors="white", width=tick_width, length=4)  # Y-axis ticks

    # Title and labels
    ax.set_title(title, color="white", fontsize=12, pad=10)
    ax.set_xlabel(main_metric_col, color="white", fontsize=10)

    # Save the chart as a PDF
    pdf = PdfPages(output_pdf)
    pdf.savefig(fig, bbox_inches="tight")
    pdf.close()

    plt.close(fig)

# Define configurations for each chart
chart_configs = [
    {"main_metric_col": "Total Views", "label_col": "Player", "title": "Total Views Per Player"},
    {"main_metric_col": "Average Views", "label_col": "Player", "title": "Average Views Per Player"},
    {"main_metric_col": "Likes Per View", "label_col": "Player", "title": "Likes Per View Per Player"},
    {"main_metric_col": "Comments Per View", "label_col": "Player", "title": "Comments Per View Per Player"},
    {"main_metric_col": "Total Views", "label_col": "Character", "title": "Total Views Per Character"},
    {"main_metric_col": "Average Views", "label_col": "Character", "title": "Average Views Per Character"},
    {"main_metric_col": "Likes Per View", "label_col": "Character", "title": "Likes Per View Per Character"},
    {"main_metric_col": "Comments Per View", "label_col": "Character", "title": "Comments Per View Per Character"},
    {"main_metric_col": "Total Likes", "label_col": "Player", "title": "Total Likes Per Player"},
    {"main_metric_col": "Total Likes", "label_col": "Character", "title": "Total Likes Per Character"},
    {"main_metric_col": "Total Comments", "label_col": "Player", "title": "Total Comments Per Player"},
    {"main_metric_col": "Total Comments", "label_col": "Character", "title": "Total Comments Per Character"}
]

# Generate charts for each input file
for input_file, output_pdf, config in zip(input_files, output_pdf_files, chart_configs):
    create_horizontal_bar_chart(
        input_file=input_file,
        output_pdf=output_pdf,
        main_metric_col=config["main_metric_col"],
        label_col=config["label_col"],
        title=config["title"]
    )

print("Bar charts generated and saved as PDFs.")
