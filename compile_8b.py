#!/usr/bin/env python3

# DW  word
# HLT
# ADD Rd Rs Rt
# LD  Rd addr
# ST  Rd addr

import sys


TOKEN_NAMES = ['HLT', 'ADD', 'LD', 'ST', 'DW']

TOKEN_CODES = {
    'HLT': 0,
    'ADD': 1,
    'LD' : 2,
    'ST' : 3
}

TOKEN_ARG_COUNT = {
    'HLT': 0,
    'ADD': 3,
    'LD': 2,
    'ST': 2,
    'DW': 1
}

REGISTER = ['R0', 'R1', 'R2', 'R3']


class AssemblyError(Exception):
    pass


class Token:
    def __init__(self, addr, name, args):
        self.addr = addr
        self.name = name
        self.args = args
        if len(self.args) != TOKEN_ARG_COUNT[self.name]:
            raise AssemblyError('Invalid number of arguments for %s')

    def encode(self, labels):
        if self.name == 'HLT':
            return TOKEN_CODES[self.name]
        
        if self.name == 'ADD':
            Rd = REGISTER.index(self.args[0].upper())
            Rs = REGISTER.index(self.args[1].upper())
            Rt = REGISTER.index(self.args[2].upper())
            return (TOKEN_CODES[self.name] << 6) | (Rd << 4) | (Rs << 2) | (Rt)
        
        if self.name == 'LD' or self.name == 'ST':
            Rd = REGISTER.index(self.args[0].upper())
            if len(args[1]) > 2 and args[1][:2] == '0x':
                addr = int(args[1], base=16)
            elif len(args[1]) > 2 and args[1][:2] == '0b':
                addr = int(args[1], base=2)
            elif args[1] in labels:
                addr = labels[args[1]].addr
            else:
                try:
                    addr = int(args[1], base=10)
                except ValueError:
                    raise AssemblyError('Invalid address!')
            return (TOKEN_CODES[self.name] << 6) | (Rd << 4) | (addr)


class Assembler:
    def __init__(self):
        self.labels = None

    def assemble(self, inputFile, outputFile):
        self.labels = dict()

        lines = None
        with open(inputFile) as file:
            lines = file.readlines()
        
        if lines is None:
            raise ValueError('Failed to load File!')

        params = parseLines(lines)
        tokens = parseParams(params)

        machine_code = list()
        for token in tokens:
            machine_code.append(token.encode(self.labels))

        with open(outputFile, 'w') as file:
            file.write('v2.0 raw\n')
            for token in tokens:
                file.write('%x\n' % token.encode(self.labels))

        labels = None

    def parseLines(self, lines):
        params = list()
        for line in lines:
            line = line.strip()
            if line == '' or line[0] == '#':
                continue
            
            comment = line.index('#')
            if comment != -1:
                line = line[:comment]
            
            params = line.split()
        
        return params

    def parseParams(self, params):
        addr = 0
        label = None
        tokens = list()

        for p in params:
            if len(p) == 0:
                print('empty p')
                continue

            token = None
            if p[0] in TOKEN_NAMES:
                token = Token(addr, p[0], p[1:])
                tokens.append(token)
                addr += 1
                if label is not None:
                    self.labels[label] = token
                    label = None

            elif len(p) >= 2 and p[1] in TOKEN_NAMES:
                if label is not None:
                    raise AssemblyError('Multiple Labels!')
                token = Token(addr, p[1], p[2:])
                tokens.append(token)
                addr += 1
                self.labels[p[0]] = token

            elif len(p[0]) > 1 and p[0][-1] == ':'
                if label is not None:
                    raise AssemblyError('Multiple Labels!')
                label = p[0][:-1]

            else:
                raise AssemblyError('Invalid Token!')
        
        return tokens



if len(sys.argv) != 3 and len(sys.argv) != 2:
    print('Usage:')
    print('./compile_8b.py <input_file>')
    print('./compile_8b.py <input_file> <output_file>')
    exit(0)

INPUT_FILE = sys.argv[1]
if INPUT_FILE[-5:] != '.toby':
    raise ValueError('Invalid input file type!')

if len(sys.argv) == 2:
    OUTPUT_FILE = INPUT_FILE[:-4] + 'lsim'
else:
    if OUTPUT_FILE[-5:] != '.lsim':
        #TODO
    OUTPUT_FILE = sys.argv[2]

lines = None
with open(INPUT_FILE) as file:
    lines = file.readlines()

if lines is None:
    print('Failed to load file!')
    exit(0)

# preprocess lines
tokens = list()
for line in lines:
    line = line.strip()
    if line != '' and line[0] != '#':
        params = line.split(' ')
        tokens.append(Token(params[0], params[1:]))

REGISTER = ['R0', 'R1', 'R2', 'R3']

def compileToken(token: Token, label=False):
    if token.name.upper() == 'HLT':
        assert(len(token.args) == 0)
        return 0

    elif token.name.upper() == 'ADD':
        assert(len(token) == 4)
        Rd = REGISTER.index(token[1].upper())
        Rs = REGISTER.index(token[2].upper())
        Rt = REGISTER.index(token[3].upper())
        return (1 << 6) | (Rd << 4) | (Rs << 2) | Rt

    elif token.name.upper() == 'LD':
        assert(len(token) == 3)
        Rd = REGISTER.index(token[1].upper())
        addr = int(token[2], base=0)
        return (2 << 6) | (Rd << 4) | addr

    elif token.name.upper() == 'ST':
        assert(len(token) == 3)
        Rd = REGISTER.index(token[1].upper())
        addr = int(token[2], base=0)
        return (3 << 6) | (Rd << 4) | addr
        
    elif token.name.upper() == 'DW':
        assert(len(token) == 2)
        word = int(token[1], base=0)
        return word
    
    print(token)
    assert(False)

# code = list()
for token in tokens:
    # code.append(compileToken(token))
    print(token, hex(compileToken(token)))

# with open(OUTPUT_FILE, 'w') as file:
#     file.write('v2.0 raw\n')
#     i = 0
#     while i < len(code):
#         file.write(' '.join('{:x}'.format(x) for x in code[i:i+8]))
#         file.write('\n')
#         i += 8

# output:
# v2.0 raw
# 3 a 3 4 5 6 7 8
# 9 a b c d e f

# some_label:
#         LD R1 VAL_A
#         LD R2 VAL_B
#         ADD R3 R1 R2
#         ST R3 VAL_A
#         ADD R3 R1 R3
#         ST R3 VAL_B
#         ADD R3 R1 R3
#         ST R3 VAL_C
#         ADD R3 R1 R3
#         ST R3 VAL_D
#         HLT

# VAL_A   DW 0x3
# VAL_B   DW 0xA
# VAL_C   DW 0x0
# VAL_D   DW 0x0