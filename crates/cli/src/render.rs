//! Markdown for the terminal, for `anneal course show`: headings, wrapped paragraphs, lists, quotes, code blocks and tables, with colour only
//! when asked for. It covers what the stage pages and hints use; it is not a general renderer.
//!
//! Without colour the text stays readable as plain text: inline code keeps its backticks, links show their address, headings keep a rule.

use pulldown_cmark::{CodeBlockKind, Event, HeadingLevel, Options, Parser, Tag, TagEnd};

/// Renders `md` in lines of at most `width` columns (a long unbreakable word or a code line may be longer).
pub fn render(md: &str, width: usize, color: bool) -> String {
    let mut r = Renderer { width: width.max(30), color, ..Renderer::default() };
    let mut opts = Options::empty();
    opts.insert(Options::ENABLE_TABLES);
    opts.insert(Options::ENABLE_STRIKETHROUGH);
    for ev in Parser::new_ext(md, opts) {
        r.event(ev);
    }
    r.finish()
}

/// A stage's markdown split at its `## Hints` section: (everything before it, the hints as (title, markdown)).
pub fn split_hints(md: &str) -> (&str, Vec<(String, String)>) {
    let Some(at) = md.lines().scan(0usize, |pos, l| {
        let start = *pos;
        *pos += l.len() + 1;
        Some((start, l))
    }).find(|(_, l)| l.trim_end() == "## Hints").map(|(p, _)| p) else {
        return (md, Vec::new());
    };
    let (body, hints) = md.split_at(at);
    let mut out: Vec<(String, String)> = Vec::new();
    for line in hints.lines().skip(1) {
        if let Some(title) = line.strip_prefix("### ") {
            out.push((title.trim().to_owned(), String::new()));
        } else if let Some((_, text)) = out.last_mut() {
            text.push_str(line);
            text.push('\n');
        }
    }
    for (_, text) in &mut out {
        *text = text.trim().to_owned();
    }
    (body, out)
}

#[derive(Clone, Copy, Default, PartialEq)]
struct Fmt {
    bold: bool,
    italic: bool,
    code: bool,
    link: bool,
    strike: bool,
}

/// One word of a paragraph: its width on screen and how it is written (with colour codes when on).
struct Word {
    plain: String,
    styled: String,
}

#[derive(Default)]
struct Table {
    rows: Vec<Vec<String>>,
    head: usize,
    row: Vec<String>,
    cell: String,
}

#[derive(Default)]
struct Renderer {
    width: usize,
    color: bool,
    out: String,
    words: Vec<Word>,
    fmt: Fmt,
    /// The next piece of text continues the last word (no space came between them).
    glue: bool,
    heading: Option<HeadingLevel>,
    /// For each open list: the next number, or `None` for bullets.
    lists: Vec<Option<u64>>,
    /// The marker still to be written before the item's first line.
    marker: Option<String>,
    quote: usize,
    code: Option<(String, String)>,
    table: Option<Table>,
    links: Vec<String>,
}

impl Renderer {
    fn sgr(&self, code: &str, s: &str) -> String {
        if self.color && !s.is_empty() { format!("\x1b[{code}m{s}\x1b[0m") } else { s.to_owned() }
    }

    fn style(&self, text: &str, f: Fmt) -> String {
        let mut s = text.to_owned();
        if f.code {
            s = if self.color { self.sgr("36", &s) } else { format!("`{s}`") };
        }
        if f.link {
            s = self.sgr("4;34", &s);
        }
        if f.bold {
            s = self.sgr("1", &s);
        }
        if f.italic {
            s = self.sgr("3", &s);
        }
        if f.strike {
            s = self.sgr("9", &s);
        }
        match self.heading {
            Some(HeadingLevel::H1 | HeadingLevel::H2) => self.sgr("1;32", &s),
            Some(_) => self.sgr("1", &s),
            None => s,
        }
    }

