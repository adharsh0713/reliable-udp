
import os

import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = "data/results/experiment_results.csv"
GRAPH_DIR = "data/results/graphs"
SUMMARY_FILE = "data/results/aggregated_results.csv"

os.makedirs(GRAPH_DIR, exist_ok=True)

PROTOCOLS = [
    "stop_wait",
    "go_back_n",
    "selective_repeat",
]

METRICS = {
    "throughput": (
        "Throughput (bytes/sec)",
        "throughput_dashboard.png",
    ),
    "completion_time": (
        "Completion Time (seconds)",
        "completion_time_dashboard.png",
    ),
    "retransmissions": (
        "Retransmissions",
        "retransmissions_dashboard.png",
    ),
}


def load_results():
    df = pd.read_csv(CSV_FILE)

    if "hash_verified" in df.columns:
        df = df[
            df["hash_verified"]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("true")
        ].copy()

    numeric_columns = [
        "file_size",
        "window",
        "data_loss",
        "throughput",
        "completion_time",
        "retransmissions",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    required = [
        "protocol",
        "file_name",
        "file_size",
        "window",
        "data_loss",
        "throughput",
        "completion_time",
        "retransmissions",
    ]

    df = df.dropna(subset=required)

    if df.empty:
        raise ValueError("No valid experiment records found.")

    return df


# Original-style individual graphs: three overall comparisons.
def plot_metric(data, metric, ylabel, filename):
    plt.figure(figsize=(8, 5))

    for protocol in sorted(data["protocol"].unique()):
        subset = data[
            data["protocol"] == protocol
        ].sort_values("data_loss")

        plt.plot(
            subset["data_loss"],
            subset[metric],
            marker="o",
            label=protocol,
        )

    plt.xlabel("Packet Loss Rate")
    plt.ylabel(ylabel)
    plt.title(f"{ylabel} vs Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        os.path.join(GRAPH_DIR, filename),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def aggregate_results(df):
    keys = [
        "protocol",
        "file_name",
        "file_size",
        "window",
        "data_loss",
    ]

    summary = (
        df.groupby(keys, as_index=False)
        .agg(
            throughput_mean=("throughput", "mean"),
            throughput_std=("throughput", "std"),
            completion_time_mean=("completion_time", "mean"),
            completion_time_std=("completion_time", "std"),
            retransmissions_mean=("retransmissions", "mean"),
            retransmissions_std=("retransmissions", "std"),
            trials=("protocol", "size"),
        )
    )

    summary.to_csv(SUMMARY_FILE, index=False)
    return summary


# Dashboards: rows are files, columns are protocols.
# Different lines represent window sizes.
def plot_dashboard(summary, metric, ylabel, filename):
    files = sorted(summary["file_name"].unique())

    fig, axes = plt.subplots(
        len(files),
        len(PROTOCOLS),
        figsize=(16, max(4 * len(files), 8)),
        squeeze=False,
    )

    mean_col = f"{metric}_mean"
    std_col = f"{metric}_std"

    for row, file_name in enumerate(files):
        for col, protocol in enumerate(PROTOCOLS):
            ax = axes[row][col]

            subset = summary[
                (summary["file_name"] == file_name)
                & (summary["protocol"] == protocol)
            ]

            if subset.empty:
                ax.text(
                    0.5, 0.5, "No data",
                    ha="center", va="center",
                    transform=ax.transAxes,
                )
            else:
                for window in sorted(subset["window"].unique()):
                    part = subset[
                        subset["window"] == window
                    ].sort_values("data_loss")

                    ax.errorbar(
                        part["data_loss"],
                        part[mean_col],
                        yerr=part[std_col].fillna(0),
                        marker="o",
                        capsize=3,
                        label=f"Window {int(window)}",
                    )

                ax.legend(fontsize=8)

            ax.set_title(f"{file_name} — {protocol}")
            ax.set_xlabel("Packet loss rate")
            ax.set_ylabel(ylabel)
            ax.grid(True, alpha=0.3)

    fig.suptitle(
        f"{ylabel}: file, protocol and window comparison",
        fontsize=15,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    fig.savefig(
        os.path.join(GRAPH_DIR, filename),
        dpi=200,
        bbox_inches="tight",
    )
    plt.close(fig)


def main():
    df = load_results()

    # Generate the three existing individual graph files.
    overall = (
        df.groupby(
            ["protocol", "data_loss"],
            as_index=False,
        )
        .agg(
            throughput=("throughput", "mean"),
            completion_time=("completion_time", "mean"),
            retransmissions=("retransmissions", "mean"),
        )
    )

    plot_metric(
        overall,
        "throughput",
        "Throughput (bytes/sec)",
        "throughput_vs_loss.png",
    )

    plot_metric(
        overall,
        "completion_time",
        "Completion Time (seconds)",
        "completion_vs_loss.png",
    )

    plot_metric(
        overall,
        "retransmissions",
        "Average Retransmissions",
        "retransmissions_vs_loss.png",
    )

    # Generate three separate dashboards.
    summary = aggregate_results(df)

    for metric, (ylabel, filename) in METRICS.items():
        plot_dashboard(
            summary,
            metric,
            ylabel,
            filename,
        )

    print(f"Verified records analyzed: {len(df)}")
    print(f"Aggregated configurations: {len(summary)}")
    print(f"Graphs saved in: {GRAPH_DIR}")
    print("Individual graphs and all three dashboards generated.")


if __name__ == "__main__":
    main()
