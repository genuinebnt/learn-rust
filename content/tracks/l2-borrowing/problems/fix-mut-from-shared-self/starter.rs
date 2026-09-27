pub struct Stack {
    items: Vec<i32>,
}

impl Stack {
    pub fn new() -> Self {
        Stack { items: Vec::new() }
    }

    pub fn push(&mut self, x: i32) {
        self.items.push(x);
    }

    /// The top item, for editing in place.
    pub fn top_mut(&self) -> Option<&mut i32> {
        self.items.last_mut()
    }
}

impl Stack {
    /// For tests.
    pub fn items_for_test(&self) -> Vec<i32> {
        self.items.to_vec()
    }
}