    fn event(&mut self, ev: Event<'_>) {
        match ev {
            Event::Start(tag) => self.start(tag),
            Event::End(tag) => self.end(tag),
            Event::Text(t) => self.text(&t),
            Event::Code(t) => {
                let f = Fmt { code: true, ..self.fmt };
                self.inline(&t, f);
            }
            Event::SoftBreak => self.glue = false,
            Event::HardBreak => self.flush(),
            Event::Rule => {
                self.flush();
                self.blank();
                let rule = "─".repeat(self.width.min(60));
                self.out.push_str(&self.sgr("2", &rule));
                self.out.push('\n');
                self.blank();
            }
            // Raw HTML, footnotes, task markers: nothing in the course uses them.
            _ => {}
        }
    }

    fn start(&mut self, tag: Tag<'_>) {
        match tag {
            Tag::Paragraph => {}
            Tag::Heading { level, .. } => {
                self.flush();
                self.blank();
                self.heading = Some(level);
            }
            Tag::BlockQuote(_) => {
                self.flush();
                self.quote += 1;
            }
            Tag::CodeBlock(kind) => {
                self.flush();
                self.blank();
                let lang = match kind {
                    CodeBlockKind::Fenced(l) => l.split_whitespace().next().unwrap_or("").to_owned(),
                    CodeBlockKind::Indented => String::new(),
                };
                self.code = Some((lang, String::new()));
            }
            Tag::List(start) => {
                self.flush();
                self.lists.push(start);
            }
            Tag::Item => {
                self.flush();
                let marker = match self.lists.last_mut() {
                    Some(Some(n)) => {
                        let m = format!("{n}. ");
                        *n += 1;
                        m
                    }
                    _ => "• ".to_owned(),
                };
                self.marker = Some(marker);
            }
            Tag::Emphasis => self.fmt.italic = true,
            Tag::Strong => self.fmt.bold = true,
            Tag::Strikethrough => self.fmt.strike = true,
            Tag::Link { dest_url, .. } => {
                self.fmt.link = true;
                self.links.push(dest_url.to_string());
            }
            Tag::Table(_) => {
                self.flush();
                self.blank();
                self.table = Some(Table::default());
            }
            Tag::TableCell => {
                if let Some(t) = &mut self.table {
                    t.cell.clear();
                }
            }
            _ => {}
        }
    }

    fn end(&mut self, tag: TagEnd) {
        match tag {
            TagEnd::Paragraph => {
                self.flush();
                if self.lists.is_empty() {
                    self.blank();
                }
            }
            TagEnd::Heading(level) => {
                self.flush();
                if level == HeadingLevel::H2 {
                    let rule = self.sgr("2", &"─".repeat(self.width.min(60)));
                    self.out.push_str(&rule);
                    self.out.push('\n');
                }
                self.heading = None;
                self.blank();
            }
            TagEnd::BlockQuote(_) => {
                self.flush();
                self.quote = self.quote.saturating_sub(1);
                self.blank();
            }
            TagEnd::CodeBlock => self.end_code(),
            TagEnd::List(_) => {
                self.flush();
                self.lists.pop();
                if self.lists.is_empty() {
                    self.blank();
                }
            }
            TagEnd::Item => self.flush(),
            TagEnd::Emphasis => self.fmt.italic = false,
            TagEnd::Strong => self.fmt.bold = false,
            TagEnd::Strikethrough => self.fmt.strike = false,
            TagEnd::Link => {
                self.fmt.link = false;
                if let Some(url) = self.links.pop() {
                    let same = self.words.last().is_some_and(|w| w.plain == url);
                    if !same && !url.starts_with('#') && !url.is_empty() {
                        self.glue = false;
                        let styled = self.sgr("2", &format!("({url})"));
                        self.words.push(Word { plain: format!("({url})"), styled });
                        self.glue = false;
                    }
                }
            }
            TagEnd::TableHead => {
                if let Some(t) = &mut self.table {
                    t.rows.push(std::mem::take(&mut t.row));
                    t.head = 1;
                }
            }
            TagEnd::TableRow => {
                if let Some(t) = &mut self.table {
                    t.rows.push(std::mem::take(&mut t.row));
                }
            }
            TagEnd::TableCell => {
                if let Some(t) = &mut self.table {
                    let cell = std::mem::take(&mut t.cell);
                    t.row.push(cell);
                }
            }
            TagEnd::Table => self.end_table(),
            _ => {}
        }
    }

