#!/usr/bin/python

import re

class ParseError(Exception): pass

class Parser(object):
    grid_re = re.compile(r'^([^\n\r\t:]*)$')
    key_re = re.compile(r'^[^\n\r\t:]:.*$')
    name_re = re.compile(r' *([a-zA-Z_][a-zA-Z0-9_]*) *')
    str_re = re.compile(r'("(?:[^\n\r\t"\\]|\\[nrt"\\])*")')

    def __init__(self, builder):
        self.name = None
        self.grid = []
        self.keys = {'.': {}, ' ': {}}
        self.builder = builder

    def parsefile(self, f):
        self.name = f.next().strip()

        ingrid = True
        for line in f:
            m = ingrid and self.grid_re.match(line)
            if m:
                self.grid.append(m.group(1))
            else:
                ingrid = False
                self.parsekey(line)

        self.width = max([len(s) for s in self.grid])
        self.height = len(self.grid)

        return self.evaluate()

    def parsekey(self, line):
        self.dieunless(self.key_re.match(line), line)
        c = line[0]
        data = line[2:]

        attrs = {}
        curr = None
        mode = 'start'
        i = 0
        while i < len(data):
            if data[i] == ' ' or data[i] == '\r' or data[i] == '\n':
                i += 1
            elif mode == 'name' or mode == 'start':
                m = self.name_re.match(data, i)
                self.dieunless(m, data[i:])
                curr = m.group(1)
                mode = 'equals'
                i += len(curr)
            elif mode == 'equals':
                self.dieunless(data[i] == '=', data[i:])
                mode = 'value'
                i += 1
            elif mode == 'value':
                m = self.str_re.match(data, i)
                self.dieunless(m, data[i:])
                s = m.group(1)
                attrs[curr] = self.parsestr(s)
                i += len(s)
                mode = 'ok'
            elif mode == 'ok':
                self.dieunless(data[i] == ',', data[i:])
                i += 1
                mode = 'name'
            else:
                self.dieunless(False, data[i:])
        self.keys[c] = attrs

    def parsestr(self, s):
        s = s[1:-1].replace('\\n', '\n').replace('\\r', '\r')
        s = s.replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
        return s

    def evaluate(self):
        self.builder.prepare(self.name, self.width, self.height)
        for y in range(0, self.height):
            for x in range(0, self.width):
                c = self.grid[y][x]
                self.builder.place(x, y, c, self.keys[c])
        return self.builder.finalize()

    def dieunless(self, b, msg):
        if not b:
            raise ParseError(msg)

class Builder(object):
    def alloc(self, width, height, f):
        return [[f() for x in range(0, width)] for y in range(0, height)]
    def prepare(self, name, width, height):
        raise Exception("unimplemented")
    def place(self, x, y, c, attrs):
        raise Exception("unimplemented")
    def finalize(self):
        raise Exception("unimplemented")

class TestBuilder(Builder):
    def prepare(self, name, width, height):
        self.level = self.alloc(width, height, lambda: ' ')
    def place(self, x, y, c, attrs):
        self.level[y][x] = c
    def finalize(self):
        return '\n'.join([''.join(row) for row in self.level])
