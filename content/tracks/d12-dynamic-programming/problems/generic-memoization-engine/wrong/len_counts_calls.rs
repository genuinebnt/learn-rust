use std::collections::HashMap;
use std::hash::Hash;
use std::rc::Rc;

pub struct Memo<'a, K, V> {
    cache: HashMap<K, V>,
    gets: usize,
    f: Rc<dyn Fn(&mut Memo<'a, K, V>, K) -> V + 'a>,
}

impl<'a, K: Eq + Hash + Clone, V: Clone> Memo<'a, K, V> {
    pub fn new(f: impl Fn(&mut Memo<'a, K, V>, K) -> V + 'a) -> Self {
        Memo { cache: HashMap::new(), gets: 0, f: Rc::new(f) }
    }

    pub fn get(&mut self, key: K) -> V {
        self.gets += 1;
        if let Some(v) = self.cache.get(&key) {
            return v.clone();
        }
        let f = Rc::clone(&self.f);
        let v = f(self, key.clone());
        self.cache.insert(key, v.clone());
        v
    }

    pub fn len(&self) -> usize {
        self.gets
    }

    pub fn is_empty(&self) -> bool {
        self.gets == 0
    }
}