    fn text(&mut self, t: &str) {
        if let Some((_, buf)) = &mut self.code {
            buf.push_str(t);
            return;
        }
        let f = self.fmt;
        self.inline(t, f);
    }

    /// Adds inline text: to the current table cell, or as words of the paragraph.
    fn inline(&mut self, t: &str, f: Fmt) {
        if self.table.is_some() {
            let styled = self.style(&t.replace('\n', " "), f);
            if let Some(tb) = &mut self.table {
                tb.cell.push_str(&styled);
            }
            return;
        }
        let leading_space = t.starts_with(char::is_whitespace);
        let trailing_space = t.ends_with(char::is_whitespace);
        let mut first = true;
        // A code span is one unit even when it contains spaces: `O(log n)` must not be split across two lines.
        let flat = t.replace('\n', " ");
        let pieces: Vec<&str> = if f.code { vec![flat.trim()].into_iter().filter(|p| !p.is_empty()).collect() } else { t.split_whitespace().collect() };
        for piece in pieces {
            let styled = self.style(piece, f);
            let plain = if f.code && !self.color { format!("`{piece}`") } else { piece.to_owned() };
            let joins = first && self.glue && !leading_space && !self.words.is_empty();
            if joins {
                if let Some(w) = self.words.last_mut() {
                    w.plain.push_str(&plain);
                    w.styled.push_str(&styled);
                }
            } else {
                self.words.push(Word { plain, styled });
            }
            first = false;
        }
        if t.is_empty() {
            return;
        }
        self.glue = !trailing_space && !t.trim().is_empty();
    }

    /// Writes the pending words as wrapped lines with the quote bars, the list indent and the item marker in front.
    fn flush(&mut self) {
        if self.words.is_empty() {
            self.glue = false;
            return;
        }
        let depth = self.lists.len().saturating_sub(1);
        let bars = "▌ ".repeat(self.quote);
        let bars_styled = self.sgr("2", &bars);
        let indent = "  ".repeat(depth);
        let marker = self.marker.take();
        let mw = marker.as_deref().map_or(if self.lists.is_empty() { 0 } else { 2 }, |m| m.chars().count());
        let first_plain = format!("{bars}{indent}{}", marker.clone().unwrap_or_else(|| " ".repeat(mw)));
        let first_styled = format!("{bars_styled}{indent}{}", marker.map(|m| self.sgr("32", &m)).unwrap_or_else(|| " ".repeat(mw)));
        let rest_styled = format!("{bars_styled}{indent}{}", " ".repeat(mw));

        let avail = self.width.saturating_sub(first_plain.chars().count()).max(10);
        let mut line = String::new();
        let mut line_w = 0usize;
        let mut first = true;
        let words = std::mem::take(&mut self.words);
        let emit = |out: &mut String, line: &str, first: &mut bool| {
            out.push_str(if *first { &first_styled } else { &rest_styled });
            out.push_str(line);
            out.push('\n');
            *first = false;
        };
        for w in &words {
            let ww = w.plain.chars().count();
            if line_w > 0 && line_w + 1 + ww > avail {
                emit(&mut self.out, &line, &mut first);
                line.clear();
                line_w = 0;
            }
            if line_w > 0 {
                line.push(' ');
                line_w += 1;
            }
            line.push_str(&w.styled);
            line_w += ww;
        }
        if line_w > 0 {
            emit(&mut self.out, &line, &mut first);
        }
        self.glue = false;
    }

    /// Ensures the output ends with exactly one empty line (or is empty).
    fn blank(&mut self) {
        if self.out.is_empty() || self.out.ends_with("\n\n") {
            return;
        }
        if !self.out.ends_with('\n') {
            self.out.push('\n');
        }
        self.out.push('\n');
    }

