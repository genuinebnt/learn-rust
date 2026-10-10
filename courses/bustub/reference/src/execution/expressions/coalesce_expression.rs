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
        // @begin 3i-c6
        use super::constant_value_expression::ConstantValueExpression;
        if args.is_empty() {
            return Err(Exception::new(ExceptionType::Invalid, "COALESCE needs at least one argument"));
        }
        let is_null_literal = |e: &ExprRef| e.as_any().downcast_ref::<ConstantValueExpression>().is_some_and(|c| c.val.is_null());
        let ret = args.iter().find(|a| !is_null_literal(a)).unwrap_or(&args[0]).return_type().with_column_name("<val>");
        let mut children = Vec::new();
        for a in args {
            if is_null_literal(&a) {
                children.push(Arc::new(ConstantValueExpression::new(Value::null(ret.type_id()))) as ExprRef);
            } else if a.return_type().type_id() != ret.type_id() {
                return Err(Exception::new(ExceptionType::MismatchType, "COALESCE types cannot be matched"));
            } else {
                children.push(a);
            }
        }
        Ok(CoalesceExpression { children, ret_type: ret })
        //~ todo!("3i-c6: at least one argument; one shared type, a NULL constant adopting it; else MismatchType")
        // @end
    }
}

impl Expression for CoalesceExpression {
    fn evaluate(&self, tuple: &Tuple, schema: &Schema) -> Result<Value> {
        // @begin 3i-c6
        for child in &self.children {
            let v = child.evaluate(tuple, schema)?;
            if !v.is_null() {
                return Ok(v);
            }
        }
        Ok(Value::null(self.ret_type.type_id()))
        //~ todo!("3i-c6: the first non-NULL child value; evaluate no child after it and none twice")
        // @end
    }

    fn evaluate_join(&self, left_tuple: &Tuple, left_schema: &Schema, right_tuple: &Tuple, right_schema: &Schema) -> Result<Value> {
        // @begin 3i-c6
        for child in &self.children {
            let v = child.evaluate_join(left_tuple, left_schema, right_tuple, right_schema)?;
            if !v.is_null() {
                return Ok(v);
            }
        }
        Ok(Value::null(self.ret_type.type_id()))
        //~ todo!("3i-c6: the same with evaluate_join")
        // @end
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
