"""
Joseph Fox-Rabinovitz - 01 Apr 2016
"""

import timeit, platform
import numpy, pandas, seaborn
from matplotlib import pyplot

#
# Global info
#

hostname = platform.uname().node
outputFile = __file__.replace('.py', '_{hostname}.csv'.format(
                                                hostname=hostname))

#
# Set up benchmark properties
#

max_pow = 9

array_types = {
    'sorted': lambda x: x.copy(),
    'reversed': lambda x: x.copy()[::-1],
    'random': lambda x: numpy.random.shuffle(x.copy()),
    # See http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.14.5196&rep=rep1&type=pdf
    'median-killer': lambda x: numpy.concatenate((numpy.stack((x[0:len(x)//2:2], x[len(x)//2::2])).T.ravel(), x[1::2]))
}

array_lengths = numpy.zeros(5 + (max_pow - 1) * 9, dtype=numpy.int_)
array_lengths[0:5] = numpy.arange(2, 11, 2)
for p in range(max_pow - 1):
    array_lengths[5 + p * 9: 5 + (p + 1) * 9] = numpy.arange(2, 11) * 10**(p + 1)

sort_kinds = ['quicksort', 'mergesort', 'heapsort']

# TODO: Eventually add loop over dtypes

#
# Set up output data frame
#

index = pandas.MultiIndex.from_product(([hostname], sort_kinds, array_types.keys(), array_lengths),
                                       names=['host', 'sort', 'type', 'length'])

# TODO: Eventually, try to read df from `outputFile`, only fill in missing elements

# This is really just a series since there is only one column. A
# DataFrame is preferred since it names the column, saving a step later
# on. It also makes future expansion easier.
df = pandas.DataFrame(index=index, columns=['time'])

#
# Perform benchmark
#

try:
    for length in array_lengths:
        for kind in sort_kinds:
            for atype, handler in array_types.items():
                print('{kind:10}, {atype:15}, {length:10}, '.format(
                        kind=kind, atype=atype, length=length), end='')
                times = timeit.repeat('numpy.sort(x, axis=None, kind=kind)',
                      setup='import numpy; numpy.random.seed(0); '
                            'x = handler(numpy.arange(length, '
                                                'dtype=numpy.float_))',
                      repeat=5, number=1,
                      globals={'length': length, 'kind': kind,
                               'handler': handler})
                df['time'][hostname, kind, atype, length] = min(times)
                print(min(times))
except KeyboardInterrupt:
    print("\nPremaure termination. No worries.")

#
# Save DF to CSV
#
df.to_csv(outputFile)

#
# Plot what you got
#
# x: length
# y: time
# color: kind
# style: atype
#

seaborn.factorplot(x='length', y='time', hue='sort', row='type', data=df.reset_index(), ci=None)
#seaborn.pointplot(x='length', y='time', hue='sort', data=df.reset_index(), ci=None)
pyplot.show()

