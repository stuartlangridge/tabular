#!/usr/bin/env python3
"Parse ASCII tabular output from commands such as docker ps or netstat -tanp"
import argparse
import sys
import re
import json
from collections import OrderedDict


def parse(filename, skip=0):
    if filename == "-":
        fp = sys.stdin
    else:
        fp = open(filename, encoding="utf-8")
    lines = fp.readlines()
    fp.close()
    if skip:
        lines = lines[skip:]
    return parse_lines(lines)


def parse_lines(lines):
    left_boundaries = [0] + [
        x.span()[0] + 1 for x in re.finditer(r" [^ ]", lines[0])]
    right_boundaries = [
        x.span()[0] + 1 for x in re.finditer(r"[^ ] ", lines[0])]
    # Columns might be left-justified, or right-justified
    # Column headers may contain a space, or not
    # So, check each row, and then look at all the left boundaries: if there is
    #   a space before the left boundary and a character after it, then this
    #   is probably the actual beginning of a left-justified column
    # And look at all the right boundaries: if there is a character before the
    #   right boundary and a space after it, then this is probably the actual
    #   end of a right-justified column
    lb_checked = dict([(lb, []) for lb in left_boundaries])
    rb_checked = dict([(rb, []) for rb in right_boundaries])
    for line in lines[1:]:  # skip the headers
        if not line:
            continue
        for lb in lb_checked:
            if lb == 0:
                lb_checked[lb].append(line[lb] != " ")
            elif lb > len(line):
                lb_checked[lb].append(False)
            else:
                lb_checked[lb].append(line[lb] != " " and line[lb - 1] == " ")
        for rb in rb_checked:
            if rb > len(line):
                rb_checked[rb].append(False)
            else:
                rb_checked[rb].append(line[rb - 1] != " " and line[rb] == " ")
    valid_lb = [x[0] for x in lb_checked.items() if all(x[1])]
    valid_rb = [x[0] for x in rb_checked.items() if all(x[1])]
    position = 0
    columns = []
    while valid_lb or valid_rb:
        if valid_lb and valid_rb:
            if valid_lb[0] < valid_rb[0]:
                nxt = (valid_lb.pop(0), "l")
            else:
                nxt = (valid_rb.pop(0), "r")
        elif valid_lb:
            nxt = (valid_lb.pop(0), "l")
        else:
            nxt = (valid_rb.pop(0), "r")
        columns.append((position, nxt[0], nxt[1]))
        position = nxt[0]
    columns.append((columns[-1][1], None, "l"))

    # split right columns where there's something on the left in all rows
    # because that's actually a left column followed by a right column
    ncolumns = []
    for cs, ce, cj in columns:
        if cj == "r":
            try:
                start_characters = [
                    line[cs] != " " for line in lines if line.strip()]
            except IndexError:
                start_characters = [False]
            if all(start_characters):
                # this right column has characters at the left in every row,
                # so it's probably two columns. Find a place to split it
                found = False
                for ncs in range(cs, ce):
                    is_spaces = [line[ncs] == " "
                                 for line in lines if line.strip()]
                    if all(is_spaces):
                        ncolumns.append((cs, ncs, "l"))
                        ncolumns.append((ncs, ce, "r"))
                        found = True
                        break
                if not found:
                    # no place to split
                    ncolumns.append((cs, ce, cj))
            else:
                ncolumns.append((cs, ce, cj))
        else:
            ncolumns.append((cs, ce, cj))
    columns = ncolumns

    headers = []
    for start, end, justification in columns:
        headers.append(lines[0][start:end].strip())
    data = []
    for line in lines[1:]:
        linedata = []
        for start, end, justification in columns:
            column = line[start:end].strip()
            linedata.append(column)
        valid_linedata = [x for x in zip(headers, linedata) if x[0] and x[1]]
        if valid_linedata:
            data.append(OrderedDict(valid_linedata))
    return data


def output_ini(data):
    for row in data:
        for k, v in row.items():
            print("{}={}".format(k, v))
        print()


def output_json(data):
    print(json.dumps(data, indent=2))


def output(data, dformat):
    if dformat == "ini":
        output_ini(data)
    elif dformat == "json":
        output_json(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Parse ASCII tabular data, such as command output')
    parser.add_argument('filename', default='-', nargs='?',
                        help='file to parse or - (default) for stdin')
    parser.add_argument('--skip', type=int, default=0,
                        help='lines to skip before table header')
    parser.add_argument('--format', default="ini", choices=["ini", "json"],
                        help='output data format')
    parser.add_argument('--debug', action="store_true",
                        help='show unfriendly tracebacks, not friendly errors')
    args = parser.parse_args()
    try:
        data = parse(args.filename, args.skip)
        output(data, args.format)
    except IndexError:
        if args.debug:
            raise
        else:
            print("That data does not seem to be tabular, so I am giving up.",
                  file=sys.stderr)
