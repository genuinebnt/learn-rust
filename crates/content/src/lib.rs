//! anneal's content: tracks, stages and problems stored as folders under `content/`.
//!
//! [`Catalog::load`] reads everything and reports every problem it finds with the
//! content as an [`Issue`], so `anneal validate` can list them all at once.

mod catalog;
mod dsa;
pub mod model;

pub use catalog::{Catalog, Issue, LoadError, Loaded, Problem, ProblemFiles, Track};
pub use dsa::{Company, DsaCatalog, DsaProblem, Role, Technique};
pub use model::{Band, COMPANIES, Mode, Perf, Rules, Section, Status, Tier};
