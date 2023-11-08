import regex

def fix_camelcase(camel_case):
    return regex.sub(r"[a-z][A-Z]", lambda m: m.group()[0] + " " + m.group()[1], camel_case)

def numberFormat(value):
    return format(int(value), ',d')