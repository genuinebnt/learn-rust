pub struct FlowNetwork {
    adj: Vec<Vec<usize>>,
    to: Vec<usize>,
    cap: Vec<u64>,
}

impl FlowNetwork {
    pub fn new(n: usize) -> Self {
        todo!()
    }

    pub fn add_edge(&mut self, u: usize, v: usize, cap: u64) {
        todo!()
    }

    pub fn max_flow(&mut self, s: usize, t: usize) -> u64 {
        todo!()
    }
}
