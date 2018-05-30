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

unopmap = { "-" : "neg",
            "~" : "not" }
  
# --------------------------------------------------------------------


class JackCompiler():
  def __init__(self, folder):
    self.folder = folder
    self.nifs = 0
    self.nwhiles = 0

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
    self.compile_expression(jclass, sb, let.expr)
    vseg = self._var_segment(jclass, sb, let.vname)
    if let.index:
      self.out.write("push %s // %s\n" % (vseg, let.vname))
      self.compile_expression(jclass, sb, let.index)
      self.out.write("add\n")
      self.out.write("pop pointer 1\n")
      self.out.write("pop that 0 // %s[%s]\n" % (let.vname, let.index))
    else:
      self.out.write("pop %s // %s\n" % (vseg, let.vname))


  # st is of type CallExpression
  def compile_do(self, jclass, sb, st):
    self.compile_call(jclass, sb, st)
    self.out.write("pop temp 0 // void\n")


  # ifst is of type IfStatement
  def compile_if(self, jclass, sb, ifst):
    ifendlabel = "%s.%s$ifend%s" % (jclass.name, sb.name, self.nifs)
    elselabel  = "%s.%s$else%s"  % (jclass.name, sb.name, self.nifs)
    self.nifs += 1

    self.compile_expression(jclass, sb, ifst.expr)
    self.out.write("not\n")

    if ifst.else_statements:
      self.out.write("if-goto %s\n" % elselabel)
    else:
      self.out.write("if-goto %s\n" % ifendlabel)

    for st in ifst.if_statements:
      self.compile_statement(jclass, sb, st)

    if ifst.else_statements:
      self.out.write("goto %s\n" % ifendlabel)
      self.out.write("label %s\n" % elselabel)
      for st in ifst.else_statements:
            self.compile_statement(jclass, sb, st)

    self.out.write("label %s\n" % ifendlabel)


  # whilest is of type WhileStatement
  def compile_while(self, jclass, sb, whilest):
    whilelabel     = "%s.%s$while%s"     % (jclass.name, sb.name, self.nwhiles)
    whileendlabel  = "%s.%s$whileend%s"  % (jclass.name, sb.name, self.nwhiles)
    self.nwhiles += 1

    self.out.write("label %s\n" % whilelabel)
    self.compile_expression(jclass, sb, whilest.expr)
    self.out.write("not\n")
    self.out.write("if-goto %s\n" % whileendlabel)

    for st in whilest.statements:
      self.compile_statement(jclass, sb, st)

    self.out.write("goto %s\n" % whilelabel)
    self.out.write("label %s\n" % whileendlabel)


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
    vseg = self._var_segment(jclass, sb, var.name)
    self.out.write("push %s // %s\n" % (vseg, var.name))
    if var.index:
      self.compile_expression(jclass, sb, var.index)
      self.out.write("add")
      self.out.write("pop pointer 1")
      self.out.write("push that 0")


  def _var_segment(self, jclass, sb, var):
    # local
    scope = list(zip(*sb.locals))
    if scope and var in scope[0]:
      return "local %s" % scope[0].index(var)
    # argument
    scope = list(zip(*sb.arguments))
    if scope and var in scope[0]:
      return "argument %s" % scope[0].index(var)
    # field
    scope = list(zip(*jclass.fields))
    if scope and var in scope[0]:
      return "this %s" % scope[0].index(var)
    # static
    scope = list(zip(*jclass.statics))
    if scope and var in scope[0]:
      return "static %s" % scope[0].index(var)
    return None

  # call is of type CallExpression
  def compile_call(self, jclass, sb, call):
    for arg in call.arguments:
      self.compile_expression(jclass, sb, arg)
    self.out.write("call %s.%s %s\n" % (call.container, call.name, len(call.arguments)))


  # binop is of type BinaryOperation
  def compile_binaryop(self, jclass, sb, binop):
    self.compile_expression(jclass, sb, binop.left)
    self.compile_expression(jclass, sb, binop.right)
    self.out.write("%s\n" % binopmap[binop.operator])


  # unop is of type UnaryOperation
  def compile_unaryop(self, jclass, sb, unop):
    self.compile_expression(jclass, sb, unop.argument)
    self.out.write("%s\n" % unopmap[unop.operator])

  
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
