pub fn with_rollback(v: &mut Vec<i32>, f: impl FnOnce(&mut Vec<i32>)) {
    struct Guard<'a> {
        v: &'a mut Vec<i32>,
        armed: bool,
    }

    impl Drop for Guard<'_> {
        fn drop(&mut self) {
            if self.armed {
                self.v.clear();
            }
        }
    }

    let mut guard = Guard { v, armed: true };
    f(guard.v);
    guard.armed = false;
}
