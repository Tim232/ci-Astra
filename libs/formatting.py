import re


def format_code(s: str):
    s = re.sub(r"("
               r"(?:(?:[a-zA-Z_][a-zA-Z_0-9]*\.)*[a-zA-Z_][a-zA-Z_0-9]*\(.*?\))|"
               r"(?:(?:[a-zA-Z_][a-zA-Z_0-9]*_)+[a-zA-Z_][a-zA-Z_0-9]*)"
               r")", r"`\1`", s, flags=re.MULTILINE)
    s = re.sub("-?->", "→", s)
    lst = s.split('`')
    ls = []
    rep = True
    for i in lst:
        ls.append(re.sub(r"([*~_\\])(?!`)", r"\\\1", i) if rep else i)
        rep = not rep
    print("`".join(ls))
    return "`".join(ls)


def limit(s: str, chars: int = 850, end: str = "..."):
    return s if len(s) < chars else s[:chars - 3] + end


def a_to_md(s: str, base: str, icode_links: bool = False):
    def _a_conv(m: re.Match):
        text = m.group(2)
        url = m.group(1)
        if not url.startswith("http"):
            url = base + url
        if icode_links:
            return f"[`{text}`]({url})"
        else:
            return f"[{text}]({url})"
    return re.sub(r"""<a.*? href="(.*?)".*?>(.*?)</a>""", _a_conv, s)


def html_to_md(s: str, base: str, icode_links: bool = False):
    repl = {
        "b": "**",
        "i": "*",
        "u": "__",
        "em": "*"
    }
    s = format_code(s)
    for st, r in repl.items():
        s = re.sub(rf"<{st}>(.*?)</{st}>", rf"{r}\1{r}", s)
    s = a_to_md(s, base, icode_links=icode_links)
    s = re.sub(r"<p>|</p>", "\n", s)
    s = re.sub("\n+", "\n", s)
    s = re.sub("<.*?>", "", s)
    return s