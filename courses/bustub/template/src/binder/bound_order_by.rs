//! Port of `src/include/binder/bound_order_by.h`: one item of an `ORDER BY`, before (`BoundOrderBy`) and after (`OrderBy`) planning.
//! Given code.

use std::fmt;

use super::bound_expression::BoundExpression;
use crate::execution::expressions::abstract_expression::ExprRef;

/// ASC / DESC as written (`Default` when neither was).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum OrderByType {
    Invalid,
    Default,
    Asc,
    Desc,
}

impl fmt::Display for OrderByType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            OrderByType::Invalid => "Invalid",
            OrderByType::Asc => "Ascending",
            OrderByType::Desc => "Descending",
            OrderByType::Default => "Default",
        })
    }
}

/// NULLS FIRST / NULLS LAST as written.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum OrderByNullType {
    Default,
    NullsFirst,
    NullsLast,
}

impl fmt::Display for OrderByNullType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            OrderByNullType::Default => "Default",
            OrderByNullType::NullsFirst => "NullsFirst",
            OrderByNullType::NullsLast => "NullsLast",
        })
    }
}

/// An `ORDER BY` item as bound by the binder (an unplanned expression).
#[derive(Clone, Debug)]
pub struct BoundOrderBy {
    pub order_type: OrderByType,
    pub null_order: OrderByNullType,
    pub expr: BoundExpression,
}

impl fmt::Display for BoundOrderBy {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "BoundOrderBy {{ type={}, nulls={}, expr={} }}", self.order_type, self.null_order, self.expr)
    }
}

/// BusTub's `OrderBy = std::tuple<OrderByType, OrderByNullType, AbstractExpressionRef>`: how to sort and by what.
#[derive(Clone, Debug)]
pub struct OrderBy {
    pub order_type: OrderByType,
    pub null_order: OrderByNullType,
    pub expr: ExprRef,
}

impl OrderBy {
    pub fn new(order_type: OrderByType, null_order: OrderByNullType, expr: ExprRef) -> OrderBy {
        OrderBy { order_type, null_order, expr }
    }
}

impl fmt::Display for OrderBy {
    /// `(Default, Default, #0.1)`: how fmt prints BusTub's tuple.
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({}, {}, {})", self.order_type, self.null_order, self.expr)
    }
}
