//! Slot numbers handed out from a counter and a free list.

pub struct SlotAllocator {
    next: usize,
    free_list: Vec<usize>,
    in_use: usize,
}

impl SlotAllocator {
    pub fn new() -> SlotAllocator {
        SlotAllocator { next: 0, free_list: Vec::new(), in_use: 0 }
    }

    pub fn allocate(&mut self) -> usize {
        self.in_use += 1;
        if let Some(slot) = self.free_list.pop() {
            return slot;
        }
        self.next += 1;
        self.next - 1
    }

    /// Takes `slot` back; false if it was not in use.
    pub fn free(&mut self, slot: usize) -> bool {
        self.free_list.push(slot);
        self.in_use = self.in_use.saturating_sub(1);
        true
    }

    pub fn in_use(&self) -> usize {
        self.in_use
    }
}

impl Default for SlotAllocator {
    fn default() -> Self {
        SlotAllocator::new()
    }
}
