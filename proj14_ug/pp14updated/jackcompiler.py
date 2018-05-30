#
# Compile Jack source to VM
#

import tokens
import jackparser
from parsetree import *
import sys, os

# --------------------------------------------------------------------

binopmap = { "+" : "add",
             "-" : "sub",
             "*" : "call Math.multiply 2",
             "/" : "call Math.divide 2",
             "&" : "and",
             "|" : "or",
             ">" : "gt",
             "<" : "lt",
             "=" : "eq" }
  
# --------------------------------------------------------------------

class JackCompiler():
  def __init__(self, folder):
    self.folder = folder

  # ------------------------------------------------------------------
    
  def compile(self, jclass):
    "Compile one class."
    sys.stderr.write("Compiling %s ...\n" % jclass.name)
    self.out = open("%s/%s.vm" % (self.folder, jclass.name), "w")
    self.out.write("// class %s\n" % jclass.name)
    for sb in jclass.subroutines:
      self.out.write("// %s %s %s.%s\n" %
                     (sb.kind, sb.ret_type, jclass.name, sb.name))
      self.compile_subroutine(jclass, sb)
    self.out.close()

  def compile_subroutine(self, jclass, sb):
    self.out.write("function %s.%s %d\n" %
                   (jclass.name, sb.name, len(sb.locals)))
    # some more work is needed here for methods and constructors
    for st in sb.statements:
      self.compile_statement(jclass, sb, st)

  def compile_statement(self, jclass, sb, st):
    if isinstance(st, LetStatement):
      self.compile_let(jclass, sb, st)
    if isinstance(st, CallExpression):
      self.compile_do(jclass, sb, st)
    if isinstance(st, IfStatement):
      self.compile_if(jclass, sb, st)
    if isinstance(st, WhileStatement):
      self.compile_while(jclass, sb, st)
    if isinstance(st, ReturnStatement):
      self.compile_return(jclass, sb, st)

  # ------------------------------------------------------------------

  #
  # In all compile_xxx methods, jclass is a JackClass object
  # describing the class containing the code being compiled, and
  # sb is a Subroutine object describing the function/method/constructor.
  # 

  # let is of type LetStatement
  def compile_let(self, jclass, sb, let):
    raise NotImplementedError

  # st is of type CallExpression
  def compile_do(self, jclass, sb, st):
    self.compile_call(jclass, sb, st)
    self.out.write("pop temp 0 // void\n")

  # ifst is of type IfStatement
  def compile_if(self, jclass, sb, ifst):
    raise NotImplementedError

  # whilest is of type WhileStatement
  def compile_while(self, jclass, sb, whilest):
    raise NotImplementedError

  # st is of type ReturnStatement
  def compile_return(self, jclass, sb, st):
    if st.expr is None:
      self.out.write("push constant 0\n")
    else:
      self.compile_expression(jclass, sb, st.expr)
    self.out.write("return\n")
    
  # ------------------------------------------------------------------

  #
  # expr is an expression, and can be of type int, str (for string
  # literals), ConstantExpression, VariableExpression, UnaryOperation,
  # BinaryOperation, or CallExpression.
  #
  
  def compile_expression(self, jclass, sb, expr):
    if isinstance(expr, int):
      self.out.write("push constant %d\n" % expr)
    if isinstance(expr, str):
      self.compile_literal(expr)
    if isinstance(expr, ConstantExpression):
      self.compile_constant(expr)
    if isinstance(expr, VariableExpression):
      self.compile_variable(jclass, sb, expr)
    if isinstance(expr, CallExpression):
      self.compile_call(jclass, sb, expr)
    if isinstance(expr, BinaryOperation):
      self.compile_binaryop(jclass, sb, expr)
    if isinstance(expr, UnaryOperation):
      self.compile_unaryop(jclass, sb, expr)

  def compile_constant(self, expr):
    if expr.value == "this":
      self.out.write("push pointer 0 // this\n")
    else:
      self.out.write("push constant 0 // %s\n" % expr.value)
      if expr.value == "true":
        self.out.write("not\n")  # true is -1
    
  def compile_literal(self, text):
    self.out.write('push constant %d // "%s"\n' % (len(text), text))
    self.out.write("call String.new 1\n")
    for ch in text:
      self.out.write("push constant %d // '%s'\n" % (ord(ch), ch))
      self.out.write("call String.appendChar 2\n")

  # var is of type VariableExpression
  def compile_variable(self, jclass, sb, var):
    raise NotImplementedError

  # call is of type CallExpression
  def compile_call(self, jclass, sb, call):
    raise NotImplementedError

  # binop is of type BinaryOperation
  def compile_binaryop(self, jclass, sb, binop):
    raise NotImplementedError

  # unop is of type UnaryOperation
  def compile_unaryop(self, jclass, sb, unop):
    raise NotImplementedError
  
# --------------------------------------------------------------------

def main():
  if len(sys.argv) != 2:
    sys.stderr.write("Usage: python3 jackcompiler.py <file.jack>\n")
    sys.stderr.write("    or python3 jackcompiler.py <directory>\n")    
    sys.exit(9)
  path = sys.argv[-1]
  fnames = []
  if path.endswith(".jack"):
    i = path.rfind("/")
    folder = path[:i]
    fnames.append(path)
  else:
    folder = path
    for fname in os.listdir(path):
      if fname.endswith(".jack"):
        fnames.append(path + "/" + fname)
  jclasses = []
  try:
    for fname in fnames:
      jclasses.append(jackparser.parse(fname))
  except jackparser.InputError as e:
    print("Error:", e.msg)
    print("In file '%s', line %d, column %d" %
          (e.token.fname, e.token.lineno, e.token.pos))
    return
  # parsing succeeded, now compile to VM
  compiler = JackCompiler(folder)
  for jclass in jclasses:
    compiler.compile(jclass)

# --------------------------------------------------------------------

if __name__ == "__main__":
  main()

# --------------------------------------------------------------------
