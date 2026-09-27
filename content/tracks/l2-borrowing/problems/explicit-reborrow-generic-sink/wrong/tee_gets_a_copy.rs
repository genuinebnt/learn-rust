pub trait Sink {
    fn put(&mut self, x: i32);
    /// How many values this sink has taken.
    fn len(&self) -> usize;
}

impl Sink for Vec<i32> {
    fn put(&mut self, x: i32) {
        self.push(x);
    }

    fn len(&self) -> usize {
        Vec::len(self)
    }
}

/// Counts values without keeping them.
pub struct Count(pub usize);

impl Sink for Count {
    fn put(&mut self, _: i32) {
        self.0 += 1;
    }

    fn len(&self) -> usize {
        self.0
    }
}

/// Sends every value to both sinks, `A` first.
pub struct Tee<A, B>(pub A, pub B);

impl<A: Sink, B: Sink> Sink for Tee<A, B> {
    fn put(&mut self, x: i32) {
        self.0.put(x);
        self.1.put(x);
    }

    fn len(&self) -> usize {
        self.0.len()
    }
}

/// Emits every value into `sink`. Like std's generic sinks, it takes the sink by value.
pub fn emit_all<S: Sink>(mut sink: S, xs: &[i32]) {
    for &x in xs {
        sink.put(x);
    }
}

impl<S: Sink + ?Sized> Sink for &mut S {
    fn put(&mut self, x: i32) {
        (**self).put(x);
    }

    fn len(&self) -> usize {
        (**self).len()
    }
}

impl<S: Sink + ?Sized> Sink for Box<S> {
    fn put(&mut self, x: i32) {
        (**self).put(x);
    }

    fn len(&self) -> usize {
        (**self).len()
    }
}

/// Emits `xs` into `sink` twice, then into `sink` and `count` together through a `Tee`. Returns how many values
/// `sink` holds afterwards.
pub fn pipeline(sink: &mut Vec<i32>, count: &mut Count, xs: &[i32]) -> usize {
    emit_all(&mut *sink, xs);
    emit_all(&mut *sink, xs);
    emit_all(Tee(Vec::new(), count), xs);
    sink.len()
}

/// Emits `xs` into every sink and returns their lengths afterwards.
pub fn fan_out(sinks: &mut [Box<dyn Sink>], xs: &[i32]) -> Vec<usize> {
    for s in sinks.iter_mut() {
        emit_all(s, xs);
    }
    sinks.iter().map(|s| s.len()).collect()
}
