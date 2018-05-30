#
# Representing a parse tree of a Jack program
#
# --------------------------------------------------------------------

class JackClass():
  def __init__(self, name):
    self.name = name
    self.fields = []
    self.statics = []
    self.subroutines = []

  def addvars(self, kind, vtype, vnames):
    if kind == "field":
      for vname in vnames:
        self.fields.append((vname, vtype))
    else:
      for vname in vnames:
        self.statics.append((vname, vtype))

  def addsubroutine(self, subroutine):
    self.subroutines.append(subroutine)

  def __repr__(self):
    s = "class %s {\n" % self.name
    if len(self.fields) > 0:
      s += "  fields: "
      for n,t in self.fields:
        s += "%s (%s), " % (n, t)
      s += "\n"
    if len(self.statics) > 0:
      s += "  statics: "
      for n,t in self.statics:
        s += "%s (%s), " % (n, t)
      s += "\n"
    s += "  subroutines:\n"
    for sb in self.subroutines:
      s += "    %s\n" % repr(sb)
    s += "}\n"
    return s

class Subroutine():
  def __init__(self, name, kind, ret_type, arguments, locals, statements):
    self.name = name
    self.kind = kind
    self.ret_type = ret_type
    self.arguments = arguments
    self.locals = locals
    self.statements = statements

  def __repr__(self):
    s = "%s %s %s(" % (self.kind, self.ret_type, self.name)
    for aname, atyp in self.arguments:
      s += "%s %s," % (atyp, aname)
    s += ")"
    return s

  def _print_statements(self):
    print(repr(self))
    if len(self.locals) > 0:
      print(" locals: ", end="")
      for lname, ltyp in self.locals:
        print("%s (%s)," % (lname, ltyp), end="")
      print()
    for s in self.statements:
      print(" - %s" % repr(s))

# --------------------------------------------------------------------      

class LetStatement():
  def __init__(self, vname, index, expr):
    self.vname = vname
    self.index = index
    self.expr = expr

  def __repr__(self):
    if self.index is None:
      return "LET %s = %s;" % (self.vname, repr(self.expr))
    else:
      return "LET %s[%s] = %s;" % (self.vname, repr(self.index),
                                   repr(self.expr))

class WhileStatement():
  def __init__(self, expr, statements):
    self.expr = expr
    self.statements = statements

  def __repr__(self):
    s = "WHILE (%s) { " % (self.expr)
    for st in self.statements:
      s += repr(st)
    s += " } "
    return s
    
class IfStatement():
  def __init__(self, expr, if_statements, else_statements):
    self.expr = expr
    self.if_statements = if_statements
    self.else_statements = else_statements    

  def __repr__(self):
    s = "IF (%s) { " % (self.expr)
    for st in self.if_statements:
      s += repr(st)
    if self.else_statements is None:
      return s + " } "
    s += " } else { "
    for st in self.else_statements:
      s += repr(st)
    return s + " } "
    
class ReturnStatement():
  def __init__(self, expr):
    self.expr = expr

  def __repr__(self):
    if self.expr is None:
      return "RETURN"
    return "RETURN (%s)" % (self.expr)

# --------------------------------------------------------------------      

class CallExpression():
  "Used both for do statements and function calls in expressions."
  def __init__(self, name, container, arguments):
    self.name = name
    self.container = container
    self.arguments = arguments

  def __repr__(self):
    if self.container is None:
      s = "%s(" % self.name
    else:
      s = "%s.%s(" % (self.container, self.name)
    for arg in self.arguments:
      s += "%s," % repr(arg)
    s += ")"
    return s

# --------------------------------------------------------------------      

class BinaryOperation():
  def __init__(self, operator, left, right):
    self.operator = operator
    self.left = left
    self.right = right

  def __repr__(self):
    return "(" + repr(self.left) + self.operator + repr(self.right) + ")"

class UnaryOperation():
  def __init__(self, operator, argument):
    self.operator = operator
    self.argument = argument

  def __repr__(self):
    return self.operator + repr(self.argument)
    
class ConstantExpression():
  "Represents true, false, null, and this"
  def __init__(self, value):
    self.value = value

  def __repr__(self):
    return self.value
    
class VariableExpression():
  "Represents a variable, possibly with array index"
  def __init__(self, name, index=None):
    self.name = name
    self.index = index

  def __repr__(self):
    if self.index is None:
      return self.name
    else:
      return "%s[%s]" % (self.name, repr(self.index))

# --------------------------------------------------------------------
