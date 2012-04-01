from attest import Tests
from . import schema, map

tests = Tests()
tests.register(schema.tests)
tests.register(map.tests)

