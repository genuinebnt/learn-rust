//! Table names and ids.

use std::collections::BTreeMap;

#[derive(Debug, PartialEq, Eq)]
pub enum NameError {
    Exists,
    Missing,
    Invalid,
}

pub struct NameCatalog {
    _names: (),
}

impl NameCatalog {
    pub fn new() -> NameCatalog {
        todo!("3c-c2: no tables; ids start at 1")
    }

    pub fn create(&mut self, name: &str) -> Result<u32, NameError> {
        todo!("3c-c2: a new id for a new name")
    }

    pub fn lookup(&self, name: &str) -> Option<u32> {
        todo!("3c-c2: the id of the table")
    }

    pub fn drop(&mut self, name: &str) -> bool {
        todo!("3c-c2: forget the name (the id is not reused)")
    }

    pub fn rename(&mut self, old: &str, new: &str) -> Result<(), NameError> {
        todo!("3c-c2: move the name, keep the id")
    }

    pub fn names(&self) -> Vec<String> {
        todo!("3c-c2: lowercase names, sorted")
    }
}

impl Default for NameCatalog {
    fn default() -> Self {
        NameCatalog::new()
    }
}
