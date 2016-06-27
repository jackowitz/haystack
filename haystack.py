#!/usr/bin/env python
def _build_index(haystack):
    return { k: i for i, k in enumerate(haystack, 1) }

def _match(haystack, needles):
    index = _build_index(haystack)
    for needle in needles:
        try:
            yield (needle, index[needle])
        except KeyError:
            pass

def _invert_match(haystack, needles):
    index = _build_index(haystack)
    for i, needle in enumerate(needles, 1):
        if needle not in index:
            yield (needle, i)

def _complement(haystack, needles):
    reverse_index = list(haystack) # No way around this memory usage.
    index = _build_index(reverse_index)

    for needle in needles:
        try:
            reverse_index[index[needle]-1] = None
        except KeyError:
            pass

    for i, needle in enumerate(reverse_index, 1):
        if needle is not None:
            yield (needle, i)

_modes = {
    'match': _match,
    'invert_match': _invert_match,
    'complement': _complement
}

def search(haystack, needles, mode='match'):
    try:
        for match in _modes[mode](haystack, needles):
            yield match
    except KeyError, e:
        raise ValueError('unrecognized mode: {}'.format(mode))


if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('haystack', type=argparse.FileType('rb'))
    parser.add_argument('needles', type=argparse.FileType('rb'), nargs='?', default=sys.stdin)

    parser.add_argument('-n', '--line-number', action='store_true', default=False, help='''
Each output line is preceded by its relative line number in the haystack, starting at line 1. \
If \033[1m-v\033[0m is specified this line number is instead relative to the set of needles.\
''')

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('-v', '--invert-match', dest='mode', action='store_const', const='invert_match', help='''
Selected lines are those needles not found in the haystack.
''')
    mode.add_argument('-c', '--complement', dest='mode', action='store_const', const='complement', help='''
Selected lines are those remaining in the haystack after all needles are removed.
''')

    args = parser.parse_args()
    fmt = "{1}:{0}" if args.line_number else "{0}"
    try:
        for match in search(args.haystack, args.needles, args.mode or 'match'):
            sys.stdout.write(fmt.format(*match))
    except Exception as e:
        raise SystemExit(e)
