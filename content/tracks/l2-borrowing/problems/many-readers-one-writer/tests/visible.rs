use solution::*;

#[test]
fn readers_together() {
    let mut inbox = Inbox::new();
    inbox.push(1, "ann", "hello");
    inbox.push(2, "boss", "report?");
    inbox.push(3, "bob", "lunch");
    inbox.reply_mut(2).unwrap().push_str("on it");
    let first = inbox.get(1);
    let second = inbox.reply_to(2);
    check!(r#"inbox 1 ann "hello", 2 boss "report?", 3 bob "lunch"; reply to 2 is "on it"; get(1).body and reply_to(2) held at once"#, (first.map(|m| m.body.as_str()), second), (Some("hello"), Some("on it")));
}

#[test]
fn mark_read_says_if_it_changed() {
    let mut inbox = Inbox::new();
    inbox.push(1, "ann", "hello");
    inbox.push(2, "boss", "report?");
    inbox.push(3, "bob", "lunch");
    check!(r#"inbox 1 ann "hello", 2 boss "report?", 3 bob "lunch"; mark_read(1) twice, then mark_read(9)"#, (inbox.mark_read(1), inbox.mark_read(1), inbox.mark_read(9)), (true, false, false));
}

#[test]
fn reply_mut_creates_then_edits() {
    let mut inbox = Inbox::new();
    inbox.push(1, "ann", "hello");
    inbox.push(2, "boss", "report?");
    inbox.push(3, "bob", "lunch");
    inbox.reply_mut(3).unwrap().push_str("no");
    inbox.reply_mut(3).unwrap().push_str("pe");
    check!(r#"inbox 1 ann "hello", 2 boss "report?", 3 bob "lunch"; reply_mut(3) += "no", then += "pe""#, (inbox.reply_to(3), inbox.reply_to(1)), (Some("nope"), None));
}

#[test]
fn newest_unread_skips_read() {
    let mut inbox = Inbox::new();
    inbox.push(1, "ann", "hello");
    inbox.push(2, "boss", "report?");
    inbox.push(3, "bob", "lunch");
    inbox.mark_read(3);
    check!(r#"inbox 1 ann "hello", 2 boss "report?", 3 bob "lunch"; mark_read(3); newest_unread_mut"#, inbox.newest_unread_mut().map(|m| m.id), Some(2));
}

#[test]
fn triage_example() {
    let mut inbox = Inbox::new();
    inbox.push(1, "ann", "hello");
    inbox.push(2, "boss", "report?");
    inbox.push(3, "bob", "lunch");
    check!(r#"inbox 1 ann "hello", 2 boss "report?", 3 bob "lunch"; triage(boss = "boss")"#, (triage(&mut inbox, "boss"), inbox.reply_to(3), inbox.reply_to(2)), (vec![1, 3], Some("on it"), None));
}

#[test]
fn unknown_ids() {
    let mut inbox = Inbox::new();
    inbox.push(1, "ann", "hello");
    inbox.push(2, "boss", "report?");
    inbox.push(3, "bob", "lunch");
    check!(r#"inbox 1 ann "hello", 2 boss "report?", 3 bob "lunch"; id 9"#, (inbox.reply_mut(9).is_none(), inbox.get_mut(9).is_none(), inbox.get(9).is_none(), inbox.reply_to(9)), (true, true, true, None));
}
