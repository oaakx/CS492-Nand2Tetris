"""
Silap Aliyev (!c) 2017 <chief_pythonista_in_office@oaakx.space>
"""

import re
import sys

# TODO: Add some error handling

class SymbolTable:
    """
    Symbol Table for labels and variables
    """

    def __init__(self):
        self.table = {
            'SP': 0,
            'LCL': 1,
            'ARG': 2,
            'THIS': 3,
            'THAT': 4,
            'R0': 0,
            'R1': 1,
            'R2': 2,
            'R3': 3,
            'R4': 4,
            'R5': 5,
            'R6': 6,
            'R7': 7,
            'R8': 8,
            'R9': 9,
            'R10': 10,
            'R11': 11,
            'R12': 12,
            'R13': 13,
            'R14': 14,
            'R15': 15,
            'SCREEN': 16384,
            'KBD': 24576
        }

        self.next_rom = 0
        self.next_ram = 16

    def add(self, key, val):
        self.table[key] = val

    def get(self, key):
        return self.table[key]

    def has(self, key):
        return key in self.table


class Assembler:
    """
    Assembler for Nand2Tetris Hack language
    """

    def __init__(self):
        self.line_num = 0
        self.inp_lines = []
        self.symtable = SymbolTable()
        self.lpat = re.compile(r'\(([a-zA-Z_.$:][a-zA-Z0-9_.$:]*)\)')
        self.apat = re.compile(r'@([0-9\-+]+|[a-zA-Z_.$:][a-zA-Z0-9_.$:]*)')
        self.cpat = re.compile(r'(?:([nulAMD]+)=)?([01\-!+&|AMD]+)(?:;([nulJGTEQLNMP]+))?')
        self.cpat_unsafe = re.compile(r'(?:([^=]*)=)?([^;]+)(?:;(.*))?')

    def assemble(self, inp):
        self.inp_lines = inp.split('\n')
        lines = list(map(self.clean_line, self.inp_lines))

        self.build_symbol_table(lines)
        out = ''

        for line in lines:
            self.line_num += 1
            aa = self.parsea(line)
            cc = self.parsec(line)

            if aa:
                out += aa + '\n'
            elif cc:
                out += cc + '\n'
            elif line != '' and not self.lpat.match(line):
                self.parse_error()

        return out

    def build_symbol_table(self, lines):
        for line in lines:
            if self.lpat.match(line):
                lmatch = self.lpat.search(line)
                key = lmatch.group(1)
                self.symtable.add(key, self.symtable.next_rom)

            if self.apat.match(line) or self.cpat.match(line):
                self.symtable.next_rom += 1

    def parsea(self, line):
        if not self.apat.match(line):
            return False

        amatch = self.apat.search(line)
        symbol = amatch.group(1)
        vbits = ''

        if self.is_int(symbol):
            addr = int(symbol)

            if addr < 0 or 32768 <= addr:
                self.misc_error("value in A-instruction should be in range 0..32767")

            vbits = self.formata(addr)
        elif self.symtable.has(symbol):
            addr = self.symtable.get(symbol)
            vbits = self.formata(addr)
        else:
            self.symtable.add(symbol, self.symtable.next_ram)
            self.symtable.next_ram += 1
            addr = self.symtable.get(symbol)
            vbits = self.formata(addr)

        return '0' + vbits

    @staticmethod
    def is_int(n):
        try:
            int(n)
            return True
        except ValueError:
            return False

    def formata(self, dec):
        return '{0:015b}'.format(dec)

    def parsec(self, line):
        # Check if at least comp section matches
        if not self.cpat.match(line):
            return False

        # If comp section matches, fetch parts unsafely
        # to detect errors in dest and jump sections
        cmatch = self.cpat_unsafe.search(line)

        dest = cmatch.group(1)
        comp = cmatch.group(2)
        jump = cmatch.group(3)

        return '111' + self.parsec_comp(comp) + self.parsec_dest(dest) + self.parsec_jump(jump)

    def parsec_comp(self, comp):
        if comp == '0': # a = 0
            return '0101010'
        elif comp == '1':
            return '0111111'
        elif comp == '-1':
            return '0111010'
        elif comp == 'D':
            return '0001100'
        elif comp == 'A':
            return '0110000'
        elif comp == '!D':
            return '0001101'
        elif comp == '!A':
            return '0110001'
        elif comp == '-D':
            return '0001111'
        elif comp == '-A':
            return '0110011'
        elif comp == 'D+1':
            return '0011111'
        elif comp == 'A+1':
            return '0110111'
        elif comp == 'D-1':
            return '0001110'
        elif comp == 'A-1':
            return '0110010'
        elif comp == 'D+A':
            return '0000010'
        elif comp == 'D-A':
            return '0010011'
        elif comp == 'A-D':
            return '0000111'
        elif comp == 'D&A':
            return '0000000'
        elif comp == 'D|A':
            return '0010101'
        elif comp == 'M': # a = 1
            return '1110000'
        elif comp == '!M':
            return '1110001'
        elif comp == '-M':
            return '1110011'
        elif comp == 'M+1':
            return '1110111'
        elif comp == 'M-1':
            return '1110010'
        elif comp == 'D+M':
            return '1000010'
        elif comp == 'D-M':
            return '1010011'
        elif comp == 'M-D':
            return '1000111'
        elif comp == 'D&M':
            return '1000000'
        elif comp == 'D|M':
            return '1010101'
        else:
            self.parse_error()

    def parsec_dest(self, dest):
        if dest == 'null' or dest is None:
            return '000'
        elif dest == 'M':
            return '001'
        elif dest == 'D':
            return '010'
        elif dest == 'MD':
            return '011'
        elif dest == 'A':
            return '100'
        elif dest == 'AM':
            return '101'
        elif dest == 'AD':
            return '110'
        elif dest == 'AMD':
            return '111'
        else:
            self.parse_error()

    def parsec_jump(self, jump):
        if jump == 'null' or jump is None:
            return '000'
        elif jump == 'JGT':
            return '001'
        elif jump == 'JEQ':
            return '010'
        elif jump == 'JGE':
            return '011'
        elif jump == 'JLT':
            return '100'
        elif jump == 'JNE':
            return '101'
        elif jump == 'JLE':
            return '110'
        elif jump == 'JMP':
            return '111'
        else:
            self.parse_error()

    def clean_line(self, line):
        line = self.strip_comment(line)
        line = re.sub(r'\s+', '', line)
        return line

    @staticmethod
    def strip_comment(line):
        return line.split('//')[0]

    def parse_error(self):
        print("\nParsing error: on line " + str(self.line_num) + '\n' + self.inp_lines[self.line_num - 1] + '\n^')
        sys.exit()

    def misc_error(self, reason):
        print("\nError (" + reason + "): on line " + str(self.line_num)
              + '\n' + self.inp_lines[self.line_num - 1] + '\n^')
        sys.exit()

    @staticmethod
    def print_usage():
        print("Usage: python assembler.py <program.asm>")


if __name__ == "__main__":

    # Check number of arguments
    if len(sys.argv) != 2 or sys.argv[1] == '/?'or sys.argv[1] == '-h' or sys.argv[1] == '--help':
        Assembler.print_usage()
        sys.exit()

    inp_file = sys.argv[1]

    # Check input file extension
    if inp_file[-4:] != '.asm':
        print("Error: Input file doesn't seem to be *.asm file")
        Assembler.print_usage()
        sys.exit()

    out_file = inp_file[:-4] + '.hack'

    with open(inp_file, 'r') as f:
        asm_code = f.read()

    print("Assembling: " + inp_file)
    print("Output file: " + out_file)

    asm = Assembler()
    hack_code = asm.assemble(asm_code)

    # print(hack_code)
    print("Assembling completed successfully")

    with open(out_file, "w") as f:
        f.write(hack_code)
