#[derive(Default)]
pub struct MedianFinder {
    values: Vec<i32>,
}

impl MedianFinder {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn add_num(&mut self, num: i32) {
        self.values.push(num);
    }

    pub fn remove_num(&mut self, num: i32) -> bool {
        match self.values.iter().position(|&x| x == num) {
            Some(i) => {
                self.values.swap_remove(i);
                true
            }
            None => false,
        }
    }

    pub fn find_median(&self) -> Option<f64> {
        let mut s = self.values.clone();
        s.sort_unstable();
        let n = s.len();
        match n {
            0 => None,
            _ if n % 2 == 1 => Some(s[n / 2] as f64),
            _ => Some((s[n / 2 - 1] as f64 + s[n / 2] as f64) / 2.0),
        }
    }
}
