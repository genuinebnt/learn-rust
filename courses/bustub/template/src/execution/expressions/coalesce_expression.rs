//! `COALESCE(a, b, ...)` as a node of its own.

use std::any::Any;
use std::sync::Arc;

use super::abstract_expression::{ExprRef, Expression};
use crate::catalog::column::Column;
use crate::catalog::schema::Schema;
use crate::common::exception::{Exception, ExceptionType, Result};
use crate::storage::table::tuple::Tuple;
use crate::types::value::Value;

#[derive(Clone, Debug)]
pub struct CoalesceExpression {
    children: Vec<ExprRef>,
    ret_type: Column,
}

impl CoalesceExpression {
    /// At least one argument; all of one type (the engine types a bare NULL constant INTEGER: it takes the type of the others).
    pub fn new(args: Vec<ExprRef>) -> Result<CoalesceExpression> {
        todo!("3i-c6: at least one argument; one shared type, a NULL constant adopting it; else MismatchType")
    }
}

impl Expression for CoalesceExpression {
    fn evaluate(&self, tuple: &Tuple, schema: &Schema) -> Result<Value> {
        todo!("3i-c6: the first non-NULL child value; evaluate no child after it and none twice")
    }

    fn evaluate_join(&self, left_tuple: &Tuple, left_schema: &Schema, right_tuple: &Tuple, right_schema: &Schema) -> Result<Value> {
        todo!("3i-c6: the same with evaluate_join")
    }

    fn children(&self) -> &[ExprRef] {
        &self.children
    }

    fn return_type(&self) -> &Column {
        &self.ret_type
    }

    fn to_string(&self) -> String {
        format!("coalesce({})", self.children.iter().map(|c| c.to_string()).collect::<Vec<_>>().join(", "))
    }

    fn clone_with_children(&self, children: Vec<ExprRef>) -> ExprRef {
        Arc::new(CoalesceExpression { children, ..self.clone() })
    }

    fn as_any(&self) -> &dyn Any {
        self
    }
}
