//! A page store whose snapshots read the past.

use std::collections::BTreeMap;

pub type SnapshotId = u64;

pub struct VersionedPages {
    _versions: (),
}

impl VersionedPages {
    pub fn new() -> VersionedPages {
        todo!("1a-c4: an empty store")
    }

    pub fn write(&mut self, page: u32, value: u64) {
        todo!("1a-c4: add a version, never overwrite")
    }

    pub fn read(&self, page: u32) -> Option<u64> {
        todo!("1a-c4: the newest value")
    }

    pub fn snapshot(&mut self) -> SnapshotId {
        todo!("1a-c4: remember how far the store had got")
    }

    pub fn read_at(&self, snapshot: SnapshotId, page: u32) -> Option<u64> {
        todo!("1a-c4: the newest value written no later than the snapshot")
    }

    pub fn drop_snapshot(&mut self, id: SnapshotId) -> bool {
        todo!("1a-c4: forget the snapshot")
    }
}

impl Default for VersionedPages {
    fn default() -> Self {
        VersionedPages::new()
    }
}
