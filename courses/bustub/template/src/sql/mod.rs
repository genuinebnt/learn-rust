//! A small SQL parser for the subset BusTub's shell accepts. BusTub parses with libpg_query (PostgreSQL's own parser, in C); this
//! course writes the parser in Rust so the project needs no dependencies. `parse(sql)` returns the statements as a syntax tree
//! (`ast`); the binder turns names into catalog objects. Given code.

pub mod ast;
pub mod lexer;
pub mod parser;
