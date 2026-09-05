from scipy.stats import binom


def threshold(nbits, fpr=0.01):
    for tau in range(nbits + 1):
        if binom.sf(tau - 1, nbits, 0.5) <= fpr:
            return tau
    return nbits + 1


def realised_fpr(nbits, tau):
    return float(binom.sf(tau - 1, nbits, 0.5))


def matched_filter(scores, bits):
    signs = 2.0 * bits - 1.0
    return float((signs * scores).sum())


def matches(scores, bits):
    return int(((scores > 0) == (bits > 0)).sum())
