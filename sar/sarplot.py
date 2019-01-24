import os
import re
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Bench(object):
    def __init__(self, df, args):
        self.df = df
        self.args = args

    def match(self):
        raise NotImplemented

    def parse_args(self):
        pass

    def plot(self):
        raise NotImplemented

    def prepare_plot(self, ngraph, max_cols=4):
        nrow, ncol = 1, ngraph
        if ncol > max_cols:
            nrow = (ncol+max_cols-1)//max_cols
            ncol = max_cols
        fig, ax = plt.subplots(nrow, ncol, figsize=(8*ncol, 6*nrow),
                               squeeze=False)
        fig.subplots_adjust(wspace=0.2)
        return fig, ax

    # 2D list to 1D list
    @staticmethod
    def flatten(ax):
        return [x for sublist in ax for x in sublist]


class BenchCPU(Bench):
    def __init__(self, df, args):
        super(BenchCPU, self).__init__(df, args)

    def match(self):
        return 'CPU' in self.df.columns

    def parse_args(self):
        cpu_max = self.df['CPU'].max()
        cpu_str = self.args.cpu
        if cpu_str is None:
            cpu_str = 'all'
        self.cpu_str = cpu_str

        self.cpu_lst = []
        if cpu_str.lower().find('all') != -1:
            self.cpu_lst += list(range(cpu_max+1))
        else:
            # 1,8-24,31
            for cpus in cpu_str.split(','):
                if re.match('[0-9]+-[0-9]+', cpus):
                    start, end = map(int, cpus.split('-'))
                    self.cpu_lst += list(range(start, end+1))
                elif re.match('[0-9]+', cpus):
                    self.cpu_lst.append(int(cpus))
                else:
                    raise ValueError('Wrong CPU list format {}!'.format(cpus))
            if max(self.cpu_lst) > cpu_max:
                raise ValueError('CPU number out of bound!')

        self.cpu_lst.sort()

    def plot(self):
        fig, ax = self.prepare_plot(2)
        # Plot average value if count > 8
        if len(self.cpu_lst) > 8 and not self.args.noagg:
            df = self.df[self.df['CPU'].isin(self.cpu_lst)]
            df = df.groupby('logtime', as_index=False).mean()
            ax[0][0].plot(df['logtime'], 100-df['%idle'])
            ax[0][0].set_title('Load - CPU:'+self.cpu_str)
            ax[0][1].plot(df['logtime'], df['%iowait'])
            ax[0][1].set_title('IOWait - CPU:'+self.cpu_str)
        else:
            for cpu in self.cpu_lst:
                df = self.df[self.df['CPU'] == cpu]
                ax[0][0].plot(df['logtime'], 100-df['%idle'],
                              label='cpu-'+str(cpu))
                ax[0][1].plot(df['logtime'], df['%iowait'],
                              label='cpu-'+str(cpu))
            ax[0][0].set_title('Load per CPU')
            ax[0][1].set_title('IOWait per CPU')
            ax[0][0].legend()
            ax[0][1].legend()
        ax[0][0].set_ylabel('Load', fontsize=14)
        ax[0][1].set_ylabel('IOWait', fontsize=14)

        fig.savefig('cpu.png', bbox_inches='tight')
        plt.show()


