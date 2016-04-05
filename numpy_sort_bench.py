"""
Benchmark of the existing numpy sorting algorithms.

Joseph Fox-Rabinovitz - 01 Apr 2016
"""

import timeit, platform, math, numpy, pandas
from collections import OrderedDict
from matplotlib import pyplot, rc_context, lines

# Modify matplotlib settings
import seaborn

#
# Global info
#

# TODO: -h parameter to set hostname, -n: new, -r: repeats -m: max_pow -o: output_file

__version__ = '0.0.1'
"""
The version of this script.

More important than the content of the script is the number of columns
that are used as the index in the CSV.

TODO: Actually use this when loading the file.
"""

hostname = platform.uname().node
"""
The name of the computer on which this test is running.

This is used to fill in missing data depending on the machine.
"""

output_file = __file__.replace('.py', '_{hostname}.csv'.format(
                                                hostname=hostname))
"""
The name of the output CSV file.

Data loaded from the file will not be re-benched.
"""

recompute = False
"""
`True` to rerun the benchmark from scratch, `False` to continue running
incrementally using saved results.

If `True`, reset the dataframe containing the results instead of loading
it from a file. A pre-existing file will get clobbered in this case.
"""

#
# Set up benchmark properties
#

max_pow = 8
"""
The power of 10 to test array sizes to.

Must be >=1.

Sizes are generated in increments of multiples of powers of 10 up to
this power. For example, for `max_pow = 4`::

    10, 20, ..., 90, 100, 200, ... 900, 1000, 2000, ..., 9000, 10000

The numbers less than 10 are always the even numbers because
median-of-three killer sequences require an even number of elements.
"""

repeats = 5
"""
The number of times to run `timeit` for each combination of inputs.

All repetitions will be recorded. The minimum and standard deviation
will be taken as the time metric and (very) approximate uncertainty.
"""

def shuffled(x):
    numpy.random.shuffle(x)
    return x

