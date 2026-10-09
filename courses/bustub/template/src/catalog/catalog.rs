//! Port of `src/include/catalog/catalog.h`: the catalog of the database: which tables and indexes exist and where they are. It is **not
//! persistent** (BusTub's isn't either): it lives in memory for the life of the instance. Tables and indexes are identified by a name
//! (tables: unique; indexes: unique per table) and by an **oid**, a number handed out in creation order.

use std::collections::HashMap;
use std::sync::Arc;

use super::schema::Schema;
use crate::buffer::buffer_pool_manager::BufferPoolManager;
use crate::common::exception::{Exception, ExceptionType, Result};
use crate::storage::index::generic_key::GenericKey;
use crate::storage::index::index::{BPlusTreeIndex, Index, IndexMetadata, IndexType};
use crate::storage::table::table_heap::TableHeap;

pub type TableOid = u32;
pub type ColumnOid = u32;
pub type IndexOid = u32;

/// What the catalog knows of a table: its schema, name, oid and heap.
pub struct TableInfo<'a> {
    pub schema: Schema,
    pub name: String,
    pub table: TableHeap<'a>,
    pub oid: TableOid,
}

/// What the catalog knows of an index.
pub struct IndexInfo<'a> {
    pub key_schema: Schema,
    pub name: String,
    pub index: Box<dyn Index + 'a>,
    pub index_oid: IndexOid,
    pub table_name: String,
    /// The size of the key in bytes: 4 per integer column.
    pub key_size: usize,
    pub is_primary_key: bool,
    pub index_type: IndexType,
}

pub struct Catalog<'a> {
    bpm: &'a BufferPoolManager,
    tables: HashMap<TableOid, Arc<TableInfo<'a>>>,
    table_names: HashMap<String, TableOid>,
    indexes: HashMap<IndexOid, Arc<IndexInfo<'a>>>,
    /// table name -> (index name -> oid)
    index_names: HashMap<String, HashMap<String, IndexOid>>,
    next_table_oid: TableOid,
    next_index_oid: IndexOid,
}

impl<'a> Catalog<'a> {
    pub fn new(bpm: &'a BufferPoolManager) -> Catalog<'a> {
        Catalog { bpm, tables: HashMap::new(), table_names: HashMap::new(), indexes: HashMap::new(), index_names: HashMap::new(), next_table_oid: 0, next_index_oid: 0 }
    }

    /// Creates a table: a new heap, the next table oid. `None` if a table of that name exists.
    pub fn create_table(&mut self, table_name: &str, schema: &Schema) -> Option<Arc<TableInfo<'a>>> {
        todo!("3c-05: None for a name in use; otherwise the next oid, a TableInfo with a new heap, remembered by oid and by name, with an (empty) set of indexes for the table")
    }

    pub fn get_table(&self, table_name: &str) -> Option<Arc<TableInfo<'a>>> {
        todo!("3c-05: look the name up, then the oid")
    }

    pub fn get_table_by_oid(&self, oid: TableOid) -> Option<Arc<TableInfo<'a>>> {
        todo!("3c-05: look the oid up")
    }

    /// A table by its oid, **borrowed** from the catalog (for an executor that keeps the table for as long as the catalog lives, without
    /// cloning the `Arc`). BusTub: `GetTable(table_oid_t)` returns a `TableInfo *`.
    pub fn table_info(&self, oid: TableOid) -> Option<&TableInfo<'a>> {
        self.tables.get(&oid).map(|t| t.as_ref())
    }

    /// The names of all tables (in no particular order).
    pub fn get_table_names(&self) -> Vec<String> {
        todo!("3c-05: every table's name")
    }

    /// Creates an index on the columns `key_attrs` of `table_name`, fills it with the table's existing tuples and returns it. `Ok(None)` if
    /// the table does not exist or the table already has an index of that name; an error if the key is not made of INTEGER columns or is
    /// bigger than 64 bytes. Tuples whose key is already in the index are ignored (the tree keeps unique keys).
    pub fn create_index(&mut self, index_name: &str, table_name: &str, key_attrs: Vec<u32>, is_primary_key: bool) -> Result<Option<Arc<IndexInfo<'a>>>> {
        todo!("3c-06: Ok(None) for a missing table or a name in use; an error unless every key column is an INTEGER (and the key is 1 to 64 bytes); build the index with a key size of 4, 8, 16, 32 or 64 bytes; insert every live tuple's key (key_from_tuple) with its rid; the next index oid; remember it by oid and by (table, name)")
    }

    pub fn get_index(&self, index_name: &str, table_name: &str) -> Option<Arc<IndexInfo<'a>>> {
        todo!("3c-06: the table's index of that name, if any")
    }

    pub fn get_index_by_oid(&self, index_oid: IndexOid) -> Option<Arc<IndexInfo<'a>>> {
        todo!("3c-06: look the oid up")
    }

    /// Every index of the table (none for an unknown table), in creation order.
    pub fn get_table_indexes(&self, table_name: &str) -> Vec<Arc<IndexInfo<'a>>> {
        todo!("3c-06: the table's indexes, ordered by oid")
    }
}

#[allow(dead_code)]
type _Unused = GenericKey<4>;
