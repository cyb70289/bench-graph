import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', help='image title')
    parser.add_argument('-n', '--nograph', action='store_true')
    parser.add_argument('csvfiles', nargs='+')
    return parser.parse_args()


def process_df(csvfiles):
    df = pd.DataFrame()
    for csvfile in csvfiles:
        df1 = pd.read_csv(csvfile)
        df1.columns = df1.columns.map(str.strip)
        df1['type'] = df1['type'].apply(str.strip)
        df1['threads'] = df1['id'].apply(lambda x: int(x.split()[0]))
        df1 = df1[['type', 'threads', 'op/s', 'mean']]
        df = pd.concat([df, df1], ignore_index=True)
    return df


def plot_line(ax, x, y, op_type):
    ax.set_title(y['label'] + '<-->' + x['label'])
    ax.set_xlabel(x['label'])
    ax.set_ylabel(y['label'])
    # ax.set_xlim(*x['range'])
    # ax.set_ylim(*y['range'])
    ax.plot(x['data'], y['data'], label=op_type)


def plot_df(args, df):
    fig, ax = plt.subplots(1, 3, figsize=(24, 6))
    fig.subplots_adjust(wspace=0.2)

    threads = {'data': None, 'label': 'Threads',     'range': (0, 1200)}
    ops =     {'data': None, 'label': 'OPS(K)',      'range': (0, 200) }
    latency = {'data': None, 'label': 'Latency(ms)', 'range': (0, 10)  }

    for op_type in df['type'].unique():
        df1 = df[df['type'] == op_type]
        threads['data'] = df1['threads']
        ops['data'] = df1['op/s'] // 1000
        latency['data'] = df1['mean']
        plot_line(ax[0], threads, ops, op_type)
        plot_line(ax[1], threads, latency, op_type)
        plot_line(ax[2], ops, latency, op_type)

    ax[0].legend(title='Operation')
    ax[1].legend(title='Operation')
    ax[2].legend(title='Operation')

    f = os.path.splitext(args.csvfiles[0])[0] + '.png'
    fig.savefig(f, bbox_inches='tight')

    if not args.nograph:
        plt.show()


if __name__ == '__main__':
    args = parse_args()

    df = process_df(args.csvfiles)
    plot_df(args, df)
