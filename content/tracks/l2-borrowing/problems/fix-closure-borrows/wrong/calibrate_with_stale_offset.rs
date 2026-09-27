/// A nested list of readings.
pub enum Item {
    One(i32),
    Many(Vec<Item>),
}

pub struct Meter {
    pub readings: Vec<i32>,
    pub offset: i32,
    pub log: Vec<String>,
}

/// Calls `f` on every reading in `items`, depth first, in order.
fn walk<F: FnMut(i32)>(items: &[Item], f: &mut F) {
    for it in items {
        match it {
            Item::One(x) => f(*x),
            Item::Many(inner) => walk(inner, f),
        }
    }
}

impl Meter {
    fn offset(&self) -> i32 {
        self.offset
    }

    /// Adds the offset to every recorded reading.
    pub fn calibrate(&mut self) {
        let offset = self.offset().max(0);
        self.readings.iter_mut().for_each(|r| *r += offset);
    }

    /// Records every value of every batch. After each batch, logs "batch <i>: <n> above" where n counts the
    /// values above `limit` so far. Returns the final count.
    pub fn record(&mut self, batches: &[&[i32]], limit: i32) -> usize {
        let mut above = 0;
        for (i, batch) in batches.iter().enumerate() {
            let mut add = |x: i32| {
                self.readings.push(x);
                if x > limit {
                    above += 1;
                }
            };
            for &x in *batch {
                add(x);
            }
            self.log.push(format!("batch {i}: {above} above"));
        }
        above
    }

    /// Records every reading in `items`, depth first, and returns their sum.
    pub fn record_nested(&mut self, items: &[Item]) -> i64 {
        let mut sum = 0;
        walk(items, &mut |x| {
            self.readings.push(x);
            sum += x as i64;
        });
        sum
    }
}
