import re


def parse_a(line):
    p = re.compile(r'^\S*@([0-9])*$')
    m = p.match(line)

    if not m:
        raise Exception("Invalid A instruction")

    g = m.groups()

    imm = g[0]
    imm = int(imm)

    return imm


def parse_c():
    pass
