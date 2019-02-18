#!/usr/bin/env python

import argparse
import numpy
import os
import pprint
import re
import subprocess
import textwrap

import matplotlib.pyplot as plt


DESCRIPTION = ('Run benchmark against recent Git revisions of a project, '
               'and plot the evolution of results. '
               'If no commands are provided, total source code lines in '
               'the repository are counted '
               '(git ls-files | xargs cat | wc -l).')

DEFAULT_COMMAND = 'git ls-files | xargs cat | wc -l'
DEFAULT_NUMBER = 100
DEFAULT_OUTPUT = 'evolution.png'
DEFAULT_SAMPLES = 1
MAX_MESSAGE_LENGTH = 48

TANGO_COLORS = (
    '#cc0000',  # Scarlet Red
    '#75507b',  # Plum
    '#3465a4',  # Sky Blue
    '#73d216',  # Chameleon
    '#c17d11',  # Chocolate
    '#f57900',  # Orange
    '#edd400',  # Butter
)

floats = re.compile(r"[-+]?\d*\.\d+|[-+]?\d+")


class GitRepository:

    def __init__(self, location):
        os.chdir(location)

        self.location = location
        self.checkout_master()

    def get_head(self):
        output = subprocess.check_output('git rev-parse HEAD', shell=True)
        return output.decode().strip()

    def checkout(self, revision):
        subprocess.check_call("git checkout {}".format(revision), shell=True)

    def checkout_master(self):
        self.checkout('master')

    def list_revisions(self, number):
        output = subprocess.check_output(
            "git log -{} --abbrev-commit --pretty=oneline".format(number),
            shell=True)
        lines = output.decode().strip().splitlines()
        return list(reversed([
            (line.split()[0],
             textwrap.shorten(line.split(' ', 1)[1], width=MAX_MESSAGE_LENGTH))
            for line in lines]))


class Runner:

    def __init__(self, repository, commands):
        self.repository = repository
        self.commands = commands

    def run_single(self, command, parse_float_at):
        output = subprocess.check_output(command, shell=True)
        numbers = floats.findall(output.decode())
        assert numbers, 'no number could be parsed from the output'
        return float(numbers[parse_float_at])

    def run(self, revisions, samples, parse_float_at):
        results = [list() for i in range(len(self.commands))]

        for revision, message in revisions:
            self.repository.checkout(revision)
            for i, command in enumerate(self.commands):
                results[i].append([self.run_single(command, parse_float_at)
                                   for s in range(samples)])

        return results


class Plot:

    def __init__(self, commands, revisions, results):
        self.commands = commands
        self.revisions = revisions
        self.results = results

    def plot(self, output, ylabel=None):
        plt.rcParams['figure.figsize'] = (16, 9)
        plt.rcParams['savefig.dpi'] = 100

        for index, command in enumerate(self.commands):
            label = os.path.basename(command.strip().split()[0])
            data = self.results[index]

            x = []
            y = []
            for i, samples in enumerate(data):
                x.extend([i] * len(samples))
                y.extend(samples)
            plt.plot(x, y, 'o', color=TANGO_COLORS[index])

            averaged = [numpy.average(samples) for samples in data]
            plt.plot(averaged, '-', label=label, color=TANGO_COLORS[index])

        xticks = [': '.join(item) for item in self.revisions]
        plt.xlim(0, len(xticks)-1)
        plt.xticks(range(len(xticks)), xticks, rotation='vertical')
        if ylabel:
            plt.ylabel(ylabel)

        # Tweak spacing to prevent clipping of tick-labels, and better use
        # available area
        plt.subplots_adjust(left=0.07, top=0.97, right=0.97, bottom=0.5)

        plt.legend()

        plt.savefig(output)


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        'repository', help='path of a Git repository to benchmark')
    parser.add_argument(
        'command', nargs='*',
        help='commands to plot results for (can be repeated)')
    parser.add_argument(
        '-n', '--number', type=int, default=DEFAULT_NUMBER,
        help='maximum number of recent revisions to include '
        '(default: %(default)s)')
    parser.add_argument(
        '-o', '--output', default=DEFAULT_OUTPUT,
        help='path to the output image (default: %(default)s)')
    parser.add_argument(
        '-p', '--parse-float-at', type=int, default=-1,
        help='of all floats/ints parsed from the output, take this '
        '(Python indexing, default: %(default)s)')
    parser.add_argument(
        '-s', '--samples', type=int, default=DEFAULT_SAMPLES,
        help='amount of samples for each revision/command '
        '(default: %(default)s)')
    parser.add_argument(
        '-y', '--ylabel', default='Benchmark result', help='Y axis label')

    args = parser.parse_args()

    commands = args.command or [DEFAULT_COMMAND]
    assert len(commands) <= len(TANGO_COLORS), 'too many commands!'
    output = os.path.abspath(args.output)

    repository = GitRepository(args.repository)
    revisions = repository.list_revisions(args.number)
    runner = Runner(repository, commands)

    try:
        results = runner.run(revisions, args.samples, args.parse_float_at)
        pprint.pprint(results)
    finally:
        repository.checkout_master()

    plot = Plot(commands, revisions, results)
    plot.plot(output, args.ylabel)


if __name__ == '__main__':
    main()
