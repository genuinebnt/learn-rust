// Markdown for AI answers. Unlike the repo's own content, a model's answer isn't trusted: raw HTML is shown as text,
// only http(s) links are kept (opening in a new tab), and images become their alt text.
import { Marked, type Tokens } from "marked";

const escape = (s: string) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);

const safe = new Marked({ async: false, gfm: true });
safe.use({
  renderer: {
    html(token: Tokens.HTML | Tokens.Tag) {
      return escape(token.text);
    },
    link(token: Tokens.Link) {
      const text = this.parser.parseInline(token.tokens);
      return /^https?:\/\//i.test(token.href) ? `<a href="${escape(token.href)}" target="_blank" rel="noreferrer noopener">${text}</a>` : text;
    },
    image(token: Tokens.Image) {
      return escape(token.text);
    },
  },
});

export const aiMarkdown = (s: string) => safe.parse(s) as string;
