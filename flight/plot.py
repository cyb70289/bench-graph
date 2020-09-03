import sys
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


if __name__ == '__main__':
    fn = './flight.csv' if len(sys.argv) == 1 else sys.argv[1]
    df = pd.read_csv(fn)
    df_get = df[df['Mode'] == 'get']
    df_put = df[df['Mode'] == 'put']
    xticks = df['Threads'].unique()

    fig, ax = plt.subplots(1, 2, figsize=(16, 5), squeeze=False)
    fig.subplots_adjust(wspace=0.2)
    if len(sys.argv) == 3:
        fig.suptitle(sys.argv[2], fontsize=16)

    ax_bandwidth = ax[0][0]
    ax_bandwidth.plot(df_get['Threads'], df_get['Bandwidth'], label="Get",
                      color = 'red')
    ax_bandwidth.plot(df_put['Threads'], df_put['Bandwidth'], label="Put",
                      color = 'green')
    ax_bandwidth.set_xlabel('Threads/Streams', fontsize=14)
    ax_bandwidth.set_ylabel('Bandwidth(MB/s)', fontsize=14)
    ax_bandwidth.legend(title='Mode', title_fontsize=12)
    ax_bandwidth.set_xticks(xticks)

    ax_latency = ax[0][1]
    ax_latency.plot(df_get['Threads'], df_get['Latency'], label="Get",
                    color = 'red')
    ax_latency.plot(df_put['Threads'], df_put['Latency'], label="Put",
                    color = 'green')
    ax_latency.set_xlabel('Threads/Streams', fontsize=14)
    ax_latency.set_ylabel('Latency(us)', fontsize=14)
    ax_latency.legend(title='Mode', title_fontsize=12)
    ax_latency.set_xticks(xticks)

    fig.savefig(re.sub(r'csv$', 'png', fn), bbox_inches='tight')
    plt.show()
