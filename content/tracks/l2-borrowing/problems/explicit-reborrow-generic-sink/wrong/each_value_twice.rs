pub trait Sink {
    fn put(&mut self, x: i32);
}

impl Sink for Vec<i32> {
    fn put(&mut self, x: i32) {
        self.push(x);
    }
}

impl<S: Sink + ?Sized> Sink for &mut S {
    fn put(&mut self, x: i32) {
        (**self).put(x);
    }
}

/// Don't change this.
pub fn emit_all<S: Sink>(mut sink: S, xs: &[i32]) {
    for &x in xs {
        sink.put(x);
    }
}

pub fn emit_twice(sink: &mut Vec<i32>, xs: &[i32]) {
    for &x in xs {
        sink.put(x);
        sink.put(x);
    }
}
