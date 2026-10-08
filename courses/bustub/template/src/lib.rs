//! BusTub in Rust. The layout mirrors cmu-db/bustub: `src/common`, `src/storage/disk`, ...
//!
//! Every function a stage asks you to write is `todo!()` until you get there. The warnings that come with that
//! (unused variables, unreachable code) are silenced so the output stays about your tests.
#![allow(unused_variables, unused_mut, unused_imports, unreachable_code, dead_code)]

pub mod buffer;
pub mod catalog;
pub mod common;
pub mod container;
pub mod storage;
pub mod types;
