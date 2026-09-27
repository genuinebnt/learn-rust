use std::collections::HashMap;
use std::hash::Hash;
use std::rc::Rc;

pub struct Memo<'a, K, V> {
    cache: HashMap<K, V>,
    f: Rc<dyn Fn(&mut Memo<'a, K, V>, K) -> V + 'a>,
}

impl<'a, K: Eq + Hash + Clone, V: Clone> Memo<'a, K, V> {
    pub fn new(f: impl Fn(&mut Memo<'a, K, V>, K) -> V + 'a) -> Self {
        Memo { cache: HashMap::new(), f: Rc::new(f) }
    }

    pub fn get(&mut self, key: K) -> V {
        if let Some(v) = self.cache.get(&key) {
            return v.clone();
        }
        let f = Rc::clone(&self.f);
        f(self, key)
    }

    pub fn len(&self) -> usize {
        self.cache.len()
    }

    pub fn is_empty(&self) -> bool {
        self.cache.is_empty()
    }
}
