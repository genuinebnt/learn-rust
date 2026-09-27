pub enum SmallVec4<T> {
    Inline { items: [Option<T>; 4], len: usize },
    Heap(Vec<T>),
}

impl<T> SmallVec4<T> {
    pub fn new() -> Self {
        todo!()
    }

    pub fn push(&mut self, value: T) {
        todo!()
    }

    pub fn len(&self) -> usize {
        todo!()
    }

    pub fn get(&self, i: usize) -> Option<&T> {
        todo!()
    }

    pub fn is_inline(&self) -> bool {
        todo!()
    }
}
