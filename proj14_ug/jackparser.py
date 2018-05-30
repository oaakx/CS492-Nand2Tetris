#
# Parse file and generate parse tree
#

import tokens
from parsetree import *

# --------------------------------------------------------------------

class InputError(Exception):
  def __init__(self, msg, token):
    self.msg = msg
    self.token = token

# --------------------------------------------------------------------

def parse_item(tok):
  t = tok[0]
  if t.isIdentifier():
    if tok[1].isSymbol("["): # array with index
      tok.pop(0)
      tok.pop(0)
      index = parse_expression(tok)
      if not tok[0].isSymbol("]"):
        raise InputError("Expected operator or ']'", tok[0])
      tok.pop(0)
      return VariableExpression(t.value, index)
    if tok[1].isSymbol(".") or tok[1].isSymbol("("):
      return parse_call(tok)
    # just a simple variable name
    tok.pop(0)
    return VariableExpression(t.value)
  tok.pop(0)  # gobble t
  if t.isNumber():
    if t.value > 32767:
      raise InputError("Integer is larger than 32767", t)
    return t.value
  if t.isString():
    return t.value  # represent simply as a str object
  if t.isConstant():
    return ConstantExpression(t.value)
  if not t.isSymbol("("):
    raise InputError("Expected number, string literal, identifier, or '('", t)
  expr = parse_expression(tok)
  if not tok[0].isSymbol(")"):
    raise InputError("Expected operator or ')'", tok[0])
  tok.pop(0)
  return expr

def parse_factor(tok):
  t = tok[0]
  operator = None
  if t.isSymbol("-") or t.isSymbol("~"):
    operator = t.value
    tok.pop(0)
  expr = parse_item(tok)
  return expr if operator is None else UnaryOperation(operator, expr)
  
def parse_term(tok):
  expr = parse_factor(tok)
  t = tok[0]
  while t.isSymbol("*") or t.isSymbol("/") or t.isSymbol("&"):
    tok.pop(0)
    rhs = parse_factor(tok)
    expr = BinaryOperation(t.value, expr, rhs)
    t = tok[0]
  return expr

def parse_expression(tok):
  expr = parse_term(tok)
  t = tok[0]
  while (t.isSymbol("+") or t.isSymbol("-") or t.isSymbol("|") or
         t.isSymbol("<") or t.isSymbol(">") or t.isSymbol("=")):
    tok.pop(0)
    rhs = parse_term(tok)
    expr = BinaryOperation(t.value, expr, rhs)
    t = tok[0]
  return expr

# --------------------------------------------------------------------

def parse_call(tok):
  if not tok[0].isIdentifier():
    raise InputError("Expected function name", tok[0])
  name = tok[0].value
  tok.pop(0)
  container = None
  if tok[0].isSymbol("."):
    # Class.function or object.method
    tok.pop(0)
    if not tok[0].isIdentifier():
      raise InputError("Expected function name", tok[0])
    container = name
    name = tok[0].value
    tok.pop(0)
  if not tok[0].isSymbol("("):
    raise InputError("Expected '('", tok[0])
  tok.pop(0)
  arguments  = []
  while True:
    if tok[0].isSymbol(')'):
      tok.pop(0)
      return CallExpression(name, container, arguments)
    expr = parse_expression(tok)
    arguments.append(expr)
    if not tok[0].isSymbol(')'):
      if not tok[0].isSymbol(','):
        raise InputError("Expected operator, ',', or ')'", tok[0])
      tok.pop(0)
  
# --------------------------------------------------------------------

def parse_let(tok):
  t = tok[0]
  tok.pop(0)
  if not t.isIdentifier():
    raise InputError("Expected variable name", t)
  vname = t.value
  index = None
  if tok[0].isSymbol("["):
    tok.pop(0)
    index = parse_expression(tok)
    if not tok[0].isSymbol("]"):
      raise InputError("Expected operator or ']'", tok[0])
    tok.pop(0)
  if not tok[0].isSymbol("="):
    raise InputError("Expected '='", tok[0])
  tok.pop(0)
  expr = parse_expression(tok)
  if not tok[0].isSymbol(";"):
    raise InputError("Expected operator or ';'", tok[0])
  tok.pop(0)
  return LetStatement(vname, index, expr)