    fn end_code(&mut self) {
        let Some((lang, text)) = self.code.take() else { return };
        if !lang.is_empty() {
            let label = self.sgr("2", &format!("  {lang}"));
            self.out.push_str(&label);
            self.out.push('\n');
        }
        let bar = self.sgr("2", "  │ ");
        for line in text.trim_end_matches('\n').lines() {
            self.out.push_str(&bar);
            self.out.push_str(line);
            self.out.push('\n');
        }
        self.blank();
    }

    fn end_table(&mut self) {
        let Some(t) = self.table.take() else { return };
        if t.rows.is_empty() {
            return;
        }
        let cols = t.rows.iter().map(Vec::len).max().unwrap_or(0);
        let mut widths = vec![0usize; cols];
        for row in &t.rows {
            for (i, c) in row.iter().enumerate() {
                widths[i] = widths[i].max(visible_width(c));
            }
        }
        let total: usize = widths.iter().sum::<usize>() + 3 * cols.saturating_sub(1) + 2;
        if total > self.width {
            // Too wide for the screen: one block per row, "heading: value" lines.
            let heads: Vec<String> = t.rows.first().cloned().unwrap_or_default();
            for row in t.rows.iter().skip(t.head) {
                for (i, c) in row.iter().enumerate() {
                    let h = heads.get(i).map(String::as_str).unwrap_or("");
                    self.out.push_str(&format!("  {}: {c}\n", self.sgr("1", &strip_ansi(h))));
                }
                self.out.push('\n');
            }
            return;
        }
        let pad = |s: &str, w: usize| format!("{s}{}", " ".repeat(w.saturating_sub(visible_width(s))));
        let sep = self.sgr("2", " │ ");
        for (ri, row) in t.rows.iter().enumerate() {
            let cells: Vec<String> = (0..cols)
                .map(|i| {
                    let c = row.get(i).map(String::as_str).unwrap_or("");
                    let c = if ri < t.head { self.sgr("1", &strip_ansi(c)) } else { c.to_owned() };
                    pad(&c, widths[i])
                })
                .collect();
            self.out.push_str("  ");
            self.out.push_str(cells.join(&sep).trim_end());
            self.out.push('\n');
            if ri + 1 == t.head {
                let rule = widths.iter().map(|w| "─".repeat(*w)).collect::<Vec<_>>().join("─┼─");
                self.out.push_str(&format!("  {}\n", self.sgr("2", &rule)));
            }
        }
        self.blank();
    }

    fn finish(mut self) -> String {
        self.flush();
        let mut s = self.out.trim_end().to_owned();
        s.push('\n');
        s
    }
}

/// Removes ANSI colour codes, for measuring and for restyling text that already carries them.
fn strip_ansi(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    let mut chars = s.chars();
    while let Some(c) = chars.next() {
        if c == '\x1b' {
            for n in chars.by_ref() {
                if n == 'm' {
                    break;
                }
            }
        } else {
            out.push(c);
        }
    }
    out
}

