#
# Tokenizer
#
# Splits a given file into a sequence of tokens
#

_keywords = [ "class", "constructor", "method", "function",
              "int", "boolean", "char", "void",
              "var", "static", "field",
              "let", "do", "if", "else", "while",
              "return", "true", "false", "null", "this" ]

class Token(object):
  def __init__(self, value, pos, typ, fname, lineno):
    self.pos = pos
    self.typ = typ
    self.value = value
    self.fname = fname
    self.lineno = lineno
               
  def isNumber(self):
    return self.typ == "number"

  def isSymbol(self, s):
    return self.typ == "symbol" and self.value == s

  def isIdentifier(self):
    return self.typ == "identifier"

  def isKeyword(self, s):
    return self.typ == "keyword" and self.value == s

  def isTypeName(self):
    if self.isIdentifier():
      return True
    return self.typ == "keyword" and self.value in [ "int", "boolean", "char" ]

  def isConstant(self):
    return (self.typ == "keyword" and
            self.value in [ "true", "false", "null", "this"])

  def isString(self):
    return self.typ == "string"
  
  def isStop(self):
    return self.typ == "stop"

  def __repr__(self):
    return "Token(%s, %d, %s)" % (repr(self.value), self.pos, repr(self.type))

  def __str__(self):
    if self.isNumber():
      return "Number: %g" % self.value
    if self.isIdentifier():
      return "Identifier: %s" % self.value
    if self.isStop():
      return "Stop"
    if self.isString():
      return 'String: "%s"' % self.value
    if self.typ == "keyword":
      return "Keyword: %s" % self.value
    return "Symbol: %s" % self.value

# --------------------------------------------------------------------

def _is_id(ch):
  return ('a' <= ch and ch <= 'z') or ('A' <= ch and ch <= 'Z') or ch == '_'

def _is_id1(ch):
  return _is_id(ch) or ch in "0123456789"

def _is_digit(ch):
  return ch in "0123456789"

# --------------------------------------------------------------------

class Tokenizer():
  def __init__(self, fname):
    self.fname = fname
    fd = open(fname, "r")
    self.s = fd.read() + "\n"  # convenient to make sure file ends nicely
    fd.close()

  def _token(self, data, typ, pos):
    return Token(data, pos - self.linestart, typ,
                 self.fname, self.lineno)

  def tokenize(self):
    self.pos = 0
    self.lineno = 1
    self.linestart = 0
    tokens = []
    while True:
      tok = self._next_token()
      if tok is not None:
        tokens.append(tok)
        if tok.isStop():
          return tokens

  def _next_token(self):
    while self.pos < len(self.s) and self.s[self.pos] in " \t":
      self.pos += 1
    if self.pos == len(self.s):
      return self._token(None, "stop", self.pos)
    begin = self.pos
    ch = self.s[self.pos]
    # End of line
    if ch == "\n":
      self.pos += 1
      self.lineno += 1
      self.linestart = self.pos
      return None
    # // comment
    if ch == "/" and self.s[self.pos + 1] == "/":
      while self.s[self.pos] != "\n":
        self.pos += 1
      return None # next time handle the linefeed
    # /* comment
    if ch == "/" and self.s[self.pos + 1] == "*":
      self.pos += 2
      while self.pos < len(self.s) - 2:
        if self.s[self.pos] == "*" and self.s[self.pos + 1] == "/":
          self.pos += 2
          return None
        if self.s[self.pos] == "\n":
          self.lineno += 1
          self.linestart = self.pos + 1
        self.pos += 1
      # the comment was not terminated before the end of the file
      return self._token(None, "stop", begin)
    # Identifier (keyword or name)
    if _is_id(ch):
      while self.pos < len(self.s) and _is_id1(self.s[self.pos]):
        self.pos += 1
      txt = self.s[begin:self.pos]
      if txt in _keywords:
        return self._token(txt, "keyword", begin)
      else:
        return self._token(txt, "identifier", begin)
    # Number literal
    if _is_digit(ch):
      while self.pos < len(self.s) and _is_digit(self.s[self.pos]):
        self.pos += 1
      txt = self.s[begin:self.pos]
      return self._token(int(txt), "number", begin)
    # String literal
    if ch == '"':
      self.pos += 1
      # we silently accept strings terminated by the end of line
      while self.s[self.pos] not in '"\n':
        self.pos += 1
      txt = self.s[begin+1:self.pos]
      if self.s[self.pos] == '"':
        self.pos += 1 
      return self._token(txt, "string", begin)
    # Symbol
    self.pos += 1
    return self._token(self.s[begin], "symbol", begin)

# --------------------------------------------------------------------

# Test code

if __name__ == "__main__":
  import sys
  if len(sys.argv) != 2:
    sys.stderr.write("Usage: python3 tokens.py <file.jack>\n")
    sys.exit(9)
  fname = sys.argv[1]
  toknzr = Tokenizer(fname)
  toks = toknzr.tokenize()
  print("\n".join(map(lambda x: str(x), toks)))

# --------------------------------------------------------------------
