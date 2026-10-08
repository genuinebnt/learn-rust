BusTub's `type_test`, ported. Five small tests, as in the original: the invalid type throws everywhere, every real type is a type, every type has a minimum and a maximum that are not NULL, and the comparison `'32' = 32` holds.

## The task

Make `type_test` pass (`cargo test --test type_test`): `invalid_type_test`, `get_instance_test`, `max_value_test`, `min_value_test` (which also checks `'32' = 32`) and `template_test` (a generic struct holding two `Value`s and comparing them).

## Tests

- All five tests of `type_test.rs`.

## Notes

**What changed from the C++.** `Type::GetInstance(type_id)` returns a singleton `Type` object with virtual methods; in this port the type-level functions live on `TypeId` and the value-level ones on `Value`, so `t->GetTypeId()` has no counterpart and `EXPECT_THROW` becomes `.unwrap_err()`. The C++ test file's `TemplateTest` builds a `std::pair<Value, Value>` and a templated class; here a tiny generic struct does the same job.

**What this module did not port.** BusTub's `TIMESTAMP` formats dates (`2025-09-30 12:00:00.000000+00`) and its type system has a `VECTOR` type for the vector-search project. This course carries a `Timestamp` as a number and has no `Vector`; no `.slt` test of the course's modules needs either.

## In BusTub

`test/type/type_test.cpp` ("TEST(TypeTests, InvalidTypeTest)" ... "TEST(TypeTests, TemplateTest)").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `EXPECT_THROW(Type::GetTypeSize(type_id), Exception);` | `assert_eq!(type_id.type_size().unwrap_err().kind, ExceptionType::UnknownType)` |
| `EXPECT_EQ(val1.CompareEquals(val2), CmpBool::CmpTrue);` | `assert_eq!(val1.compare_equals(&val2).unwrap(), CmpBool::True)` |

## Learn more
- [BusTub's `type_test.cpp`](https://github.com/cmu-db/bustub/blob/master/test/type/type_test.cpp)

## Performance

These tests are instantaneous; the point of the boss is conformance. The performance question for the whole module is the cost of a dynamically typed value (stage 5's "Measure it"): write down your numbers now, and compare them with the executors' in module 3b.

**Measure it.** Run all six stages' benchmarks you wrote along the way in one file and keep the output: module 3b's executors will be measured against it.

## Hints

### If `min_value_test` fails on `'32' = 32`

The comparison converts the *integer* to text when the string is on the left: `"32" == "32"`. If you converted the string to a number instead the answer would still be true, but `'5' < 12` (stage 4's test) would be wrong. Re-read the rule for a string on the left.

### If `get_instance_test` fails for `Boolean`

`Boolean` is coercable from every type, including `Invalid`: that is the table, not a bug.

### Everything else failing

`cargo test --test stages_3a` names the stage whose rule is broken before this test does.
