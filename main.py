from ast import parse

from astunparse import unparse

from antigen.filters import get_filters
from antigen.gen import gen_mutations

if __name__ == "__main__":
    tree = parse("a = b'a' + (-2) if 1 > 2 < 3 else ~(a // 2)")

    for mut in gen_mutations(tree):
        if not all(filter_fn(mut) for filter_fn in get_filters()):
            continue
        print(unparse(mut.node))
