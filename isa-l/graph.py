import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# python graph.py /tmp/xor_4k.csv:"4K normal page"  \
#                 /tmp/xor_2m.csv:"2M huge page"    \
#                 --title "Histogram of xor benchmark on ThunderX2"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', help='image title')
    parser.add_argument('-n', '--nograph', action='store_true')
    parser.add_argument('csvfiles', nargs='+')
    return parser.parse_args()


def process_df_lst(args):
    df_legend_lst = []

    for csvfile_legend in args.csvfiles:
        sp = csvfile_legend.split(':')
        csvfile = sp[0]
        legend = sp[1] if len(sp) > 1 else os.path.splitext(
            os.path.basename(csvfile))[0]
        legend = legend.lstrip('_')
        df_legend_lst.append((pd.read_csv(csvfile), legend))

    return df_legend_lst


# plot histgram of multiple csvfiles
def plot_hist(args, df_legend_lst):
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    minv, maxv = 99999999, -1
    for df, _ in df_legend_lst:
        minv = min(minv, df['bandwidth'].min())
        maxv = max(maxv, df['bandwidth'].max())
    delta = maxv - minv
    bins = np.arange(minv-delta*0.05, maxv+delta*0.05, 64)

    for i, (df, legend) in enumerate(df_legend_lst):
        ax.hist(df['bandwidth'], bins=bins, label=legend)

    ax.set_xlim([minv/2, maxv*1.05])
    ax.set_title(args.title)
    ax.set_xlabel('Bandwidth')
    ax.set_ylabel('Count')
    ax.legend()

    fig.savefig('histogram.png', bbox_inches='tight')

    if not args.nograph:
        plt.show()


if __name__ == '__main__':
    args = parse_args()

    df_legend_lst = process_df_lst(args)
    plot_hist(args, df_legend_lst)
