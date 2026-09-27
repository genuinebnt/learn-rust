use std::cell::RefCell;

pub struct Cart {
    items: RefCell<Vec<u32>>,
    total: u32,
}

impl Cart {
    pub fn new() -> Self {
        Cart { items: RefCell::new(Vec::new()), total: 0 }
    }

    pub fn add(&mut self, price: u32) {
        self.items.borrow_mut().push(price);
        self.total += price;
    }

    /// Doubles every price and keeps the total in step.
    pub fn double_all(&mut self) {
        for p in self.items.borrow_mut().iter_mut() {
            self.total += *p;
            *p *= 2;
        }
    }

    pub fn total(&self) -> u32 {
        self.total
    }

    pub fn items(&self) -> Vec<u32> {
        self.items.borrow().to_vec()
    }
}
