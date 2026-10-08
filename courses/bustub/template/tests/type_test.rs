//! Port of `test/type/type_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database Group).
//! `Type::GetInstance(type_id)` is gone (a `TypeId` carries the type-level functions); a C++ exception is an `Err`.

use bustub::common::exception::ExceptionType;
use bustub::types::type_id::TypeId;
use bustub::types::value::{CmpBool, Value};

const TYPE_TEST_TYPES: [TypeId; 6] = [TypeId::Boolean, TypeId::TinyInt, TypeId::SmallInt, TypeId::Integer, TypeId::BigInt, TypeId::Decimal];

/// BusTub's `BPlusTreePage<KeyType, ValueType>` from the test: a generic struct whose method compares two values.
struct BPlusTreePage<K, V>(std::marker::PhantomData<(K, V)>);

impl BPlusTreePage<Value, Value> {
    fn get_info(&self, key: &Value, val: &Value) -> Option<String> {
        if key.compare_equals(val).unwrap() == CmpBool::True {
            return Some(format!("key info{key}"));
        }
        None
    }
}

#[test]
fn invalid_type_test() {
    // First get the INVALID type
    let type_id = TypeId::Invalid;
    assert!(!type_id.is_coercable_from(type_id));

    // Then hit up all of the mofos methods: they should all be errors
    assert_eq!(type_id.type_size().unwrap_err().kind, ExceptionType::UnknownType);
    assert!(type_id.min_value().is_err());
    assert!(type_id.max_value().is_err());
}

#[test]
fn get_instance_test() {
    for col_type in TYPE_TEST_TYPES {
        assert!(col_type.is_coercable_from(col_type));
    }
}

#[test]
fn max_value_test() {
    for col_type in TYPE_TEST_TYPES {
        let max_val = col_type.max_value().unwrap();
        assert!(!max_val.is_null());
        // NOTE: We should not be allowed to create a value that is greater than the max value.
    }
}

#[test]
fn min_value_test() {
    for col_type in TYPE_TEST_TYPES {
        let min_val = col_type.min_value().unwrap();
        assert!(!min_val.is_null());
        // NOTE: We should not be allowed to create a value that is less than the min value.
    }
    let temp = "32";
    let val1 = Value::varchar(temp);
    let val2 = Value::integer(32);
    assert_eq!(val1.compare_equals(&val2).unwrap(), CmpBool::True);
}

#[test]
fn template_test() {
    let val1 = Value::integer(32);
    let val2 = Value::integer(32);
    println!("size is {}", std::mem::size_of_val(&(val1.clone(), val2.clone())));
    let node = BPlusTreePage::<Value, Value>(std::marker::PhantomData);
    assert_eq!(node.get_info(&val1, &val2), Some("key info32".to_string()));
}
