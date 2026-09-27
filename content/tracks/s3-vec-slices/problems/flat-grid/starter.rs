pub struct Grid {
    w: usize,
    h: usize,
    cells: Vec<u8>,
}

impl Grid {
    pub fn new(w: usize, h: usize) -> Self {
        todo!()
    }

    pub fn get(&self, x: usize, y: usize) -> Option<u8> {
        todo!()
    }

    pub fn set(&mut self, x: usize, y: usize, value: u8) -> bool {
        todo!()
    }

    pub fn row(&self, y: usize) -> Option<&[u8]> {
        todo!()
    }
}
