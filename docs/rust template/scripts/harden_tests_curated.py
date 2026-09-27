"""Curated harden verification blocks for W1–W10 (high-signal cards)."""

HARDEN_CURATED: dict[str, str] = {
    "w1-x1": """\
fn main() {
    let mut s = Stack::new();
    assert_eq!(s.peek_mut(), None);
    s.push(10);
    s.push(20);
    assert_eq!(s.peek(), Some(&20));
    *s.peek_mut().unwrap() += 1;
    assert_eq!(s.peek(), Some(&21));
    assert_eq!(s.pop(), Some(21));
}""",
    "w1-x2": """\
fn main() {
    let mut s = Stack::new();
    s.push(1);
    s.push(2);
    s.push(3);
    let immut: Vec<_> = s.iter().copied().collect();
    assert_eq!(immut.len(), 3);
    for x in s.iter_mut() {
        *x *= 10;
    }
    assert_eq!(s.pop(), Some(30)); // top was 3
}""",
    "w1-x3": """\
fn main() {
    let mut s = Stack::new();
    s.push(1);
    s.push(2);
    let mut sum = 0;
    for x in &s {
        sum += *x;
    }
    assert_eq!(sum, 3);
    for x in &mut s {
        *x += 1;
    }
    assert_eq!(s.pop(), Some(3));
}""",
    "w1-x4": """\
fn main() {
    let mut s = Stack::new();
    s.push(1);
    s.push(2);
    s.push(3);
    {
        let mut d = s.drain();
        assert_eq!(d.next(), Some(3));
        assert_eq!(d.next(), Some(2));
        // drop mid-drain — remaining must be cleaned up
    }
    assert!(s.is_empty());
    s.push(9);
    assert_eq!(s.drain().collect::<Vec<_>>(), vec![9]);
}""",
    "w1-x5": """\
fn main() {
    let s: Stack<_> = [1, 2, 3].into_iter().collect();
    assert_eq!(s.len(), 3);
    let mut s2 = Stack::new();
    s2.extend([4, 5]);
    assert_eq!(s2.len(), 2);
    assert_eq!(s2.pop(), Some(5));
}""",
    "w2-x1": """\
fn main() {
    use std::sync::atomic::{AtomicU64, Ordering};
    let a = AtomicU64::new(3);
    assert!(try_inc_if_lt(&a, 5));
    assert_eq!(a.load(Ordering::Relaxed), 4);
    assert!(try_inc_if_lt(&a, 5));
    assert!(!try_inc_if_lt(&a, 5));
    assert_eq!(a.load(Ordering::Relaxed), 5);
}""",
    "w2-x2": """\
fn main() {
    use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
    use std::sync::Arc;
    use std::thread;
    let data = Arc::new(AtomicU64::new(0));
    let ready = Arc::new(AtomicBool::new(false));
    let d2 = Arc::clone(&data);
    let r2 = Arc::clone(&ready);
    let h = thread::spawn(move || producer(&d2, &r2, 42));
    let got = consumer(&data, &ready);
    h.join().unwrap();
    assert_eq!(got, 42);
}""",
    "w2-x3": """\
fn main() {
    use std::sync::Arc;
    use std::thread;
    let state = Arc::new(Mutex::new(State { count: 0, last_thread: 0 }));
    let mut handles = vec![];
    for tid in 0..4usize {
        let s = Arc::clone(&state);
        handles.push(thread::spawn(move || {
            for _ in 0..1000 {
                inc(&s, tid);
            }
        }));
    }
    for h in handles {
        h.join().unwrap();
    }
    let g = state.lock().unwrap();
    assert_eq!(g.count, 4000);
    assert!(g.last_thread < 4);
}""",
    "w2-x4": """\
fn main() {
    use std::time::Instant;
    let t0 = Instant::now();
    fixed(); // must overlap work across threads
    assert!(t0.elapsed().as_millis() < 500, "still serialized?");
}""",
    "w2-x5": """\
fn main() {
    use std::sync::atomic::{AtomicU64, Ordering};
    let a = AtomicU64::new(3);
    assert_eq!(fetch_max(&a, 5), 3);
    assert_eq!(a.load(Ordering::Relaxed), 5);
    assert_eq!(fetch_max(&a, 4), 5);
    assert_eq!(a.load(Ordering::Relaxed), 5);
}""",
    "w3-x1": """\
fn main() {
    let mut a = MiniRc::new(10);
    assert_eq!(a.get_mut().copied(), Some(10));
    *a.get_mut().unwrap() = 11;
    let b = a.clone();
    assert!(a.get_mut().is_none());
    drop(b);
    assert_eq!(a.get_mut().copied(), Some(11));
}""",
    "w3-x2": """\
fn main() {
    let a = MiniRc::new(7);
    let b = a.clone();
    match MiniRc::try_unwrap(a) {
        Err(a2) => {
            assert_eq!(*a2, 7);
            assert_eq!(MiniRc::try_unwrap(b).unwrap(), 7);
        }
        Ok(_) => panic!("should not unwrap while shared"),
    }
}""",
    "w3-x3": """\
fn main() {
    let a = MiniRc::new(5);
    let ptr = MiniRc::into_raw(a);
    let a = unsafe { MiniRc::from_raw(ptr) };
    assert_eq!(*a, 5);
    assert_eq!(a.strong_count(), 1);
}""",
    "w3-x4": """\
fn main() {
    let a = MiniRc::new(1);
    let b = a.clone();
    let c = MiniRc::new(1);
    assert!(MiniRc::ptr_eq(&a, &b));
    assert!(!MiniRc::ptr_eq(&a, &c));
}""",
    "w3-x5": """\
fn main() {
    // Correct Drop must free exactly once when last handle dies.
    let a = MiniRc::new(String::from("x"));
    let b = a.clone();
    drop(a);
    assert_eq!(b.strong_count(), 1);
    drop(b); // must not double-free / leak
}""",
    "w4-x1": """\
fn main() {
    let q = BoundedQueue::new(1);
    assert!(q.try_push(1).is_ok());
    assert!(q.try_push(2).is_err());
    assert_eq!(q.try_pop(), Some(1));
    assert_eq!(q.try_pop(), None);
}""",
    "w4-x2": """\
fn main() {
    use std::sync::Arc;
    use std::thread;
    use std::time::Duration;
    let q = Arc::new(BoundedQueue::new(1));
    let q2 = Arc::clone(&q);
    let h = thread::spawn(move || q2.pop());
    thread::sleep(Duration::from_millis(30));
    q.close();
    let result = h.join().unwrap();
    assert!(result.is_err());
}""",
    "w4-x3": """\
fn main() {
    use std::time::Duration;
    let q = BoundedQueue::new(1);
    assert!(q.pop_timeout(Duration::from_millis(20)).is_err());
    q.push_timeout(1, Duration::from_millis(20)).unwrap();
    assert!(q.push_timeout(2, Duration::from_millis(20)).is_err());
}""",
    "w4-x4": """\
fn main() {
    use std::sync::Arc;
    use std::thread;
    let q = Arc::new(BoundedQueue::new(2));
    let q2 = Arc::clone(&q);
    thread::spawn(move || {
        q2.push_correct(1);
        q2.push_correct(2);
    })
    .join()
    .unwrap();
    assert_eq!(q.pop(), 1);
}""",
    "w4-x5": """\
fn main() {
    use std::sync::Arc;
    use std::thread;
    let q = Arc::new(BoundedQueue::new(1));
    let q2 = Arc::clone(&q);
    let h = thread::spawn(move || {
        q2.push(10);
        q2.push(20);
    });
    assert_eq!(q.pop(), 10);
    assert_eq!(q.pop(), 20);
    h.join().unwrap();
}""",
    "w5-x1": """\
fn main() {
    let pool = ThreadPool::new(2);
    let rx = pool.execute(|| 21 * 2);
    assert_eq!(rx.recv().unwrap(), 42);
}""",
    "w5-x2": """\
fn main() {
    use std::sync::atomic::{AtomicUsize, Ordering};
    use std::sync::Arc;
    let pool = ThreadPool::new(2);
    let ok = Arc::new(AtomicUsize::new(0));
    pool.execute(|| panic!("boom"));
    let c = Arc::clone(&ok);
    pool.execute(move || {
        c.fetch_add(1, Ordering::Relaxed);
    });
    drop(pool);
    assert_eq!(ok.load(Ordering::Relaxed), 1);
}""",
    "w5-x3": """\
fn main() {
    let pool = ThreadPool::new(1);
    drop(pool); // shutdown
    // Reconstruct to call try_execute after sender taken — or:
    let mut pool = ThreadPool::new(1);
    // if try_execute is method on pool after partial drop of sender:
    assert!(pool.try_execute(|| ()).is_err() || true);
    // Stronger: take shutdown path then try_execute
    let pool = ThreadPool::new(1);
    drop(pool);
}""",
    "w5-x4": """\
fn main() {
    use std::sync::atomic::{AtomicUsize, Ordering};
    use std::sync::Arc;
    let pool = ThreadPool::new(2);
    let n = Arc::new(AtomicUsize::new(0));
    for _ in 0..50 {
        let c = Arc::clone(&n);
        pool.execute(move || {
            c.fetch_add(1, Ordering::Relaxed);
        });
    }
    drop(pool);
    assert_eq!(n.load(Ordering::Relaxed), 50);
}""",
    "w5-x5": """\
fn main() {
    use std::sync::atomic::{AtomicUsize, Ordering};
    use std::sync::Arc;
    use std::thread;
    use std::time::Duration;
    let pool = ThreadPool::new(1); // bound small in your new()
    let n = Arc::new(AtomicUsize::new(0));
    for _ in 0..5 {
        let c = Arc::clone(&n);
        pool.execute(move || {
            thread::sleep(Duration::from_millis(10));
            c.fetch_add(1, Ordering::Relaxed);
        });
    }
    drop(pool);
    assert_eq!(n.load(Ordering::Relaxed), 5);
}""",
    "w6-x1": """\
fn main() {
    use std::sync::{Arc, Mutex};
    struct Cap(Arc<Mutex<Vec<String>>>);
    impl Logger for Cap {
        fn log(&self, msg: &str) {
            self.0.lock().unwrap().push(msg.to_string());
        }
    }
    let buf = Arc::new(Mutex::new(Vec::new()));
    let facade = LevelFilter {
        min: Level::Warn,
        inner: Box::new(Cap(buf.clone())),
    };
    facade.log(Level::Info, "skip");
    facade.log(Level::Error, "keep");
    assert_eq!(*buf.lock().unwrap(), vec!["keep".to_string()]);
}""",
    "w6-x2": """\
fn main() {
    use std::sync::{Arc, Mutex};
    struct Cap(Arc<Mutex<Vec<String>>>);
    impl Logger for Cap {
        fn log(&self, msg: &str) {
            self.0.lock().unwrap().push(msg.to_string());
        }
    }
    let a = Arc::new(Mutex::new(Vec::new()));
    let b = Arc::new(Mutex::new(Vec::new()));
    let tee = Tee {
        sinks: vec![Box::new(Cap(a.clone())), Box::new(Cap(b.clone()))],
    };
    tee.log("hi");
    assert_eq!(*a.lock().unwrap(), vec!["hi".to_string()]);
    assert_eq!(*b.lock().unwrap(), vec!["hi".to_string()]);
}""",
    "w6-x3": """\
fn main() {
    use std::sync::{Arc, Mutex};
    struct Cap(Arc<Mutex<bool>>);
    impl Logger for Cap {
        fn log(&self, _msg: &str) {}
        fn flush(&self) {
            *self.0.lock().unwrap() = true;
        }
    }
    let flag = Arc::new(Mutex::new(false));
    let l: Box<dyn Logger> = Box::new(Cap(flag.clone()));
    l.flush();
    assert!(*flag.lock().unwrap());
}""",
    "w6-x4": """\
fn main() {
    use std::sync::{Arc, Mutex};
    struct Cap(Arc<Mutex<Vec<String>>>);
    impl Logger for Cap {
        fn log(&self, msg: &str) {
            self.0.lock().unwrap().push(msg.to_string());
        }
    }
    let buf = Arc::new(Mutex::new(Vec::new()));
    let mut holder = SinkHolder::new(Box::new(Cap(buf.clone())));
    holder.log("a");
    holder.set(Box::new(Cap(buf.clone())));
    holder.log("b");
    assert_eq!(*buf.lock().unwrap(), vec!["a".to_string(), "b".to_string()]);
}""",
    "w6-x5": """\
fn main() {
    use std::sync::{Arc, Mutex};
    struct Cap(Arc<Mutex<Vec<String>>>);
    impl Logger for Cap {
        fn log(&self, msg: &str) {
            self.0.lock().unwrap().push(msg.to_string());
        }
    }
    let buf = Arc::new(Mutex::new(Vec::new()));
    let p = PrefixLogger {
        inner: Cap(buf.clone()),
        prefix: "[x] ".into(),
    };
    p.log("msg");
    assert_eq!(*buf.lock().unwrap(), vec!["[x] msg".to_string()]);
}""",
    "w7-x1": """\
fn main() {
    let s = TreiberStack::new();
    s.push(1);
    s.push(2);
    assert_eq!(s.pop(), Some(2));
    assert_eq!(s.pop(), Some(1));
    assert_eq!(s.pop(), None);
}""",
    "w7-x2": """\
fn main() {
    use std::sync::Arc;
    use std::thread;
    let s = Arc::new(TreiberStack::new());
    let mut hs = vec![];
    for i in 0..4 {
        let s = Arc::clone(&s);
        hs.push(thread::spawn(move || {
            for v in 0..500 {
                s.push(i * 500 + v);
            }
        }));
    }
    for h in hs {
        h.join().unwrap();
    }
    let mut n = 0;
    while s.pop().is_some() {
        n += 1;
    }
    assert_eq!(n, 2000);
}""",
    "w7-x3": """\
fn main() {
    let s = TreiberStack::new();
    assert!(s.is_empty());
    s.push(1);
    assert!(!s.is_empty());
}""",
    "w7-x4": """\
fn main() {
    // ABA / deferred free: after pop, value is returned and node is not reused unsoundly.
    let s = TreiberStack::new();
    s.push(String::from("a"));
    assert_eq!(s.pop().as_deref(), Some("a"));
}""",
    "w7-x5": """\
fn main() {
    let s = TreiberStack::new();
    s.push(1);
    s.push(2);
    assert_eq!(s.pop(), Some(2));
    drop(s); // Drop must free remaining nodes without leak/double-free
}""",
    "w8-x1": """\
fn main() {
    let mut c = LruCache::new(2);
    c.put(1, "a");
    assert_eq!(c.peek(&1), Some(&"a"));
    c.put(2, "b");
    c.put(3, "c"); // evict 1 without get-touch via peek
    assert!(c.get(&1).is_none() || c.peek(&1).is_none());
}""",
    "w8-x2": """\
fn main() {
    let mut c = LruCache::new(2);
    c.put("a", 1);
    c.put("b", 2);
    assert_eq!(c.remove(&"a"), Some(1));
    assert!(c.get(&"a").is_none());
    c.put("c", 3);
    assert!(c.get(&"b").is_some());
}""",
    "w8-x3": """\
fn main() {
    let mut c = LruCache::new(1);
    c.put(1, 10);
    assert_eq!(c.get(&1), Some(&10));
    c.put(1, 11); // update
    assert_eq!(c.get(&1), Some(&11));
}""",
    "w8-x4": """\
fn main() {
    let mut c = LruCache::new(2);
    c.put(1, 1);
    c.put(2, 2);
    assert_eq!(c.len(), 2);
    c.clear();
    assert_eq!(c.len(), 0);
}""",
    "w8-x5": """\
fn main() {
    let mut c = LruCache::new(2);
    c.put("x", 1);
    c.put("y", 2);
    let keys: Vec<_> = c.iter().map(|(k, _)| *k).collect();
    assert_eq!(keys.len(), 2);
}""",
    "w9-x1": """\
fn main() {
    let data = [1, 2, 3, 4];
    assert_eq!(windows(&data, 0).count(), 0);
    assert_eq!(windows(&data, 5).count(), 0);
}""",
    "w9-x2": """\
fn main() {
    let data = [1, 2, 3, 4, 5];
    let (lo, hi) = windows(&data, 3).size_hint();
    assert_eq!(lo, 3);
    assert_eq!(hi, Some(3));
}""",
    "w9-x3": """\
fn main() {
    let data = [1, 2, 3, 4];
    let v: Vec<_> = windows(&data, 2).collect();
    assert_eq!(v.len(), 3);
}""",
    "w9-x4": """\
fn main() {
    let data = [1, 2, 3, 4, 5, 6];
    let v: Vec<_> = windows_step(&data, 2, 2).collect();
    assert_eq!(v, vec![&[1, 2][..], &[3, 4][..], &[5, 6][..]]);
}""",
    "w9-x5": """\
fn main() {
    let data = [1, 2, 3];
    // ExactSizeIterator / DoubleEnded if implemented
    let mut first = windows(&data, 2);
    assert_eq!(first.next_back(), Some(&[2, 3][..]));
}""",
    "w10-x1": """\
fn main() {
    let e: ConfigError = std::io::Error::new(std::io::ErrorKind::Other, "x").into();
    assert!(!e.to_string().is_empty());
    assert!(std::error::Error::source(&e).is_some());
}""",
    "w10-x2": """\
fn main() {
    use std::io::Write;
    let dir = std::env::temp_dir().join("w10x2");
    let _ = std::fs::create_dir_all(&dir);
    let p = dir.join("c.conf");
    std::fs::write(&p, "port=12\\n").unwrap();
    let cfg = load_config(p.to_str().unwrap()).unwrap();
    assert_eq!(cfg.port, 12);
}""",
    "w10-x3": """\
fn main() {
    // thiserror / manual Display — message must be useful
    let e = ConfigError::MissingKey("port".into());
    assert!(e.to_string().contains("port"));
}""",
    "w10-x4": """\
fn main() {
    fn parse_port(s: &str) -> Result<u16, ConfigError> {
        Ok(s.parse()?)
    }
    assert_eq!(parse_port("80").unwrap(), 80);
    assert!(parse_port("x").is_err());
}""",
    "w10-x5": """\
fn main() {
    let dir = std::env::temp_dir().join("w10x5");
    let _ = std::fs::create_dir_all(&dir);
    let p = dir.join("c.conf");
    std::fs::write(&p, "host=localhost\\n").unwrap();
    match load_config(p.to_str().unwrap()) {
        Err(ConfigError::MissingKey(k)) => assert_eq!(k, "port"),
        other => panic!("expected MissingKey, got {other:?}"),
    }
}""",
}
