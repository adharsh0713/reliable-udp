import pandas as pd
import matplotlib.pyplot as plt
import os


CSV_FILE = "data/results/experiment_results.csv"

GRAPH_DIR = "data/results/graphs"


os.makedirs(
    GRAPH_DIR,
    exist_ok=True
)


def load_results():

    return pd.read_csv(
        CSV_FILE
    )


def average_by_loss(df):

    return (
        df.groupby(
            [
                "protocol",
                "data_loss"
            ]
        )
        .agg(
            {
                "throughput": "mean",
                "completion_time": "mean",
                "retransmissions": "mean"
            }
        )
        .reset_index()
    )


def plot_metric(
    data,
    metric,
    ylabel,
    filename
):

    plt.figure(
        figsize=(8,5)
    )


    for protocol in data["protocol"].unique():

        subset = data[
            data["protocol"] == protocol
        ]

        plt.plot(
            subset["data_loss"],
            subset[metric],
            marker="o",
            label=protocol
        )


    plt.xlabel(
        "Packet Loss Rate"
    )

    plt.ylabel(
        ylabel
    )

    plt.title(
        f"{ylabel} vs Loss"
    )

    plt.legend()

    plt.grid(
        True
    )


    plt.savefig(
        f"{GRAPH_DIR}/{filename}",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()



def main():

    df = load_results()


    avg = average_by_loss(
        df
    )


    print(avg)


    plot_metric(
        avg,
        "throughput",
        "Throughput (bytes/sec)",
        "throughput_vs_loss.png"
    )


    plot_metric(
        avg,
        "completion_time",
        "Completion Time (seconds)",
        "completion_vs_loss.png"
    )


    plot_metric(
        avg,
        "retransmissions",
        "Average Retransmissions",
        "retransmissions_vs_loss.png"
    )


if __name__ == "__main__":
    main()