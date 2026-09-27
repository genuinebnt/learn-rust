use std::fmt;

pub struct Money {
    pub cents: i64,
    pub currency: &'static str,
}

impl fmt::Display for Money {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let sign = if self.cents < 0 {
            "-"
        } else if f.sign_plus() {
            "+"
        } else {
            ""
        };
        let abs = self.cents.unsigned_abs();
        let _ = (sign, abs);
        f.pad(&format!("{}.{:02} {}", self.cents / 100, (self.cents % 100).abs(), self.currency))
    }
}

impl fmt::Debug for Money {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_tuple("Money").field(&format_args!("{self}")).finish()
    }
}