fn visible_width(s: &str) -> usize {
    strip_ansi(s).chars().count()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn plain(md: &str, width: usize) -> String {
        render(md, width, false)
    }

    #[test]
    fn paragraphs_wrap_at_the_width_without_breaking_words() {
        let text = "one two three four five six seven eight nine ten eleven twelve thirteen";
        let out = plain(text, 30);
        for line in out.lines() {
            assert!(line.chars().count() <= 30, "{line:?}");
        }
        assert_eq!(out.split_whitespace().collect::<Vec<_>>().join(" "), text);
        assert!(out.lines().count() >= 3);
    }

    #[test]
    fn no_colour_codes_unless_asked_and_inline_code_keeps_its_backticks() {
        let out = plain("Call `get_undo_log` first, then **stop**.", 80);
        assert!(!out.contains('\x1b'));
        assert_eq!(out.trim(), "Call `get_undo_log` first, then stop.");
        let coloured = render("Call `x` then **stop**.", 80, true);
        assert!(coloured.contains("\x1b[36m"), "inline code is cyan");
        assert!(coloured.contains("\x1b[1m"), "bold is bold");
    }

    #[test]
    fn a_code_span_with_spaces_stays_one_unit() {
        assert_eq!(plain("amortised `O(log n)` growth", 80).trim(), "amortised `O(log n)` growth");
        let narrow = plain("x x x x x x x x x x x x `O(log n)` y", 30);
        assert!(narrow.lines().any(|l| l.contains("`O(log n)`")), "{narrow}");
    }

    #[test]
    fn punctuation_stays_glued_to_the_code_before_it() {
        assert_eq!(plain("See `a`, then `b`.", 80).trim(), "See `a`, then `b`.");
        assert_eq!(plain("(`x`)", 80).trim(), "(`x`)");
    }

    #[test]
    fn lists_have_markers_and_a_hanging_indent() {
        let out = plain("- first item that is quite long and has to wrap around\n- second", 24);
        let lines: Vec<&str> = out.lines().collect();
        assert!(lines[0].starts_with("• first"), "{lines:?}");
        assert!(lines[1].starts_with("  "), "continuation is indented under the text: {lines:?}");
        assert!(lines.iter().any(|l| l.starts_with("• second")));
        let numbered = plain("1. a\n2. b\n3. c", 40);
        assert!(numbered.contains("1. a") && numbered.contains("2. b") && numbered.contains("3. c"));
    }

    #[test]
    fn nested_lists_indent_one_level_more() {
        let out = plain("- outer\n  - inner", 40);
        assert!(out.lines().any(|l| l.starts_with("• outer")));
        assert!(out.lines().any(|l| l.starts_with("  • inner")), "{out}");
    }

    #[test]
    fn code_blocks_are_not_wrapped_and_carry_a_bar_and_their_language() {
        let long = "let very_long_line = some_function(argument_one, argument_two, argument_three, argument_four);";
        let out = plain(&format!("```rust\n{long}\n```"), 30);
        assert!(out.contains("rust"));
        assert!(out.lines().any(|l| l.ends_with(long) && l.starts_with("  │ ")), "{out}");
    }

    #[test]
    fn headings_and_a_blank_line_between_blocks() {
        let out = plain("# Title\n\ntext\n\n## Section\n\nmore", 40);
        assert!(out.starts_with("Title\n"));
        assert!(out.contains("\n\ntext\n\n"));
        assert!(out.contains("Section\n────"), "an h2 gets a rule: {out}");
    }

    #[test]
    fn links_show_their_address_unless_it_is_the_text() {
        assert!(plain("[docs](https://example.com/x)", 80).contains("docs (https://example.com/x)"));
        assert_eq!(plain("<https://example.com>", 80).trim(), "https://example.com");
    }

    #[test]
    fn block_quotes_get_a_bar() {
        let out = plain("> **Tip.** do this", 40);
        assert!(out.starts_with("▌ "), "{out}");
    }

    #[test]
    fn tables_align_their_columns() {
        let out = plain("| call | meaning |\n|---|---|\n| `a` | the first |\n| `longer` | second |", 60);
        let lines: Vec<&str> = out.lines().collect();
        assert!(lines[0].contains("call") && lines[0].contains("meaning"));
        assert!(lines[1].contains('┼'));
        let col = lines[2].find('│').unwrap();
        assert_eq!(lines[3].find('│'), Some(col), "the separators line up:\n{out}");
    }

    #[test]
    fn a_table_wider_than_the_screen_becomes_one_block_per_row() {
        let out = plain("| name | description |\n|---|---|\n| `x` | a description that is much too long to fit next to its name |", 30);
        assert!(out.contains("name: `x`"), "{out}");
        assert!(out.contains("description: a description"), "{out}");
    }

    #[test]
    fn hints_are_split_off_the_page() {
        let md = "Intro\n\n## The task\n\ntext\n\n## Hints\n\n### First\n\nbody one\n\n### Second\n\nbody two\nmore\n";
        let (body, hints) = split_hints(md);
        assert!(body.contains("The task") && !body.contains("Hints") && !body.contains("body one"));
        assert_eq!(hints, vec![("First".to_owned(), "body one".to_owned()), ("Second".to_owned(), "body two\nmore".to_owned())]);
        let (whole, none) = split_hints("no hints here");
        assert_eq!(whole, "no hints here");
        assert!(none.is_empty());
    }
}