array_types = OrderedDict((
    ('random', shuffled),
    ('sorted', lambda x: x),
    ('reversed', lambda x: x[::-1]),
    # See http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.14.5196&rep=rep1&type=pdf
    ('median-killer', lambda x: numpy.concatenate((numpy.stack((x[0:len(x)//2:2], x[len(x)//2::2])).T.ravel(), x[1::2])))
))
"""
A dictionary containing functions to generate the different arrays used
in the benchmark.

The keys are the label for each type. The values are functions that take
a sorted array and return a permutation appropriate for the benchmark.
The return value can be a view (should be whenever possible). The only
function that currently makes a new array is `median-killer`.
"""

array_lengths = numpy.zeros(5 + (max_pow - 1) * 9, dtype=numpy.int_)
"""
An array containing the lengths that will be benchmarked for each type
of input.

The sequence is generated up to `max_pow`::

    2, 4, 6, 8, 10, 20, 30, ..., 90, 100, 200, ..., 9 * 10**(max_pow - 1), 10**max_pow
"""
array_lengths[0:5] = numpy.arange(2, 11, 2)
for p in range(max_pow - 1):
    array_lengths[5 + p * 9: 5 + (p + 1) * 9] = numpy.arange(2, 11) * 10**(p + 1)

# TODO: Add loop over dtypes
array_dtypes = [numpy.float_]
"""
The data-types of arrays to benchmark against.
"""

sort_kinds = {kind: 'numpy.sort(x, axis=None, kind="{0}")'.format(kind)
                    for kind in ('quicksort', 'mergesort', 'heapsort')}
"""
The types of sorting algorithm to benchmark.

Although all the algorithms are currently just calls to `numpy.sort`
with different values of ``kind``, other sorts are supported. The
dictionary values must be strings that run the sorting function on an
input named ``x``. Since this is not a test of any of the algorithms,
the sort can be in-place or not. The return value is ignored either way. 
"""

#
# Set up output data frame
#

# TODO: The number of index columns should depend on the __version__
try:
    df = pandas.read_csv(output_file, index_col=numpy.arange(4))
    data_cols = list(df.columns[2:])
except (OSError, IndexError):
    index = pandas.MultiIndex.from_product(([hostname], sort_kinds, array_types.keys(), array_lengths),
                                           names=['host', 'sort', 'type', 'length'])

    data_cols = ['t{0}'.format(ind) for ind in range(repeats)]
    df = pandas.DataFrame(index=index,
                          columns=['time', 'sigma'] + data_cols,
                          dtype=numpy.float_)

#
# Perform benchmark
#

try:
    for length in array_lengths:
        for dtype in array_dtypes:
            for kind, sort in sort_kinds.items():
                for atype, gen in array_types.items():
                    row = (hostname, kind, atype, length)
                    if pandas.isnull(df.loc[row, 'time']):
                        print('{kind:10} {atype:15} {length:10} {dtype:25}'.format(
                                kind=kind, atype=atype, length=length, dtype=repr(dtype)), end='')
                        times = timeit.repeat(sort,
                              setup='import numpy; numpy.random.seed(0); '
                                    'x = gen(numpy.arange(length, '
                                                         'dtype=dtype))',
                              repeat=repeats, number=1,
                              globals={'length': length, 'kind': kind,
                                       'dtype': dtype, 'gen': gen})
                        time = min(times)
                        sigma = numpy.std(times)

                        df.loc[row, data_cols] = times
                        df.loc[row, 'time'] = time
                        df.loc[row, 'sigma'] = sigma

                        print('{time} +/- {sigma}'.format(time=time, sigma=sigma))
except KeyboardInterrupt:
    print("\nPremaure termination. No worries.")

#
# Save DF to CSV
#
df.to_csv(output_file)

#
# Plot DF
#
# x: length
# y: time
# plot: atype
# color: kind (cycled automatically by mpl)
#

styles = ['solid', 'dashed', 'dashdot', 'dotted']

with rc_context(rc={'interactive': True}):
    # The following is based on http://stackoverflow.com/a/36371454/2988730

    legend1_lines = []

    ax1 = None
    ax1Counter = 1
    ax1Rows = 2
    ax1Cols = int(math.ceil(len(array_types) / 2))

    fig1 = pyplot.figure()
    for dtype in array_dtypes:
        for atype in array_types.keys():
            ax = fig1.add_subplot(ax1Rows, ax1Cols, ax1Counter,
                                  sharex=ax1, sharey=ax1)
            for kind in sort_kinds.keys():
                rows = (hostname, kind, atype)
                ln, = ax.plot(df.loc[rows, 'time'])
                if ax1Counter == 1:
                    ax1 = ax
                    legend1_lines.append(ln)
            ax.set_title(atype)
            ax.set_xlabel('Array Size')
            ax.set_ylabel('Runtime (s)')
            ax1Counter += 1
    if len(array_types) % 2:
        obj = fig1
        loc = 'center'
        anchor = (1.0 - 0.5 / ax1Cols, 0.5 / ax1Rows)
    else:
        obj = ax
        loc = 'center left'
        anchor = (1.1, 1.1)
    obj.legend(legend1_lines, list(sort_kinds.keys()), loc=loc, bbox_to_anchor=anchor)
    fig1.suptitle('Comparison of Algorithm Runtime by Input Type')

    legend2_lines = []

    ax2 = None
    ax2Counter = 1
    ax2Rows = 2
    ax2Cols = int(math.ceil(len(sort_kinds) / 2))

    fig2 = pyplot.figure()
    for dtype in array_dtypes:
        for kind in sort_kinds.keys():
            ax = fig2.add_subplot(ax2Rows, ax2Cols, ax2Counter,
                                  sharex=ax2, sharey=ax2)
            for atype in array_types.keys():
                rows = (hostname, kind, atype)
                ln, = ax.plot(df.loc[rows, 'time'])
                if ax2Counter == 1:
                    ax2 = ax
                    legend2_lines.append(ln)
            ax.set_title(kind)
            ax.set_xlabel('Array Size')
            ax.set_ylabel('Runtime (s)')
            ax2Counter += 1
    if len(sort_kinds) % 2:
        obj = fig2
        loc = 'center'
        anchor = (1.0 - 0.5 / ax2Cols, 0.5 / ax2Rows)
    else:
        obj = ax
        loc = 'center left'
        anchor = (1.1, 1.1)
    obj.legend(legend2_lines, list(array_types.keys()), loc=loc, bbox_to_anchor=anchor)
    fig2.suptitle('Comparison of Runtime for Input Types by Algorithm')

    from IPython import embed
    embed()