def parse_if(tok):
  if not tok[0].isSymbol("("):
    raise InputError("Expected '('", tok[0])
  tok.pop(0)
  expr = parse_expression(tok)
  if not tok[0].isSymbol(")"):
    raise InputError("Expected operator or ')'", tok[0])
  tok.pop(0)
  if not tok[0].isSymbol("{"):
    raise InputError("Expected '{'", tok[0])
  tok.pop(0)
  statements = parse_statements(tok)
  else_statements = None
  if tok[0].isKeyword("else"):
    tok.pop(0)
    if not tok[0].isSymbol("{"):
      raise InputError("Expected '{'", tok[0])
    tok.pop(0)
    else_statements = parse_statements(tok)
  return IfStatement(expr, statements, else_statements)

def parse_while(tok):
  if not tok[0].isSymbol("("):
    raise InputError("Expected '('", tok[0])
  tok.pop(0)
  expr = parse_expression(tok)
  if not tok[0].isSymbol(")"):
    raise InputError("Expected operator or ')'", tok[0])
  tok.pop(0)
  if not tok[0].isSymbol("{"):
    raise InputError("Expected '{'", tok[0])
  tok.pop(0)
  statements = parse_statements(tok)
  return WhileStatement(expr, statements)
  
def parse_do(tok):
  sbcall = parse_call(tok)
  if not tok[0].isSymbol(";"):
    raise InputError("Expected ';'", tok[0])
  tok.pop(0)
  return sbcall

def parse_return(tok):
  expr = None
  if not tok[0].isSymbol(";"):
    expr = parse_expression(tok)
  if not tok[0].isSymbol(";"):
    raise InputError("Expected ';'", tok[0])
  tok.pop(0)
  return ReturnStatement(expr)
  
# --------------------------------------------------------------------

def parse_statement(tok):
  """Returns statement or None for '}'"""
  t = tok[0]
  tok.pop(0)
  if t.isKeyword("let"):
    return parse_let(tok)
  if t.isKeyword("do"):
    return parse_do(tok)
  if t.isKeyword("if"):
    return parse_if(tok)
  if t.isKeyword("while"):
    return parse_while(tok)
  if t.isKeyword("return"):
    return parse_return(tok)
  if t.isSymbol('}'):
    return None
  raise InputError("Expected let, if, while, do, return, or '}'", t)

def parse_statements(tok):
  "Parse a sequence of statements, and gobble terminating '}'."
  s = parse_statement(tok)
  statements = []
  while s is not None:
    statements.append(s)
    s = parse_statement(tok)
  return statements
  
# --------------------------------------------------------------------

def parse_namelist(tok):
  names = []
  while True:
    if not tok[0].isIdentifier():
      raise InputError("Expected identifier", tok[0])
    names.append(tok[0].value)
    tok.pop(0)
    if tok[0].isSymbol(";"):
      tok.pop(0)
      return names
    if not tok[0].isSymbol(","):
      raise InputError("Expected ',' or ';'", tok[0])
    tok.pop(0)
    
def parse_vars(tok):
  if not tok[0].isTypeName():
    raise InputError("Expected a type name", tok[0])
  tname = tok[0].value
  tok.pop(0)
  names = parse_namelist(tok)
  return tname, names
  
def parse_arglist(tok):
  args = []
  while True:
    if not tok[0].isTypeName():
      raise InputError("Expected a type name", tok[0])
    tname = tok[0].value
    tok.pop(0)
    if not tok[0].isIdentifier():
      raise InputError("Expected a parameter name", tok[0])
    name = tok[0].value
    tok.pop(0)
    args.append((name, tname))
    if tok[0].isSymbol(")"):
      tok.pop(0)
      return args
    if not tok[0].isSymbol(","):
      raise InputError("Expected ',' or ')'", tok[0])
    tok.pop(0)
  
