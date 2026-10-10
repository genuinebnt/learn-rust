//! Port of `src/binder/` and `src/include/binder/`. The binder takes the syntax tree and **binds** names: which table a name means,
//! which column a column reference is, what `*` expands to. It produces the *bound* tree the planner turns into a plan. Given code.

pub mod binder;
pub mod bound_expression;
pub mod bound_order_by;
pub mod bound_statement;
pub mod bound_table_ref;
