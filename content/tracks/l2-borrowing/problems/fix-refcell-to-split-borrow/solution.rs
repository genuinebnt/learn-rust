pub struct Cart {
    items: Vec<u32>,
    total: u32,
}

impl Cart {
    pub fn new() -> Self {
        Cart { items: Vec::new(), total: 0 }
    }

    pub fn add(&mut self, price: u32) {
        self.items.push(price);
        self.total += price;
    }

    /// Doubles every price and keeps the total in step.
    pub fn double_all(&mut self) {
        for p in self.items.iter_mut() {
            self.total += *p;
            *p *= 2;
        }
    }

    pub fn total(&self) -> u32 {
        self.total
    }

    pub fn items(&self) -> Vec<u32> {
        self.items.to_vec()
    }
}
