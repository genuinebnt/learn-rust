use solution::*;

#[test]
fn empty_inbox() {
    let mut inbox = Inbox::new();
    check!(r#"new inbox"#, (inbox.unread().len(), inbox.newest_unread_mut().is_none(), triage(&mut inbox, "x")), (0, true, vec![]));
}

#[test]
fn unread_oldest_first() {
    let mut inbox = Inbox::new();
    inbox.push(1, "ann", "hello");
    inbox.push(2, "boss", "report?");
    inbox.push(3, "bob", "lunch");
    inbox.mark_read(2);
    check!(r#"inbox 1 ann "hello", 2 boss "report?", 3 bob "lunch"; mark_read(2)"#, inbox.unread().iter().map(|m| m.id).collect::<Vec<_>>(), vec![1, 3]);
}

#[test]
fn reply_mut_keeps_existing() {
    let mut inbox = Inbox::new();
    inbox.push(1, "ann", "hello");
    inbox.push(2, "boss", "report?");
    inbox.push(3, "bob", "lunch");
    *inbox.reply_mut(1).unwrap() = "a".to_string();
    inbox.reply_mut(1).unwrap().push_str("b");
    check!(r#"inbox 1 ann "hello", 2 boss "report?", 3 bob "lunch"; reply_mut(1) = "a", then reply_mut(1) += "b""#, inbox.reply_to(1), Some("ab"));
}

#[test]
fn empty_reply_is_some() {
    let mut inbox = Inbox::new();
    inbox.push(1, "ann", "hello");
    inbox.push(2, "boss", "report?");
    inbox.push(3, "bob", "lunch");
    inbox.reply_mut(1);
    check!(r#"inbox 1 ann "hello", 2 boss "report?", 3 bob "lunch"; reply_mut(1) without writing"#, inbox.reply_to(1), Some(""));
}

#[test]
fn get_mut_edits_in_place() {
    let mut inbox = Inbox::new();
    inbox.push(1, "ann", "hello");
    inbox.push(2, "boss", "report?");
    inbox.push(3, "bob", "lunch");
    inbox.get_mut(2).unwrap().body = "done".to_string();
    check!(r#"inbox 1 ann "hello", 2 boss "report?", 3 bob "lunch"; get_mut(2).body = "done""#, inbox.get(2).map(|m| m.body.as_str()), Some("done"));
}

#[test]
fn all_read() {
    let mut inbox = Inbox::new();
    inbox.push(1, "ann", "hello");
    inbox.push(2, "boss", "report?");
    inbox.push(3, "bob", "lunch");
    for id in 1..=3 {
        inbox.mark_read(id);
    }
    check!(r#"inbox 1 ann "hello", 2 boss "report?", 3 bob "lunch"; mark_read 1, 2, 3"#, (inbox.newest_unread_mut().is_none(), inbox.unread().len()), (true, 0));
}

#[test]
fn triage_everything_from_boss() {
    let mut inbox = Inbox::new();
    inbox.push(1, "boss", "a");
    inbox.push(2, "boss", "b");
    check!(r#"inbox 1 boss, 2 boss; triage("boss")"#, (triage(&mut inbox, "boss"), inbox.reply_to(1), inbox.reply_to(2)), (vec![], None, None));
}

#[test]
fn triage_appends_to_existing_reply() {
    let mut inbox = Inbox::new();
    inbox.push(1, "ann", "hello");
    inbox.push(2, "boss", "report?");
    inbox.push(3, "bob", "lunch");
    inbox.reply_mut(3).unwrap().push_str("ok, ");
    check!(r#"inbox 1 ann "hello", 2 boss "report?", 3 bob "lunch"; reply to 3 is "ok, "; triage("nobody")"#, (triage(&mut inbox, "nobody"), inbox.reply_to(3)), (vec![1, 2, 3], Some("ok, on it")));
}

#[test]
fn triage_skips_already_read_boss_mail() {
    let mut inbox = Inbox::new();
    inbox.push(1, "ann", "hello");
    inbox.push(2, "boss", "report?");
    inbox.push(3, "bob", "lunch");
    inbox.mark_read(2);
    check!(r#"inbox 1 ann "hello", 2 boss "report?", 3 bob "lunch"; mark_read(2); triage("boss"); mark_read(2)"#, { triage(&mut inbox, "boss"); inbox.mark_read(2) }, false);
}

#[test]
fn many_readers_at_once() {
    let mut inbox = Inbox::new();
    inbox.push(7, "a", "x");
    inbox.push(8, "b", "y");
    let all = inbox.unread();
    let one = inbox.get(8);
    let reply = inbox.reply_to(7);
    check!("unread(), get(8) and reply_to(7) held together", (all.len(), one.map(|m| m.from.as_str()), reply), (2, Some("b"), None));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6202);
    for _ in 0..300 {
        let mut inbox = Inbox::new();
        // (id, read, reply)
        let mut model: Vec<(u32, bool, Option<String>)> = Vec::new();
        let mut ops = Vec::new();
        for step in 0..12u32 {
            match rng.below(4) {
                0 => {
                    inbox.push(step, "f", "b");
                    model.push((step, false, None));
                    ops.push(format!("push {step}"));
                }
                1 => {
                    let id = rng.below(step as usize + 1) as u32;
                    let want = match model.iter_mut().find(|m| m.0 == id) {
                        Some(m) if !m.1 => {
                            m.1 = true;
                            true
                        }
                        _ => false,
                    };
                    ops.push(format!("mark_read {id}"));
                    check!(ops.join(", "), inbox.mark_read(id), want);
                }
                2 => {
                    let id = rng.below(step as usize + 1) as u32;
                    let s = rng.string(1, "xy");
                    if let Some(r) = inbox.reply_mut(id) {
                        r.push_str(&s);
                    }
                    if let Some(m) = model.iter_mut().find(|m| m.0 == id) {
                        m.2.get_or_insert_with(String::new).push_str(&s);
                    }
                    ops.push(format!("reply_mut {id} += {s}"));
                }
                _ => {
                    let got = inbox.newest_unread_mut().map(|m| m.id);
                    let want = model.iter().rev().find(|m| !m.1).map(|m| m.0);
                    ops.push("newest_unread_mut".to_string());
                    check!(ops.join(", "), got, want);
                }
            }
        }
        let unread: Vec<u32> = inbox.unread().iter().map(|m| m.id).collect();
        let want_unread: Vec<u32> = model.iter().filter(|m| !m.1).map(|m| m.0).collect();
        check!(format!("{}; unread ids", ops.join(", ")), unread, want_unread);
        for m in &model {
            check!(format!("{}; reply_to({})", ops.join(", "), m.0), inbox.reply_to(m.0), m.2.as_deref());
        }
    }
}
