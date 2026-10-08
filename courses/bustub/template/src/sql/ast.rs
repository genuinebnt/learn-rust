//! The syntax tree the parser builds. It is what PostgreSQL's parser would give BusTub's binder (`PGSelectStmt`, `PGAExpr`, ...), in
//! Rust enums. Identifiers are lower-cased unless they were quoted, as PostgreSQL does. Given code.

#[derive(Clone, Debug, PartialEq)]
pub enum Statement {
    CreateTable { name: String, columns: Vec<ColumnDef>, primary_key: Vec<String> },
    CreateIndex { name: String, table: String, columns: Vec<String>, using: Option<String> },
    Insert { table: String, columns: Option<Vec<String>>, query: Box<Query> },
    Update { table: String, assignments: Vec<(String, Expr)>, filter: Option<Expr>, has_from: bool },
    Delete { table: String, filter: Option<Expr> },
    Select(Box<Query>),
    /// `EXPLAIN [(option, ...)] statement`.
    Explain { options: Vec<String>, statement: Box<Statement> },
    Set { name: String, value: Expr },
    Show { name: String },
    Begin,
    Commit,
    Rollback,
}

#[derive(Clone, Debug, PartialEq)]
pub struct ColumnDef {
    pub name: String,
    /// The type's name as written (`int`, `varchar`, ...), lower-case.
    pub type_name: String,
    /// The `(n)` after the type, if any.
    pub type_args: Vec<Expr>,
    pub primary_key: bool,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Query {
    pub ctes: Vec<Cte>,
    pub body: QueryBody,
    pub order_by: Vec<OrderItem>,
    pub limit: Option<Expr>,
    pub offset: Option<Expr>,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Cte {
    pub name: String,
    pub query: Query,
    pub recursive: bool,
}

#[derive(Clone, Debug, PartialEq)]
pub enum QueryBody {
    Select(Box<SelectCore>),
    Values(Vec<Vec<Expr>>),
}

#[derive(Clone, Debug, PartialEq)]
pub struct SelectCore {
    pub distinct: bool,
    pub distinct_on: bool,
    pub items: Vec<SelectItem>,
    pub from: Vec<TableRef>,
    pub filter: Option<Expr>,
    pub group_by: Vec<Expr>,
    pub having: Option<Expr>,
}

#[derive(Clone, Debug, PartialEq)]
pub enum SelectItem {
    Wildcard,
    Expr { expr: Expr, alias: Option<String> },
}

#[derive(Clone, Debug, PartialEq)]
pub enum TableRef {
    Named { name: String, alias: Option<String> },
    Subquery { query: Box<Query>, alias: Option<String> },
    Join { kind: JoinKind, left: Box<TableRef>, right: Box<TableRef>, on: Option<Expr> },
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum JoinKind {
    Inner,
    Left,
    Right,
    Full,
    Cross,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum SortDir {
    Default,
    Asc,
    Desc,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum SortNulls {
    Default,
    First,
    Last,
}

#[derive(Clone, Debug, PartialEq)]
pub struct OrderItem {
    pub expr: Expr,
    pub dir: SortDir,
    pub nulls: SortNulls,
}

#[derive(Clone, Debug, PartialEq)]
pub enum Expr {
    Integer(i64),
    /// A number that is not a 32-bit integer (`1.5`, `1e3`, `3000000000`), as written.
    Float(String),
    Str(String),
    Bool(bool),
    Null,
    /// `a`, `t.a`.
    Column(Vec<String>),
    Binary { op: String, left: Box<Expr>, right: Box<Expr> },
    Unary { op: String, expr: Box<Expr> },
    IsNull { expr: Box<Expr>, negated: bool },
    Function { name: String, args: Vec<Expr>, distinct: bool, over: Option<Box<WindowSpec>> },
    /// `count(*)` is `Function { name: "count", args: [] }`; a bare `*` in an argument list is this.
    Star,
}

#[derive(Clone, Debug, PartialEq)]
pub struct WindowSpec {
    pub partition_by: Vec<Expr>,
    pub order_by: Vec<OrderItem>,
    pub frame: Option<WindowFrame>,
}

#[derive(Clone, Debug, PartialEq)]
pub struct WindowFrame {
    pub range: bool,
    pub start: FrameBound,
    pub end: FrameBound,
}

#[derive(Clone, Debug, PartialEq)]
pub enum FrameBound {
    UnboundedPreceding,
    UnboundedFollowing,
    CurrentRow,
    Preceding(Box<Expr>),
    Following(Box<Expr>),
}
