//! A tiny SQL shell, in the spirit of BusTub's `bustub-shell`: type SQL ending in `;`, see the result. `\dt` lists the tables, `\di` the
//! indexes, `explain <query>;` shows the plan, `\q` quits. Run it with `cargo run --bin bustub_shell`. Given code.

use std::io::{self, BufRead, Write};

use bustub::common::bustub_instance::BusTubInstance;
use bustub::common::result_writer::SimpleStreamWriter;

fn main() {
    let db = BusTubInstance::new(128);
    db.generate_mock_table();
    db.generate_test_table();
    println!("Welcome to the BusTub shell! Statements end with `;`. \\help lists the commands, \\q quits.");
    let stdin = io::stdin();
    let mut sql = String::new();
    loop {
        print!("{}", if sql.is_empty() { "bustub> " } else { "   ...> " });
        io::stdout().flush().ok();
        let mut line = String::new();
        if stdin.lock().read_line(&mut line).unwrap_or(0) == 0 {
            break;
        }
        let trimmed = line.trim();
        if sql.is_empty() && trimmed == "\\q" {
            break;
        }
        if sql.is_empty() && trimmed.starts_with('\\') {
            run(&db, trimmed);
            continue;
        }
        sql.push_str(&line);
        if trimmed.ends_with(';') {
            run(&db, sql.trim());
            sql.clear();
        }
    }
}

fn run(db: &BusTubInstance, sql: &str) {
    let mut out = String::new();
    match db.execute_sql(sql, &mut SimpleStreamWriter::new(&mut out, false, "\t"), None) {
        Ok(true) => print!("{out}"),
        Ok(false) => println!("{out}(the statement failed)"),
        Err(e) => println!("{e}"),
    }
}
