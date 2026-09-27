"""Hand-crafted verification blocks for core exercises lacking asserts (W1–W26, W28)."""

CORE_MAIN: dict[int, str] = {
    1: """\
fn main() {
    let mut s: Stack<String> = Stack::new();
    assert!(s.is_empty());
    s.push("a".to_string());
    s.push("b".to_string());
    assert_eq!(s.peek(), Some(&"b".to_string()));
    assert_eq!(s.pop(), Some("b".to_string()));
    assert_eq!(s.len(), 1);
    assert_eq!(s.pop(), Some("a".to_string()));
    assert!(s.is_empty());
    assert_eq!(s.pop(), None);
}""",
    2: """\
fn main() {
    use std::sync::atomic::{AtomicU64, Ordering};
    use std::sync::Arc;
    let counter = Arc::new(AtomicU64::new(0));
    let handles: Vec<_> = (0..10)
        .map(|_| {
            let counter = Arc::clone(&counter);
            thread::spawn(move || {
                for _ in 0..100_000 {
                    counter.fetch_add(1, Ordering::Relaxed);
                }
            })
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    assert_eq!(counter.load(Ordering::Relaxed), 1_000_000);
}""",
    3: """\
fn main() {
    let a = MiniRc::new(vec![1, 2, 3]);
    assert_eq!(a.strong_count(), 1);
    let b = a.clone();
    assert_eq!(a.strong_count(), 2);
    assert_eq!(*b, vec![1, 2, 3]);
    drop(b);
    assert_eq!(a.strong_count(), 1);
}""",
    4: """\
fn main() {
    use std::sync::Arc;
    use std::thread;
    use std::time::Duration;
    let q = Arc::new(BoundedQueue::new(2));
    let q2 = Arc::clone(&q);
    let producer = thread::spawn(move || {
        q2.push(1);
        q2.push(2);
        q2.push(3);
    });
    thread::sleep(Duration::from_millis(30));
    assert_eq!(q.pop(), 1);
    assert_eq!(q.pop(), 2);
    assert_eq!(q.pop(), 3);
    producer.join().unwrap();
}""",
    5: """\
fn main() {
    use std::sync::atomic::{AtomicUsize, Ordering};
    use std::sync::Arc;
    let pool = ThreadPool::new(4);
    let counter = Arc::new(AtomicUsize::new(0));
    for _ in 0..100 {
        let c = Arc::clone(&counter);
        pool.execute(move || {
            c.fetch_add(1, Ordering::Relaxed);
        });
    }
    drop(pool);
    assert_eq!(counter.load(Ordering::Relaxed), 100);
}""",
    6: """\
fn main() {
    use std::sync::{Arc, Mutex};
    struct SharedLogger(Arc<Mutex<Vec<String>>>);
    impl Logger for SharedLogger {
        fn log(&self, msg: &str) {
            self.0.lock().unwrap().push(msg.to_string());
        }
    }
    let buf = Arc::new(Mutex::new(Vec::<String>::new()));
    let loggers: Vec<Box<dyn Logger>> = vec![
        Box::new(SharedLogger(buf.clone())),
        Box::new(PrefixLogger {
            inner: Box::new(SharedLogger(buf.clone())),
            prefix: "[ERROR] ".to_string(),
        }),
    ];
    for l in &loggers {
        l.log("system startup");
    }
    assert_eq!(
        *buf.lock().unwrap(),
        vec![
            "system startup".to_string(),
            "[ERROR] system startup".to_string()
        ]
    );
}""",
    7: """\
fn main() {
    use std::sync::Arc;
    use std::thread;
    let stack = Arc::new(TreiberStack::new());
    let mut handles = vec![];
    for t in 0..4 {
        let s = Arc::clone(&stack);
        handles.push(thread::spawn(move || {
            for i in 0..1000 {
                s.push(t * 1000 + i);
            }
        }));
    }
    for h in handles {
        h.join().unwrap();
    }
    let mut count = 0;
    while stack.pop().is_some() {
        count += 1;
    }
    assert_eq!(count, 4000);
    assert_eq!(stack.pop(), None);
}""",
    8: """\
fn main() {
    let mut cache = LruCache::new(2);
    cache.put("a", 1);
    cache.put("b", 2);
    assert_eq!(cache.get(&"a"), Some(&1));
    cache.put("c", 3);
    assert_eq!(cache.get(&"b"), None);
    assert_eq!(cache.get(&"a"), Some(&1));
    assert_eq!(cache.get(&"c"), Some(&3));
}""",
    9: """\
fn main() {
    let data = [1, 2, 3, 4, 5];
    let got: Vec<&[i32]> = windows(&data, 3).collect();
    assert_eq!(got, vec![&[1, 2, 3][..], &[2, 3, 4][..], &[3, 4, 5][..]]);
    let sums: Vec<i32> = windows(&data, 2).map(|w| w.iter().sum()).collect();
    assert_eq!(sums, vec![3, 5, 7, 9]);
    assert_eq!(windows(&data, 6).count(), 0);
}""",
    10: """\
fn main() {
    use std::io::Write;
    let dir = std::env::temp_dir().join("w10_config_test");
    let _ = std::fs::create_dir_all(&dir);
    let path = dir.join("app.conf");
    {
        let mut f = std::fs::File::create(&path).unwrap();
        writeln!(f, "port=8080").unwrap();
    }
    let cfg = load_config(path.to_str().unwrap()).unwrap();
    assert_eq!(cfg.port, 8080);

    let bad = dir.join("bad.conf");
    {
        let mut f = std::fs::File::create(&bad).unwrap();
        writeln!(f, "port=xyz").unwrap();
    }
    assert!(load_config(bad.to_str().unwrap()).is_err());

    let missing = dir.join("missing.conf");
    {
        let mut f = std::fs::File::create(&missing).unwrap();
        writeln!(f, "host=localhost").unwrap();
    }
    assert!(load_config(missing.to_str().unwrap()).is_err());
}""",
    11: """\
fn main() {
    let req = RequestBuilder::new("https://example.com")
        .header("Accept", "application/json")
        .timeout_ms(1500)
        .build()
        .unwrap();
    assert_eq!(req.url, "https://example.com");
    assert!(req.headers.iter().any(|(k, v)| k == "Accept" && v == "application/json"));
    assert_eq!(req.timeout_ms, 1500);
    assert!(RequestBuilder::new("").build().is_err());
}""",
    12: """\
fn main() {
    let rt = tokio::runtime::Runtime::new().unwrap();
    rt.block_on(async {
        let start = std::time::Instant::now();
        Delay::new(std::time::Duration::from_millis(50)).await;
        assert!(start.elapsed() >= std::time::Duration::from_millis(40));
    });
}""",
    13: """\
fn main() {
    let rt = tokio::runtime::Runtime::new().unwrap();
    rt.block_on(async {
        use std::sync::atomic::{AtomicU32, Ordering};
        let attempts = AtomicU32::new(0);
        let result = retry_with_backoff(
            || async {
                let n = attempts.fetch_add(1, Ordering::SeqCst) + 1;
                if n < 3 {
                    Err("fail")
                } else {
                    Ok(42)
                }
            },
            5,
            std::time::Duration::from_millis(1),
        )
        .await;
        assert_eq!(result, Ok(42));
        assert_eq!(attempts.load(Ordering::SeqCst), 3);
    });
}""",
    14: """\
fn main() {
    let bucket = TokenBucket::new(2.0, 1000.0);
    assert!(bucket.try_acquire(1.0));
    assert!(bucket.try_acquire(1.0));
    assert!(!bucket.try_acquire(1.0)); // empty
    std::thread::sleep(std::time::Duration::from_millis(5));
    assert!(bucket.try_acquire(1.0)); // refilled
}""",
    15: """\
fn main() {
    match parse(r#"{"a": [1, true, null]}"#) {
        Ok(Json::Object(map)) => {
            match map.get("a") {
                Some(Json::Array(items)) => {
                    assert_eq!(items.len(), 3);
                    assert!(matches!(items[0], Json::Number(_)));
                    assert!(matches!(items[1], Json::Bool(true)));
                    assert!(matches!(items[2], Json::Null));
                }
                other => panic!("expected array, got {other:?}"),
            }
        }
        other => panic!("parse failed: {other:?}"),
    }
    assert!(parse("{").is_err());
}""",
    16: """\
fn main() {
    let mut g = Graph::new();
    g.add_edge("a", "b");
    g.add_edge("b", "c");
    g.add_edge("a", "c");
    assert_eq!(g.shortest_path(&"a", &"c"), Some(vec!["a".into(), "c".into()]));
    assert_eq!(g.shortest_path(&"c", &"a"), None);
}""",
    17: """\
fn main() {
    let arena = Arena::new(1024);
    let a = arena.alloc(1u32);
    let b = arena.alloc(2u32);
    assert_eq!(*a, 1);
    assert_eq!(*b, 2);
    *a = 9;
    assert_eq!(*a, 9);
}""",
    18: """\
fn main() {
    let rt = tokio::runtime::Runtime::new().unwrap();
    rt.block_on(async {
        let handle = CounterHandle::new();
        handle.increment().await;
        handle.increment().await;
        assert_eq!(handle.get().await, 2);
    });
}""",
    19: """\
fn main() {
    use std::sync::Arc;
    use std::thread;
    use std::time::{Duration, Instant};
    let sem = Arc::new(Semaphore::new(1));
    let s2 = Arc::clone(&sem);
    let t0 = Instant::now();
    let h = thread::spawn(move || {
        let _g = s2.acquire();
        thread::sleep(Duration::from_millis(50));
    });
    thread::sleep(Duration::from_millis(10));
    let _g = sem.acquire();
    assert!(t0.elapsed() >= Duration::from_millis(40));
    h.join().unwrap();
}""",
    20: """\
fn main() {
    let mut ds = DisjointSet::new(5);
    ds.union(0, 1);
    ds.union(1, 2);
    assert_eq!(ds.find(0), ds.find(2));
    assert_ne!(ds.find(0), ds.find(3));
    ds.union(3, 4);
    ds.union(2, 3);
    assert_eq!(ds.find(0), ds.find(4));
}""",
    21: """\
fn main() {
    assert_eq!(apply_n_times_generic(1, 5, |x| x * 2), 32);
    let mut total_calls = 0;
    let mut counting = |x: i32| {
        total_calls += 1;
        x + 1
    };
    assert_eq!(apply_n_times_dyn(0, 3, &mut counting), 3);
    assert_eq!(total_calls, 3);
    let mut pipeline: Vec<Box<dyn FnMut(i32) -> i32>> = vec![
        Box::new(|x| x + 1),
        Box::new(|x| x * 2),
    ];
    assert_eq!(run_pipeline(5, &mut pipeline), 12);
}""",
    22: """\
fn main() {
    use std::io::Write;
    let dir = std::env::temp_dir().join("w22_wordfreq");
    let _ = std::fs::create_dir_all(&dir);
    let inp = dir.join("in.txt");
    let out = dir.join("out.txt");
    {
        let mut f = std::fs::File::create(&inp).unwrap();
        writeln!(f, "Hello hello world").unwrap();
    }
    word_frequencies(inp.to_str().unwrap(), out.to_str().unwrap()).unwrap();
    let text = std::fs::read_to_string(&out).unwrap();
    assert!(text.to_lowercase().contains("hello"));
    assert!(text.contains('2') || text.contains("hello 2"));
}""",
    23: """\
fn main() {
    use std::io::Write;
    let path = std::env::temp_dir().join("w23_mmap.txt");
    {
        let mut f = std::fs::File::create(&path).unwrap();
        write!(f, "one\\ntwo\\nthree").unwrap();
    }
    let p = path.to_str().unwrap();
    assert_eq!(mmap_line_count(p).unwrap(), 2);
    assert!(mmap_contains(p, b"two").unwrap());
    assert!(!mmap_contains(p, b"four").unwrap());
}""",
    24: """\
fn main() {
    let rt = tokio::runtime::Runtime::new().unwrap();
    rt.block_on(async {
        use std::collections::HashMap;
        let mem = InMemory {
            data: HashMap::from([(1, "ok".into())]),
        };
        assert_eq!(mem.fetch(1).await.unwrap(), "ok");
        let sources: Vec<Box<dyn DataSourceDyn>> = vec![Box::new(mem)];
        let v = sources[0].fetch(1).await.unwrap();
        assert_eq!(v, "ok");
    });
}""",
    25: """\
fn main() {
    let circles = vec![Circle { radius: 1.0 }, Circle { radius: 2.0 }];
    let generic_total = total_area_generic(&circles);
    assert!((generic_total - (std::f64::consts::PI * 5.0)).abs() < 1e-6);
    let mixed: Vec<Box<dyn Shape>> = vec![
        Box::new(Circle { radius: 1.0 }),
        Box::new(Rectangle {
            width: 2.0,
            height: 3.0,
        }),
    ];
    let dyn_total = total_area_dyn(&mixed);
    assert!((dyn_total - (std::f64::consts::PI + 6.0)).abs() < 1e-6);
}""",
    26: """\
fn main() {
    let data = std::sync::Arc::new((0..10_000i64).collect::<Vec<_>>());
    let expected: i64 = data.iter().sum();
    assert_eq!(parallel_sum(std::sync::Arc::clone(&data), 1), expected);
    assert_eq!(parallel_sum(std::sync::Arc::clone(&data), 4), expected);
    assert_eq!(parallel_sum(std::sync::Arc::clone(&data), 8), expected);
}""",
    28: """\
#[cfg(test)]
mod tests {
    use super::*;
    use std::io::{BufRead, BufReader, Write};
    use std::net::TcpStream;
    use std::thread;
    use std::time::Duration;

    #[test]
    fn echoes_a_line() {
        let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        let addr = listener.local_addr().unwrap();
        thread::spawn(move || {
            let (stream, _) = listener.accept().unwrap();
            let _ = handle_client(stream);
        });
        thread::sleep(Duration::from_millis(20));
        let mut client = TcpStream::connect(addr).unwrap();
        writeln!(client, "hello").unwrap();
        let mut reader = BufReader::new(client.try_clone().unwrap());
        let mut line = String::new();
        reader.read_line(&mut line).unwrap();
        assert_eq!(line.trim(), "hello");
    }
}

fn main() {
    println!("run `cargo test` for W28 echo checks");
}""",
}
