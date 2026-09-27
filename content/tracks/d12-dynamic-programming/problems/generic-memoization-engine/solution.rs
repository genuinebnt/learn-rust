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
        Memo { cache: HashMap::new(), f: Rc::new(f) }
    }

    /// f(key), computed at most once per key.
    pub fn get(&mut self, key: K) -> V {
        if let Some(v) = self.cache.get(&key) {
            return v.clone();
        }
        // `(self.f)(self, ..)` would borrow self.f while lending all of self mutably.
        // Cloning the Rc gives the function its own handle, so self is free to lend.
        let f = Rc::clone(&self.f);
        let v = f(self, key.clone());
        self.cache.insert(key, v.clone());
        v
    }

    /// How many keys are cached.
    pub fn len(&self) -> usize {
        self.cache.len()
    }

    pub fn is_empty(&self) -> bool {
        self.cache.is_empty()
    }
}
