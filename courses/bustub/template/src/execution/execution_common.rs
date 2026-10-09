//! Port of `src/execution/execution_common.cpp` (the parts project 3 needs): the **sort key** of a tuple and the comparison of two sort
//! entries. Sorting, top-N, and window functions all order rows with these.

use std::cmp::Ordering;

use crate::binder::bound_order_by::{OrderBy, OrderByNullType, OrderByType};
use crate::catalog::schema::Schema;
use crate::common::exception::Result;
use crate::storage::table::tuple::Tuple;
use crate::types::value::{CmpBool, Value};

/// The values of a tuple's ORDER BY expressions.
pub type SortKey = Vec<Value>;
/// A sort key and the tuple it belongs to.
pub type SortEntry = (SortKey, Tuple);

/// Evaluates each ORDER BY expression on `tuple` (laid out with `schema`).
pub fn generate_sort_key(tuple: &Tuple, order_bys: &[OrderBy], schema: &Schema) -> Result<SortKey> {
    todo!("3g-01: the value of every order-by expression for this tuple, in order")
}

/// Orders sort entries by their keys according to the ORDER BY list. BusTub's `TupleComparator`.
#[derive(Clone, Debug)]
pub struct TupleComparator {
    order_bys: Vec<OrderBy>,
}

impl TupleComparator {
    pub fn new(order_bys: Vec<OrderBy>) -> TupleComparator {
        TupleComparator { order_bys }
    }

    /// Compares two non-NULL values (the same type): `Less`, `Equal` or `Greater`.
    fn compare_values(a: &Value, b: &Value) -> Ordering {
        if a.compare_equals(b) == Ok(CmpBool::True) {
            Ordering::Equal
        } else if a.compare_less_than(b) == Ok(CmpBool::True) {
            Ordering::Less
        } else {
            Ordering::Greater
        }
    }

    /// The order of two entries (by their keys). `Less` means `a` comes first.
    pub fn compare(&self, a: &SortEntry, b: &SortEntry) -> Ordering {
        self.compare_keys(&a.0, &b.0)
    }

    /// The order of two sort keys: key by key; the first key that differs decides. `Less` means `a` comes first.
    ///
    /// For each key: `Desc` reverses the order of values; a NULL is the **smallest** value (first when ascending, last when
    /// descending) unless the key says `NULLS FIRST` or `NULLS LAST`, which put NULLs first or last whatever the direction.
    pub fn compare_keys(&self, a: &SortKey, b: &SortKey) -> Ordering {
        todo!("3g-01: for each order-by key in turn: both NULL: equal; one NULL: by the NULL rule above; else compare the values (Value::compare_equals / compare_less_than), reversed for DESC; return the first result that is not Equal; Equal if all are")
    }
}
