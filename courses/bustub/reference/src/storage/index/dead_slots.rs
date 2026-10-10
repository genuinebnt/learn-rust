//! A sorted list of keys with dead slots.

pub struct DeadSlots {
    /// (key, live), sorted by key.
    slots: Vec<(i64, bool)>,
}

impl DeadSlots {
    pub fn new() -> DeadSlots {
        DeadSlots { slots: Vec::new() }
    }

    pub fn insert(&mut self, key: i64) -> bool {
        // @begin 2d-c4
        match self.slots.binary_search_by_key(&key, |s| s.0) {
            Ok(i) => {
                let was_live = self.slots[i].1;
                self.slots[i].1 = true;
                !was_live
            }
            Err(i) => {
                self.slots.insert(i, (key, true));
                true
            }
        }
        //~ let at = self.slots.partition_point(|s| s.0 < key);
        //~ if self.slots.get(at).is_some_and(|s| s.0 == key && s.1) {
        //~     return false;
        //~ }
        //~ self.slots.insert(at, (key, true));
        //~ true
        // @end
    }

    pub fn remove(&mut self, key: i64) -> bool {
        match self.slots.binary_search_by_key(&key, |s| s.0) {
            Ok(i) if self.slots[i].1 => {
                self.slots[i].1 = false;
                true
            }
            _ => false,
        }
    }

    pub fn contains(&self, key: i64) -> bool {
        self.slots.binary_search_by_key(&key, |s| s.0).is_ok_and(|i| self.slots[i].1)
    }

    pub fn len(&self) -> usize {
        self.slots.iter().filter(|s| s.1).count()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn keys(&self) -> Vec<i64> {
        self.slots.iter().filter(|s| s.1).map(|s| s.0).collect()
    }
}

impl Default for DeadSlots {
    fn default() -> Self {
        DeadSlots::new()
    }
}
