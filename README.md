This project has moved to GitLab: https://gitlab.com/madphysicist/wselect. Please download the latest code and submit issues there rather than GitHub, which will no longer be monitored until this stale clone is deleted.

# wselect
This is a temporary repo containing the development of a set of benchmarks for some new algorithms I am adding to numpy.

The goal is twofold: to benchmark the existing algorithms and to compare them against the new ones.

# Benchmarks

## Sorting
Comparing the speeds of the different sort implementations.

Checking if it is worth adding a C implementation of `_sort2`, which would be equivalent to

    i = np.argsort(a)
    a = a[i]
    w = w[i]

Where `a` is the data and `w` is the weights. I suspect that doing a simultaneous in=place sort would be much faster.

## Selection

Weighted introselect compared to full-sort+cumsum-binary-search implementations in `statsmodels` and `wquantiles`.
