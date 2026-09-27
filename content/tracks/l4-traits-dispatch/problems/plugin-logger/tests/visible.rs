use solution::*;

use std::sync::{Arc, Mutex};

struct Rec(Mutex<Vec<String>>);

impl Logger for Rec {
    fn log(&self, level: Level, msg: &str) {
        self.0.lock().unwrap().push(format!("{level:?} {msg}"));
    }
    fn flush(&self) {
        self.0.lock().unwrap().push("flush".into());
    }
}

fn rec() -> Arc<Rec> {
    Arc::new(Rec(Mutex::new(Vec::new())))
}

fn lines(r: &Rec) -> Vec<String> {
    r.0.lock().unwrap().clone()
}

#[test]
fn prefix() {
    let r = rec();
    PrefixLogger::new("[db] ", Box::new(r.clone())).log(Level::Info, "up");
    check!(r#"PrefixLogger("[db] ") → rec; Info "up""#, lines(&r), vec!["Info [db] up"]);
}

#[test]
fn filter_at_or_above() {
    let r = rec();
    let f = LevelFilter::new(Level::Warn, Box::new(r.clone()));
    f.log(Level::Info, "a");
    f.log(Level::Warn, "b");
    f.log(Level::Error, "c");
    check!(r#"LevelFilter(Warn) → rec; Info a, Warn b, Error c"#, lines(&r), vec!["Warn b", "Error c"]);
}

#[test]
fn nested() {
    let (r1, r2) = (rec(), rec());
    let l = PrefixLogger::new("a:", Box::new(Tee::new(vec![Box::new(r1.clone()), Box::new(PrefixLogger::new("b:", Box::new(r2.clone())))])));
    l.log(Level::Info, "x");
    check!(r#"Prefix("a:", Tee[r1, Prefix("b:", r2)]); Info x"#, (lines(&r1), lines(&r2)), (vec!["Info a:x".to_string()], vec!["Info b:a:x".to_string()]));
}

#[test]
fn flush_passes_through() {
    let (r1, r2) = (rec(), rec());
    let l = PrefixLogger::new("p", Box::new(LevelFilter::new(Level::Error, Box::new(Tee::new(vec![Box::new(r1.clone()), Box::new(r2.clone())])))));
    l.flush();
    check!(r#"Prefix(Filter(Tee[r1, r2])).flush()"#, (lines(&r1), lines(&r2)), (vec!["flush".to_string()], vec!["flush".to_string()]));
}

#[test]
fn shared_across_threads() {
    let r = rec();
    let root: Arc<dyn Logger + Send + Sync> = Arc::new(Tee::new(vec![Box::new(PrefixLogger::new("t", Box::new(r.clone())))]));
    std::thread::scope(|s| {
        for i in 0..4 {
            let root = &root;
            s.spawn(move || root.log(Level::Info, &i.to_string()));
        }
    });
    let mut got = lines(&r);
    got.sort();
    check!("4 threads log through one Tee", got, vec!["Info t0", "Info t1", "Info t2", "Info t3"]);
}
