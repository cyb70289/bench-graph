import sys
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


if __name__ == '__main__':
    fn = './sort-range.csv' if len(sys.argv) == 1 else sys.argv[1]
    df = pd.read_csv(fn)

    xmin, xmax = df['count'].agg([min, max])
    ymin, ymax = df['speedup'].agg([min, max])

    plt.figure(figsize=(16, 9))

    for r, grp in df.groupby('range'):
        plt.plot(grp['count'], grp['speedup'], label=r)

    plt.hlines(1, xmin, xmax, linestyles='dashdot', linewidth=2)

    plt.xscale('log')

    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

    xticks = df['count'].unique()
    plt.xticks(xticks, xticks)
    yticks = range(0, int(df['speedup'].max())+2)
    plt.yticks(yticks, yticks)

    plt.xlabel('array size', fontsize=14)
    plt.ylabel('speed ratio of counting sort vs std::stable_sort', fontsize=14)
    plt.legend(title='value range', title_fontsize=12)

    plt.savefig(re.sub(r'csv$', 'png', fn), bbox_inches='tight')
    plt.show()
