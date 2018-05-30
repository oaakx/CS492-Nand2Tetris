class Papa:
    pass


class Oak:
    pass


class Son(Papa):
    pass


son = Papa()
# son = Son()

if isinstance(son, Papa):
    print("They are either Papa or Son.")

if son.__class__ != Papa:
    print("Oh, they aren't Papa.")
else:
    print("They are Papa, after all.")

print("Moment of truth: " + str(son.__class__))
