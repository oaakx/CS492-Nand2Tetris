#
# VM to Hack Assembly Translator
#

import sys, os
import re

unops = { 'neg': '-',
          'not': '!'}

binops = {  'add': '+',
            'sub': '-',
            'eq' : '-',
            'gt' : '-',
            'lt' : '-',
            'and': '&',
            'or' : '|'}
# comparison operators
cmpops = {  'eq': 'JEQ',
            'gt': 'JGT',
            'lt': 'JLT'}
# "relative" segments
relsegs = { 'local'   : 'LCL',
            'argument': 'ARG',
            'this'    : 'THIS',
            'that'    : 'THAT'}

class VMTranslator():
  def __init__(self, vmfile):
    self.vmfile = vmfile
    self.vmclass = os.path.basename(vmfile)[:-len('.vm')] # only filename - '.vm'
    self.curfuncname = 'Oaakx.space'
    self.nretaddr = 0
    self.ncmpop = 0

  # ------------------------------------------------------------------

  def translate(self):
    "Translate one .vm file."
    sys.stderr.write("Translating %s ...\n" % self.vmfile)
    self.inp = open(self.vmfile)
    # start translating
    asmout = ''
    asmout += self.translate_init()
    for line in self.inp:
      line = self.strip_comment(line)
      line = line.strip()
      if line == '':
        continue
      tokens = re.split("\s+", line)

      print(tokens)
      
      if tokens[0] in unops:
        asmout += self.translate_unop(tokens[0])
      elif tokens[0] in binops:
        asmout += self.translate_binop(tokens[0])
      elif tokens[0] == 'push':
        asmout += self.translate_push(tokens[1], int(tokens[2]))
      elif tokens[0] == 'pop':
        asmout += self.translate_pop(tokens[1], int(tokens[2]))
      elif tokens[0] == 'function':
        asmout += self.translate_function(tokens[1], int(tokens[2]))
      elif tokens[0] == 'return':
        asmout += self.translate_return()
      elif tokens[0] == 'call':
        asmout += self.translate_call(tokens[1], int(tokens[2]))
      elif tokens[0] == 'label':
        asmout += self.translate_label(tokens[1])
      elif tokens[0] == 'goto':
        asmout += self.translate_goto(tokens[1])
      elif tokens[0] == 'if-goto':
        asmout += self.translate_ifgoto(tokens[1])
      else:
        print('push you 0\ncall suffer_eternal_pain 1\n')
        return 'translation error :('
    self.inp.close()
    return asmout

  def strip_comment(self, line):
    idx = line.find("//")
    return line if idx == -1 else line[:idx]

  def translate_init(self):
    out = ''
    # SP=256
    out += '@256\n'
    out += 'D=A\n'
    out += '@SP\n'
    out += 'M=D\n'
    # call Sys.init
    # out += '@Sys.init\n'
    # out += '0; JMP\n'
    out += self.translate_call('Sys.init', 0)
    return out

  def translate_call(self, funcname, nargs):
    out = ''
    # push return-address
    retaddr = self._next_retaddr()
    out += '@%s\n' % retaddr
    out += 'D=A\n'
    out += self._pushD()
    # push LCL
    out += '@LCL\n'
    out += 'D=M\n'
    out += self._pushD()
    # push ARG
    out += '@ARG\n'
    out += 'D=M\n'
    out += self._pushD()
    # push THIS
    out += '@THIS\n'
    out += 'D=M\n'
    out += self._pushD()
    # push THAT
    out += '@THAT\n'
    out += 'D=M\n'
    out += self._pushD()
    # ARG = SP - (nargs+5)
    out += '@%s\n' % str(nargs+5)
    out += 'D=A\n'
    out += '@SP\n'
    out += 'D=M-D\n'
    out += '@ARG\n'
    out += 'M=D\n'
    # LCL = SP
    out += '@SP\n'
    out += 'D=M\n'
    out += '@LCL\n'
    out += 'M=D\n'
    # goto funcname // Board.rotate
    out += '@%s\n' % funcname
    out += '0; JMP\n'
    # (return-address)
    out += '(' + retaddr + ')\n'
    return out

  def translate_function(self, funcname, nlocals):
    # update current function name
    self.curfuncname = funcname
    out = ''
    # (funcname)
    out += '(' + funcname + ')\n'
    # push 0 // nlocals times
    # TODO: optimize this (first, by 1 operation. then (maybe?) mass init locals to 0, and increase SP at once)
    out += 'D=0\n'
    for i in range(nlocals):
      out += self._pushD()
    return out

  def translate_return(self):
    out = ''
    # store retaddr in R13
    out += '@5\n'
    out += 'D=A\n'
    out += '@LCL\n'
    out += 'A=M-D\n'
    out += 'D=M\n'
    out += '@R13\n'
    out += 'M=D\n'
    # reposition retval
    out += '@SP\n'
    out += 'A=M-1\n'
    out += 'D=M\n'
    out += '@ARG\n'
    out += 'A=M\n'
    out += 'M=D\n'
    # SP = ARG + 1
    out += '@ARG\n'
    out += 'D=M+1\n'
    out += '@SP\n'
    out += 'M=D\n'
    # THAT = *(LCL-1) # TODO: optimize this. just remove first 2 operations and use constant 1 for D.
    out += '@1\n'
    out += 'D=A\n'
    out += '@LCL\n'
    out += 'A=M-D\n'
    out += 'D=M\n'
    out += '@THAT\n'
    out += 'M=D\n'
    # THIS = *(LCL-2)
    out += '@2\n'
    out += 'D=A\n'
    out += '@LCL\n'
    out += 'A=M-D\n'
    out += 'D=M\n'
    out += '@THIS\n'
    out += 'M=D\n'
    # ARG = *(LCL-3)
    out += '@3\n'
    out += 'D=A\n'
    out += '@LCL\n'
    out += 'A=M-D\n'
    out += 'D=M\n'
    out += '@ARG\n'
    out += 'M=D\n'
    # LCL = *(LCL-4)
    out += '@4\n'
    out += 'D=A\n'
    out += '@LCL\n'
    out += 'A=M-D\n'
    out += 'D=M\n'
    out += '@LCL\n'
    out += 'M=D\n'
    # goto retaddr
    out += '@R13\n'
    out += 'A=M\n'
    out += '0; JMP\n'
    return out

  def translate_binop(self, opername):
    out = ''
    out += '@SP\n'
    out += 'AM=M-1\n'
    out += 'D=M\n'
    out += '@SP\n'
    out += 'A=M-1\n'
    out += 'MD=M%sD\n' % binops[opername]
    if opername in cmpops:
      cmpoplabel = self._next_cmpoplabel()
      out += '@%s\n' % cmpoplabel
      out += 'D; %s\n' % cmpops[opername]
      out += '@SP\n'
      out += 'A=M-1\n'
      out += 'M=0\n'
      out += '@%s\n' % (cmpoplabel + '_END')
      out += '0; JMP\n'
      out += '(%s)\n' % cmpoplabel
      out += '@SP\n'
      out += 'A=M-1\n'
      out += 'M=-1\n'
      out += '(%s)\n' % (cmpoplabel + '_END')
    return out

  def translate_unop(self, opername):
    out = ''
    out += '@SP\n'
    out += 'A=M-1\n'
    out += 'M=%sM\n' % unops[opername]
    return out

  def translate_push(self, segment, index):
    out = ''
    if segment == 'constant':
      out += '@%s\n' % str(index)
      out += 'D=A\n'
    elif segment == 'static':
      out += '@%s\n' % self._static_seg(index)
      out += 'D=M\n'
    elif segment == 'pointer':
      out += '@%s\n' % str(index + 3)
      out += 'D=M\n'
    elif segment == 'temp':
      out += '@%s\n' % str(index + 5)
      out += 'D=M\n'
    else: # local, argument, this, that
      out += '@%s\n' % str(index)
      out += 'D=A\n'
      out += '@%s\n' % relsegs[segment]
      out += 'A=M+D\n'
      out += 'D=M\n'
    out += self._pushD()
    return out

  def translate_pop(self, segment, index):
    out = ''

    if segment in relsegs: # local, argument, this, that
      out += '@%s\n' % str(index)
      out += 'D=A\n'
      out += '@%s\n' % relsegs[segment]
      out += 'D=M+D\n'
      out += '@R13\n'
      out += 'M=D\n'
      out += '@SP\n'
      out += 'AM=M-1\n'
      out += 'D=M\n'
      out += '@R13\n'
      out += 'A=M\n'
      out += 'M=D\n'
    else:
      out += '@SP\n'
      out += 'AM=M-1\n'
      out += 'D=M\n'
      if segment == 'constant':
        raise Exception('Can not pop into constant segment')
      elif segment == 'static':
        out += '@%s\n' % self._static_seg(index)
        out += 'M=D\n'
      elif segment == 'pointer':
        out += '@%s\n' % str(index + 3)
        out += 'M=D\n'
      elif segment == 'temp':
        out += '@%s\n' % str(index + 5)
        out += 'M=D\n'
    
    return out  

  def translate_label(self, label):
    out = '(%s.%s)\n' % (self.curfuncname, label)
    return out

  def translate_goto(self, label):
    out = ''
    out += '@%s.%s\n' % (self.curfuncname, label)
    out += '0; JMP\n'
    return out

  def translate_ifgoto(self, label):
    out = ''
    out += '@SP\n'
    out += 'AM=M-1\n'
    out += 'D=M\n'
    out += '@%s.%s\n' % (self.curfuncname, label)
    out += 'D; JNE\n'
    return out

  def _pushD(self):
    out = ''
    out += '@SP\n'
    out += 'A=M\n'
    out += 'M=D\n'
    out += '@SP\n'
    out += 'M=M+1\n'
    return out

  def _next_retaddr(self):
    retaddr = 'RETURN.' + self.vmclass + str(self.nretaddr)
    self.nretaddr += 1
    return retaddr

  def _next_cmpoplabel(self):
    cmpoplabel = 'CMPOPER.' + self.vmclass + str(self.ncmpop)
    self.ncmpop += 1
    return cmpoplabel

  def _static_seg(self, index):
    return '%s.%s' % (self.vmclass, str(index))

  # ------------------------------------------------------------------

  
# --------------------------------------------------------------------

def main():
  if len(sys.argv) != 2:
    sys.stderr.write("Usage: python3 vmtranslator.py <file.jack>\n")
    sys.stderr.write("    or python3 vmtranslator.py <directory>\n")    
    sys.exit(9)

  path = sys.argv[-1]
  asmfiles = []
  if path.endswith(".vm"):
    asmfiles.append(path)
  else:
    for fname in os.listdir(path):
      if fname.endswith(".vm"):
        asmfiles.append(os.path.join(path, fname))

  print(asmfiles)

  output = ''
  for file in asmfiles:
    output += VMTranslator(file).translate()

  folder = path if os.path.isdir(path) and path[-1] not in '\\/' else os.path.dirname(path)

  with open(os.path.join(folder, os.path.basename(folder)+".asm"), "w") as asmfile:
    asmfile.write(output)

# --------------------------------------------------------------------

if __name__ == "__main__":
  main()

# --------------------------------------------------------------------
