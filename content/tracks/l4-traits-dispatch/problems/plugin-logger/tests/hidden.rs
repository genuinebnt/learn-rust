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
fn filter_error_only() {
    let r = rec();
    let f = LevelFilter::new(Level::Error, Box::new(r.clone()));
    f.log(Level::Debug, "a");
    f.log(Level::Info, "b");
    f.log(Level::Warn, "c");
    check!(r#"LevelFilter(Error); Debug, Info, Warn"#, lines(&r), Vec::<String>::new());
}

#[test]
fn filter_debug_passes_all() {
    let r = rec();
    LevelFilter::new(Level::Debug, Box::new(r.clone())).log(Level::Debug, "d");
    check!(r#"LevelFilter(Debug); Debug d"#, lines(&r), vec!["Debug d"]);
}

#[test]
fn nested_filters() {
    let r = rec();
    let l = LevelFilter::new(Level::Info, Box::new(LevelFilter::new(Level::Error, Box::new(r.clone()))));
    l.log(Level::Warn, "w");
    l.log(Level::Error, "e");
    check!(r#"Filter(Info, Filter(Error)); Warn w, Error e"#, lines(&r), vec!["Error e"]);
}

#[test]
fn tee_order() {
    let r = rec();
    Tee::new(vec![Box::new(PrefixLogger::new("1", Box::new(r.clone()))), Box::new(PrefixLogger::new("2", Box::new(r.clone())))]).log(Level::Warn, "x");
    check!(r#"Tee[Prefix("1", r), Prefix("2", r)]; Warn x"#, lines(&r), vec!["Warn 1x", "Warn 2x"]);
}

#[test]
fn empty_tee() {
    let t = Tee::new(vec![]);
    t.log(Level::Info, "x");
    t.flush();
    check!(r#"Tee[] log and flush"#, true, true);
}

#[test]
fn arc_forwards_flush() {
    let r = rec();
    let shared = Arc::new(Tee::new(vec![Box::new(r.clone())]));
    let l = PrefixLogger::new("x", Box::new(Arc::clone(&shared)));
    l.flush();
    check!(r#"shared Arc<Tee[r]> under a Prefix; flush"#, lines(&r), vec!["flush"]);
}

#[test]
fn filter_forwards_flush() {
    let r = rec();
    LevelFilter::new(Level::Error, Box::new(r.clone())).flush();
    check!(r#"LevelFilter(Error) → rec; flush"#, lines(&r), vec!["flush"]);
}

#[test]
fn unicode_prefix() {
    let r = rec();
    PrefixLogger::new("» ", Box::new(r.clone())).log(Level::Error, "é");
    check!(r#"Prefix("» "); Error é"#, lines(&r), vec!["Error » é"]);
}

#[test]
fn default_flush_sink() {
    // A sink that keeps the default flush: flushing a Tee around it must not fail.
    struct Quiet;
    impl Logger for Quiet {
        fn log(&self, _: Level, _: &str) {}
    }
    let r = rec();
    let t = Tee::new(vec![Box::new(Quiet), Box::new(r.clone())]);
    t.flush();
    check!("Tee[Quiet, r].flush()", lines(&r), vec!["flush"]);
}

#[test]
fn random_chains_vs_model() {
    let mut rng = anneal_prelude::Rng::new(4410);
    let levels = [Level::Debug, Level::Info, Level::Warn, Level::Error];
    for _ in 0..200 {
        // Outermost first: Some(prefix) or None + a filter level.
        let n = rng.below(5);
        let chain: Vec<(Option<String>, Level)> = (0..n)
            .map(|_| if rng.bool() { let len = rng.below(3); (Some(rng.string(len, "ab")), Level::Debug) } else { (None, *rng.pick(&levels)) })
            .collect();
        let r = rec();
        let mut l: BoxLogger = Box::new(r.clone());
        for (p, min) in chain.iter().rev() {
            l = match p {
                Some(p) => Box::new(PrefixLogger::new(p, l)),
                None => Box::new(LevelFilter::new(*min, l)),
            };
        }
        let mut want = Vec::new();
        for i in 0..3 {
            let level = *rng.pick(&levels);
            let msg = format!("m{i}");
            l.log(level, &msg);
            let mut text = msg;
            let mut pass = true;
            for (p, min) in &chain {
                match p {
                    Some(p) => text = format!("{p}{text}"),
                    None => pass &= level >= *min,
                }
            }
            if pass {
                want.push(format!("{level:?} {text}"));
            }
        }
        check!(format!("chain = {chain:?}"), lines(&r), want);
    }
}
