//! The registers of a HyperLogLog sketch, and merging them.

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Registers {
    bits: u32,
    regs: Vec<u8>,
}

#[derive(Debug, PartialEq, Eq)]
pub struct SizeMismatch;

impl Registers {
    /// `2^bits` registers, `bits` in `1..=16`.
    pub fn new(bits: u32) -> Registers {
        let bits = bits.clamp(1, 16);
        Registers { bits, regs: vec![0; 1 << bits] }
    }

    /// Records one hashed element.
    pub fn update(&mut self, hash: u64) {
        let idx = (hash >> (64 - self.bits)) as usize;
        let rest = hash << self.bits;
        let rank = (rest.leading_zeros().min(64 - self.bits) + 1) as u8;
        self.regs[idx] = self.regs[idx].max(rank);
    }

    pub fn registers(&self) -> &[u8] {
        &self.regs
    }

    /// Absorbs another sketch of the same size.
    pub fn merge(&mut self, other: &Registers) -> Result<(), SizeMismatch> {
        if self.bits != other.bits {
            return Err(SizeMismatch);
        }
        for (a, b) in self.regs.iter_mut().zip(&other.regs) {
            // @begin 0d-c5
            *a = (*a).max(*b);
            //~ *a = a.saturating_add(*b);
            // @end
        }
        Ok(())
    }
}
