from ranges import parse_range

assert parse_range("1-5") == [1, 2, 3, 4, 5]
assert parse_range("7") == [7]

try:
    parse_range("5-1")
except ValueError:
    pass
else:
    raise AssertionError("expected ValueError")

print("ok")