class BenchBLK(Bench):
    def __init__(self, df, args):
        super(BenchBLK, self).__init__(df, args)

    def match(self):
        return 'DEV' in self.df.columns

    def parse_args(self):
        devs = self.df['DEV'].unique()
        devs_str = self.args.dev

        self.dev_lst = []
        if devs_str is None:
            m = re.compile("^loop|.*[0-9]$")
            self.dev_lst += [dev for dev in devs if not m.match(dev)]
        else:
            # sda,sdb1
            for dev in devs_str.split(','):
                if dev not in devs:
                    raise ValueError('Unknown device {}!'.format(dev))
                self.dev_lst.append(dev)

        self.dev_lst.sort()

    def plot(self):
        fig, ax = self.prepare_plot(len(self.dev_lst)*4, 4)
        for i, dev in enumerate(self.dev_lst):
            df = self.df[self.df['DEV'] == dev]
            # tps
            ax[i][0].plot(df['logtime'], df['tps'])
            ax[i][0].set_title(dev+' - IOPS')
            ax[i][0].set_ylabel('Transfers per second', fontsize=14)
            # rkB/s, wkB/s
            ax[i][1].plot(df['logtime'], df['rkB/s'], label='read')
            ax[i][1].plot(df['logtime'], df['wkB/s'], label='write')
            ax[i][1].set_title(dev+' - Read,Write')
            ax[i][1].set_ylabel('KB per second', fontsize=14)
            ax[i][1].legend()
            # %util
            ax[i][2].plot(df['logtime'], df['%util'])
            ax[i][2].set_title(dev+' - Utilization')
            ax[i][2].set_ylabel('Device utilization', fontsize=14)
            l = ['{:.0f}%'.format(y) for y in ax[i][2].get_yticks().tolist()]
            ax[i][2].set_yticklabels(l)
            # await, svctm
            ax[i][3].plot(df['logtime'], df['await'], label='await')
            ax[i][3].plot(df['logtime'], df['svctm'], label='svctm')
            ax[i][3].set_title(dev+' - IOWAIT')
            ax[i][3].set_ylabel('Milliseconds', fontsize=14)
            ax[i][3].legend()

        fig.savefig('blk.png', bbox_inches='tight')
        plt.show()


class BenchNET(Bench):
    def __init__(self, df, args):
        super(BenchNET, self).__init__(df, args)

    def match(self):
        return 'IFACE' in self.df.columns

    def parse_args(self):
        devs = self.df['IFACE'].unique()
        devs_str = self.args.dev

        self.dev_lst = []
        if devs_str is None:
            self.dev_lst += [dev for dev in devs if dev != 'lo']
        else:
            # eth0,eth1
            for dev in devs_str.split(','):
                if dev not in devs:
                    raise ValueError('Unknown device {}!'.format(dev))
                self.dev_lst.append(dev)

        self.dev_lst.sort()

    def plot(self):
        fig, ax = self.prepare_plot(len(self.dev_lst))
        ax = self.flatten(ax)
        for i, dev in enumerate(self.dev_lst):
            df = self.df[self.df['IFACE'] == dev]
            ax[i].plot(df['logtime'], df['rxkB/s']//1000, label='RX')
            ax[i].plot(df['logtime'], df['txkB/s']//1000, label='TX')
            ax[i].set_title(dev)
            ax[i].set_ylabel('MB/s', fontsize=14)
            ax[i].legend()

        fig.savefig('net.png', bbox_inches='tight')
        plt.show()


class BenchMEM(Bench):
    def __init__(self, df, args):
        super(BenchMEM, self).__init__(df, args)

    def match(self):
        return 'kbmemfree' in self.df.columns

    def plot(self):
        fig, ax = self.prepare_plot(1)
        ax[0][0].plot(self.df['logtime'], self.df['%memused'])
        ax[0][0].set_title('Memory usage')
        ax[0][0].set_ylabel('Memory used', fontsize=14)
        # append % to y labels
        ylabels = ['{:.0f}%'.format(y) for y in ax[0][0].get_yticks().tolist()]
        ax[0][0].set_yticklabels(ylabels)

        fig.savefig('mem.png', bbox_inches='tight')
        plt.show()


def bench_plot(args):
    df = pd.read_csv(args.csvfile[0], delim_whitespace=True)
    # adjust time column. XXX: should consider day change
    logtime = pd.to_datetime(df['logtime'])
    logtime = (logtime - logtime[0]).apply(pd.Timedelta.total_seconds)
    df['logtime'] = logtime.apply(int)
    # select wanted timeslot
    if args.start_second:
        df = df[df['logtime'] >= args.start_second]
    if args.end_second:
        df= df[df['logtime'] <= args.end_second]

    for bench_class in [BenchCPU, BenchBLK, BenchNET, BenchMEM]:
        bench = bench_class(df, args)
        if bench.match():
            bench.parse_args()
            bench.plot()
            break
    else:
        raise Exception('No matching bench parser found!')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dev', help='disk or nic list')
    parser.add_argument('--cpu', help='cpu list')
    parser.add_argument('--noagg', action='store_true', help='no aggragation')
    parser.add_argument('-s', '--start-second', type=int, help='start second')
    parser.add_argument('-e', '--end-second', type=int, help='end second')
    parser.add_argument('csvfile', nargs=1)
    return parser.parse_args()


if __name__ == '__main__':
    bench_plot(parse_args())
