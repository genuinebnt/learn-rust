//! Which frame holds which page: two maps that must mirror each other.

use std::collections::HashMap;

#[derive(Default)]
pub struct PageTable {
    page_to_frame: HashMap<u32, u32>,
    frame_to_page: HashMap<u32, u32>,
}

impl PageTable {
    pub fn new() -> PageTable {
        PageTable::default()
    }

    pub fn insert(&mut self, page: u32, frame: u32) {
        if let Some(old_frame) = self.page_to_frame.remove(&page) {
            self.frame_to_page.remove(&old_frame);
        }
        if let Some(old_page) = self.frame_to_page.remove(&frame) {
            self.page_to_frame.remove(&old_page);
        }
        self.page_to_frame.insert(page, frame);
        self.frame_to_page.insert(frame, page);
    }

    /// Forgets `page`; returns the frame that held it.
    pub fn remove_page(&mut self, page: u32) -> Option<u32> {
        // @begin 1f-c5
        let frame = self.page_to_frame.remove(&page)?;
        self.frame_to_page.remove(&frame);
        Some(frame)
        //~ self.page_to_frame.remove(&page)
        // @end
    }

    pub fn frame_of(&self, page: u32) -> Option<u32> {
        self.page_to_frame.get(&page).copied()
    }

    pub fn page_of(&self, frame: u32) -> Option<u32> {
        self.frame_to_page.get(&frame).copied()
    }

    pub fn len(&self) -> usize {
        self.page_to_frame.len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
}
