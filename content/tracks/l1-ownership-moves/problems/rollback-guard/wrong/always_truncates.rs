pub fn with_rollback(v: &mut Vec<i32>, f: impl FnOnce(&mut Vec<i32>)) {
    struct Guard<'a> {
        v: &'a mut Vec<i32>,
        len: usize,
    }

    impl Drop for Guard<'_> {
        fn drop(&mut self) {
            self.v.truncate(self.len);
        }
    }

    let len = v.len();
    let guard = Guard { v, len };
    f(guard.v);
}