# --------------------------------------------------------------------

def parse_subroutine(tok):
  kind = tok[0].value # constructor, method, or function
  tok.pop(0)
  t1 = tok[0]
  if not (t1.isKeyword("void") or t1.isTypeName()):
    raise InputError("Expected type name", t1)
  tok.pop(0)
  ret_type = t1.value
  if not tok[0].isIdentifier():
    raise InputError("Expected function name", tok[0])
  sbname = tok[0].value
  tok.pop(0)
  if not tok[0].isSymbol("("):
    raise InputError("Expected '('", tok[0])
  tok.pop(0)
  args = []
  if tok[0].isSymbol(")"): # no arguments
    tok.pop(0)
  else:
    args = parse_arglist(tok)
  if not tok[0].isSymbol("{"):
    raise InputError("Expected '{'", tok[0])
  tok.pop(0)
  t = tok[0]
  locals = []
  while t.isKeyword("var"):
    tok.pop(0)
    tname, names = parse_vars(tok)
    for name in names:
      locals.append((name, tname))
    t = tok[0]
  statements = parse_statements(tok)
  return Subroutine(sbname, kind, ret_type, args, locals, statements)

# --------------------------------------------------------------------

def parse_class(tok):
  if not tok[0].isKeyword("class"):
    raise InputError("Expected keyword 'class'", tok[0])
  tok.pop(0)
  if not tok[0].isIdentifier():
    raise InputError("Expected class name", tok[0])
  name = tok[0].value
  tok.pop(0)
  jclass = JackClass(name)
  if not tok[0].isSymbol("{"):
    raise InputError("Expected '{'", tok[0])
  tok.pop(0)
  t  = tok[0]
  while t.isKeyword("field") or t.isKeyword("static"):
    tok.pop(0)
    vtype, varnames = parse_vars(tok)
    jclass.addvars(t.value, vtype, varnames)
    t = tok[0]
  while (t.isKeyword("constructor") or t.isKeyword("function") or
         t.isKeyword("method")):
    subroutine = parse_subroutine(tok)
    jclass.addsubroutine(subroutine)
    t = tok[0]
  if not tok[0].isSymbol("}"):
    raise InputError("Expected subroutine or '}'", tok[0])
  tok.pop(0)
  return jclass

# --------------------------------------------------------------------

def parse(fname):
  toks = tokens.Tokenizer(fname)
  tok = toks.tokenize()
  ptree = parse_class(tok)
  if not tok[0].isStop():
    raise InputError("Expected end of file", tok[0])
  return ptree

# --------------------------------------------------------------------

if __name__ == "__main__":
  import sys, os
  if len(sys.argv) not in [2, 3]:
    sys.stderr.write("Usage: python3 parser.py [-v] <file.jack>\n")
    sys.stderr.write("    or python3 parser.py [-v] <directory>\n")    
    sys.exit(9)
  verbose = False
  if len(sys.argv) == 3:
    verbose = (sys.argv[1] == "-v")
  path = sys.argv[-1]
  fnames = []
  if path.endswith(".jack"):
    fnames.append(path)
  else:
    for fname in os.listdir(path):
      if fname.endswith(".jack"):
        fnames.append(path + "/" + fname)
  try:
    jclasses = []
    for fname in fnames:
      jclasses.append(parse(fname))
    for jclass in jclasses:
      print(repr(jclass))
    if verbose:
      for jclass in jclasses:
        for sb in jclass.subroutines:
          sb._print_statements()
  except InputError as e:
    print("Error:", e.msg)
    print("In file '%s', line %d, column %d" %
          (e.token.fname, e.token.lineno, e.token.pos))

# --------------------------------------------------------------------
