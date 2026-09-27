use std::collections::HashMap;
use std::hash::Hash;
use std::rc::Rc;

pub struct Memo<'a, K, V> {
    cache: HashMap<K, V>,
    // Why an Rc? See the hints.
    f: Rc<dyn Fn(&mut Memo<'a, K, V>, K) -> V + 'a>,
}

impl<'a, K: Eq + Hash + Clone, V: Clone> Memo<'a, K, V> {
    pub fn new(f: impl Fn(&mut Memo<'a, K, V>, K) -> V + 'a) -> Self {
        todo!()
    }

    /// f(key), computed at most once per key.
    pub fn get(&mut self, key: K) -> V {
        todo!()
    }

    /// How many keys are cached.
    pub fn len(&self) -> usize {
        todo!()
    }

    pub fn is_empty(&self) -> bool {
        todo!()
    }
}
