//! A bitmap of which pages of a file are in use.

#[derive(Debug, PartialEq, Eq)]
pub enum FreeError {
    DoubleFree,
    OutOfRange,
}

pub struct PageBitmap {
    // @begin 1a-c3
    used: Vec<bool>,
    count: usize,
    //~ _map: (),
    // @end
}

impl PageBitmap {
    pub fn new(capacity: usize) -> PageBitmap {
        // @begin 1a-c3
        PageBitmap { used: vec![false; capacity], count: 0 }
        //~ todo!("1a-c3: every page free")
        // @end
    }

    /// The lowest free page, marked used.
    pub fn allocate(&mut self) -> Option<usize> {
        // @begin 1a-c3
        let at = self.used.iter().position(|u| !u)?;
        self.used[at] = true;
        self.count += 1;
        Some(at)
        //~ todo!("1a-c3: find the lowest free page")
        // @end
    }

    pub fn free(&mut self, page: usize) -> Result<(), FreeError> {
        // @begin 1a-c3
        match self.used.get_mut(page) {
            None => Err(FreeError::OutOfRange),
            Some(false) => Err(FreeError::DoubleFree),
            Some(u) => {
                *u = false;
                self.count -= 1;
                Ok(())
            }
        }
        //~ todo!("1a-c3: give the page back, or say why not")
        // @end
    }

    pub fn is_allocated(&self, page: usize) -> bool {
        // @begin 1a-c3
        self.used.get(page).copied().unwrap_or(false)
        //~ todo!("1a-c3: is this page in use")
        // @end
    }

    pub fn used(&self) -> usize {
        // @begin 1a-c3
        self.count
        //~ todo!("1a-c3: how many pages are in use")
        // @end
    }
}
