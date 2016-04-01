"""
Joseph Fox-Rabinovitz - 01 Apr 2016
"""

import numpy, pandas, timeit

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

index = pandas.MultiIndex.from_product((sort_kinds, array_types.keys(), array_lengths),
                                       names=['sort', 'type', 'length'])

# TODO: Eventually, try to read df from __file__.replace(.py, .csv).

df = pandas.DataFrame(index=index, columns=['time'])

#
# Perform benchmark
#

for length in array_lengths:
    for kind in sort_kinds:
        for atype, handler in array_types.items():
            print('{0}, {1}, {2}'.format(kind, atype, length), end='')
            times = timeit.repeat('numpy.sort(x, kind=kind)',
                  setup='import numpy; numpy.random.seed(0); x = handler(numpy.arange(length, dtype=numpy.float_))',
                  repeat=2, number=1, globals={'length': length, 'kind': kind, 'handler': handler})
            df[kind, atype, length] = min(times)
            print(min(times))

# TODO: Save DF to CSV
