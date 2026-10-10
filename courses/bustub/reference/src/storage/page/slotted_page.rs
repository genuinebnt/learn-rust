//! A fixed-size page of variable-length records.

pub struct SlottedPage {
    // @begin 2a-c3
    size: usize,
    slots: Vec<Option<Vec<u8>>>,
    //~ _page: (),
    // @end
}

const SLOT_COST: usize = 4;

impl SlottedPage {
    pub fn new(size: usize) -> SlottedPage {
        // @begin 2a-c3
        SlottedPage { size, slots: Vec::new() }
        //~ todo!("2a-c3: an empty page of `size` bytes")
        // @end
    }

    pub fn free_space(&self) -> usize {
        // @begin 2a-c3
        self.size - self.slots.iter().flatten().map(|r| r.len() + SLOT_COST).sum::<usize>()
        //~ todo!("2a-c3: the bytes not used by records and their slot entries")
        // @end
    }

    pub fn insert(&mut self, record: &[u8]) -> Option<usize> {
        // @begin 2a-c3
        if record.len() + SLOT_COST > self.free_space() {
            return None;
        }
        let slot = match self.slots.iter().position(|s| s.is_none()) {
            Some(i) => i,
            None => {
                self.slots.push(None);
                self.slots.len() - 1
            }
        };
        self.slots[slot] = Some(record.to_vec());
        Some(slot)
        //~ todo!("2a-c3: the lowest free slot, if the record fits in the total free space")
        // @end
    }

    pub fn get(&self, slot: usize) -> Option<&[u8]> {
        // @begin 2a-c3
        self.slots.get(slot)?.as_deref()
        //~ todo!("2a-c3: the record in the slot")
        // @end
    }

    pub fn delete(&mut self, slot: usize) -> bool {
        // @begin 2a-c3
        match self.slots.get_mut(slot) {
            Some(s @ Some(_)) => {
                *s = None;
                true
            }
            _ => false,
        }
        //~ todo!("2a-c3: free the slot")
        // @end
    }

    pub fn len(&self) -> usize {
        // @begin 2a-c3
        self.slots.iter().flatten().count()
        //~ todo!("2a-c3: how many records")
        // @end
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
}
