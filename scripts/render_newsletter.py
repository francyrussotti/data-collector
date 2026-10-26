"""Compone l'HTML della newsletter da un file di contenuti (JSON) con le etichette in inglese.

Uso: python scripts/render_newsletter.py content.json newsletter.html
"""
import html, json, sys
E = html.escape
INK, SIG, TXT, MUT, BG, BRD = "#0E1A2B", "#19C39C", "#1B2430", "#5B6675", "#EEF1F5", "#DDE3EA"
TYPE = {"Journal": ("#166534", "#DCFCE7"), "Review": ("#166534", "#DCFCE7"), "Preprint – not peer reviewed": ("#92400E", "#FEF3C7")}
CAT = {"emerging": ("#6D28D9", "#EFE7FF"), "strong growth": ("#0F766E", "#DDF5F1"),
       "growing": ("#0F766E", "#ECFDF5"), "stable": ("#374151", "#F3F4F6"), "declining": ("#B42318", "#FEE4E2")}
FONT = "-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"

def chip(text, colors):
    c, b = colors
    return f'<span style="display:inline-block;padding:1px 7px;border-radius:9px;font-size:11px;font-weight:700;color:{c};background:{b};">{E(text)}</span>'

def section(title):
    return f'<tr><td style="padding:26px 28px 0 28px;"><div style="font-size:12px;letter-spacing:1.5px;color:{MUT};font-weight:700;border-bottom:1px solid {BRD};padding-bottom:8px;">{E(title)}</div></td></tr>'

def theme(name, cat, weight, ctx=None):
    out = f'<tr><td style="padding:16px 28px 0 28px;"><span style="font-size:16px;font-weight:700;color:{INK};">{E(name)}</span>'
    if cat:
        c, b = CAT[cat]
        out += f'<span style="display:inline-block;margin-left:6px;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700;color:{c};background:{b};">{E(cat)}</span>'
    if weight:
        out += f'<div style="font-size:12px;color:{MUT};margin-top:3px;">{E(weight)}</div>'
    if ctx:
        out += (f'<div style="font-size:14px;line-height:1.55;color:{TXT};background:#F6F8FA;border-radius:6px;padding:10px 12px;margin-top:8px;">'
                f'<b style="color:#0F766E;">What it is about.</b> {E(ctx)}</div>')
    return out + '</td></tr>'

def row(label, text, color=MUT, italic=False):
    t = f"<i>{E(text)}</i>" if italic else E(text)
    return (f'<tr><td valign="top" style="width:96px;font-size:12px;font-weight:700;color:{color};padding:3px 0;">{label}</td>'
            f'<td style="font-size:14px;line-height:1.5;padding:3px 0;">{t}</td></tr>')

def paper(p):
    rows = row("CONTEXT", p["contesto"]) if p.get("contesto") else ""
    rows += row("WHAT THEY DO", p["cosa"])
    if p.get("risultato"):
        rows += row("RESULT", p["risultato"])
    rows += row("WHY IT MATTERS", p["perche"], "#0F766E", True)
    return (f'<tr><td style="padding:10px 28px 0 28px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid {BRD};border-radius:8px;"><tr><td style="padding:14px 16px;">'
            f'<div style="font-size:15px;font-weight:700;line-height:1.4;"><a href="{p["link"]}" style="color:{TXT};text-decoration:none;">{E(p["titolo"])}</a></div>'
            f'<div style="font-size:12px;color:{MUT};margin-top:5px;">{E(p["fonte"])} · {E(p["data"])} &nbsp;{chip(p["tipo"], TYPE[p["tipo"]])}'
            + (f' &nbsp;{chip("High-impact journal", ("#1E40AF", "#DBEAFE"))}' if p.get("alto_impatto") else "")
            + (f' &nbsp;<a href="{p["pdf"]}" style="color:#0F766E;font-weight:700;text-decoration:none;">Free PDF ↗</a>' if p.get("pdf") else "")
            + '</div>'
            + (f'<div style="font-size:12px;color:{MUT};margin-top:3px;line-height:1.5;"><b style="color:{TXT};">Who wrote it:</b> {E(p["firma"])}</div>' if p.get("firma") else "")
            + f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:10px;">{rows}</table>'
            + '</td></tr></table></td></tr>')

d = json.load(open(sys.argv[1], encoding="utf-8"))
parts = [f'<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:{BG};">{E(d["anteprima"])}</div>',
         f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{BG};"><tr><td align="center" style="padding:16px 8px;">',
         f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:960px;background:#FFFFFF;border:1px solid {BRD};border-radius:10px;overflow:hidden;font-family:{FONT};color:{TXT};">',
         f'<tr><td style="background:{INK};padding:22px 28px 18px 28px;"><div style="font-size:12px;letter-spacing:2px;color:{SIG};font-weight:700;">TECH RADAR</div>'
         f'<div style="font-size:22px;line-height:1.3;color:#FFFFFF;font-weight:700;margin-top:6px;">{E(d["titolo"])}</div>'
         f'<div style="font-size:13px;color:#A9B4C2;margin-top:8px;">{E(d["sottotitolo"])}</div></td></tr>',
         f'<tr><td style="height:3px;background:{SIG};line-height:3px;font-size:0;">&nbsp;</td></tr>',
         f'<tr><td style="padding:22px 28px 6px 28px;"><div style="font-size:12px;letter-spacing:1.5px;color:{MUT};font-weight:700;">IN 30 SECONDS</div><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:10px;">']
for i, t in enumerate(d["in30"], 1):
    parts.append(f'<tr><td valign="top" style="width:22px;padding:4px 0;color:{SIG};font-weight:700;font-size:15px;">{i}</td><td style="padding:4px 0;font-size:15px;line-height:1.5;">{E(t)}</td></tr>')
parts.append('</table></td></tr>')
parts.append(f'<tr><td style="padding:14px 28px 6px 28px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid {BRD};border-radius:8px;"><tr>')
for n, lab in d["numeri"]:
    parts.append(f'<td align="center" style="padding:14px 6px;width:33%;"><div style="font-size:24px;font-weight:700;color:{INK};">{E(n)}</div><div style="font-size:12px;color:{MUT};line-height:1.4;margin-top:2px;">{E(lab)}</div></td>')
parts.append('</tr></table></td></tr>')
s = d["segnale"]
parts.append(f'<tr><td style="padding:18px 28px 4px 28px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#F2FBF8;border-left:4px solid {SIG};border-radius:6px;"><tr><td style="padding:16px 18px;">'
             f'<div style="font-size:12px;letter-spacing:1.5px;color:#0F766E;font-weight:700;">SIGNAL OF THE DAY</div>'
             f'<div style="font-size:17px;font-weight:700;margin-top:6px;line-height:1.4;"><a href="{s["link"]}" style="color:{INK};text-decoration:none;">{E(s["titolo"])}</a></div>'
             f'<div style="font-size:13px;color:{MUT};margin-top:4px;">{E(s["meta"])} &nbsp;{chip(s["tipo"], TYPE[s["tipo"]])}' + (f' &nbsp;{chip("High-impact journal", ("#1E40AF", "#DBEAFE"))}' if s.get("alto_impatto") else "") + '</div>' +
             (f'<div style="font-size:12px;color:{MUT};margin-top:3px;line-height:1.5;"><b style="color:{TXT};">Who wrote it:</b> {E(s["firma"])}</div>' if s.get("firma") else '') +
             (f'<div style="font-size:14px;line-height:1.55;margin-top:10px;color:{MUT};"><b style="color:#0F766E;">Context.</b> {E(s["contesto"])}</div>' if s.get("contesto") else '') +
             f'<div style="font-size:15px;line-height:1.55;margin-top:10px;">{E(s["testo"])}</div></td></tr></table></td></tr>')
for sec in d["sezioni"]:
    parts.append(section(sec["titolo"]))
    if sec.get("nota"):
        parts.append(f'<tr><td style="padding:8px 28px 0 28px;font-size:13px;color:{MUT};line-height:1.5;">{E(sec["nota"])}</td></tr>')
    for th in sec["temi"]:
        if th.get("nome"):
            parts.append(theme(th["nome"], th.get("cat"), th.get("peso"), th.get("contesto")))
        for p in th["paper"]:
            parts.append(paper(p))
def arrow(v):
    if v > 0.05:
        return f'<span style="color:#0F766E;">▲ +{round(v*100):,}%</span>'.replace(",", ".")
    if v < -0.05:
        return f'<span style="color:#B42318;">▼ −{round(-v*100)}%</span>'
    return f'<span style="color:{MUT};">■ {"+" if v >= 0 else "−"}{round(abs(v)*100)}%</span>'
if d.get("radar"):
    r = d["radar"]
    parts.append(section("WEEKLY RADAR"))
    td = 'style="padding:7px 0;border-top:1px solid #EEF1F5;"'
    tdr = 'align="right" style="padding:7px 0 7px 8px;border-top:1px solid #EEF1F5;white-space:nowrap;"'
    rows = "".join(f'<tr><td {td}>{E(a)}<div style="font-size:11px;color:{MUT};">{E(t)}</div></td><td {tdr}>{arrow(x)}</td><td {tdr}>{arrow(g)}</td><td {tdr}>{arrow(h)}</td></tr>'
                   for a, t, x, g, h in r["righe"])
    parts.append(f'<tr><td style="padding:4px 28px 0 28px;"><div style="font-size:12px;color:{MUT};line-height:1.5;margin-top:6px;">{E(r["intro"])}</div>'
                 f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:8px;font-size:13px;">'
                 f'<tr style="color:{MUT};font-size:11px;font-weight:700;"><td style="padding:6px 0;">AREA</td><td align="right" style="padding:6px 0;">RESEARCH<br>(share, 3 years)</td><td align="right" style="padding:6px 0;">GITHUB<br>(year on year)</td><td align="right" style="padding:6px 0;">HACKER NEWS<br>(year on year)</td></tr>'
                 f'{rows}</table><div style="font-size:12px;color:{MUT};margin-top:6px;line-height:1.5;">{E(r["nota"])}</div></td></tr>')
def pct(v):
    return f"{'+' if v >= 0 else '−'}{int(abs(v) * 100 + 0.5)}%"
def arr(v):
    if v is None:
        return f'<span style="color:{MUT};">—</span>'
    if v > 0.05:
        return f'<span style="color:#0F766E;">▲ {pct(v)}</span>'
    if v < -0.05:
        return f'<span style="color:#B42318;">▼ {pct(v)}</span>'
    return f'<span style="color:{MUT};">■ {pct(v)}</span>'
if d.get("radar_v"):
    r = d["radar_v"]
    parts.append(section("RADAR OF THE DAY · " + r["nome"].upper()))
    cells = "".join(f'<td align="center" style="padding:12px 6px;width:33%;"><div style="font-size:20px;font-weight:700;color:{INK};">{E(n)}</div><div style="font-size:12px;color:{MUT};line-height:1.4;">{E(l)}</div></td>' for n, l in r["cifre"])
    temi = "".join(f'<tr><td style="padding:6px 0;border-top:1px solid #EEF1F5;">{E(t)}<div style="font-size:12px;color:{MUT};">{E(x)}</div></td><td align="right" valign="top" style="padding:6px 0 6px 8px;border-top:1px solid #EEF1F5;white-space:nowrap;">{arr(v)}</td></tr>' for t, x, v in r["temi"])
    ad = "".join(f'<tr><td style="padding:6px 0;border-top:1px solid #EEF1F5;">«{E(q)}»</td><td align="right" style="padding:6px 0;border-top:1px solid #EEF1F5;">{arr(g)}</td><td align="right" style="padding:6px 0;border-top:1px solid #EEF1F5;">{arr(h)}</td></tr>' for q, g, h in r["adozione"])
    parts.append(f'<tr><td style="padding:6px 28px 0 28px;">'
                 f'<div style="font-size:14px;line-height:1.55;color:{TXT};background:#F6F8FA;border-radius:6px;padding:10px 12px;margin-top:6px;"><b style="color:#0F766E;">What it is about.</b> {E(r["contesto"])}</div>'
                 f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:10px;border:1px solid {BRD};border-radius:8px;"><tr>{cells}</tr></table>'
                 f'<div style="font-size:13px;font-weight:700;color:{INK};margin-top:14px;">Where research is growing <span style="font-weight:400;color:{MUT};font-size:12px;">(topic share, 2022→2025)</span></div>'
                 f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:4px;font-size:13px;">{temi}</table>'
                 f'<div style="font-size:13px;font-weight:700;color:{INK};margin-top:14px;">What developers and the public do</div>'
                 f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:4px;font-size:13px;"><tr style="color:{MUT};font-size:11px;font-weight:700;"><td style="padding:6px 0;">SIGNAL</td><td align="right" style="padding:6px 0;">GITHUB<br>(year on year)</td><td align="right" style="padding:6px 0;">HACKER NEWS<br>(year on year)</td></tr>{ad}</table>'
                 f'<div style="font-size:12px;color:{MUT};margin-top:6px;line-height:1.5;">{E(r["nota"])}</div>'
                 f'<div style="font-size:14px;line-height:1.55;margin-top:10px;"><b>In short:</b> {E(r["sintesi"])}</div></td></tr>')
if d.get("radar_w"):
    r = d["radar_w"]
    parts.append(section("WEEKEND RADAR · THE 5 VERTICALS COMPARED"))
    hdr = "".join(f'<td align="right" style="padding:6px 0 6px 6px;">{h}</td>' for h in r["colonne"])
    rows = ""
    for nome, tema, vals in r["righe"]:
        cells = "".join(f'<td align="right" valign="top" style="padding:7px 0 7px 6px;border-top:1px solid #EEF1F5;white-space:nowrap;">{arr(v) if isinstance(v, float) else E(v)}</td>' for v in vals)
        rows += f'<tr><td style="padding:7px 0;border-top:1px solid #EEF1F5;">{E(nome)}<div style="font-size:11px;color:{MUT};">{E(tema)}</div></td>{cells}</tr>'
    parts.append(f'<tr><td style="padding:6px 28px 0 28px;"><div style="font-size:12px;color:{MUT};line-height:1.5;">{E(r["intro"])}</div>'
                 f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:8px;font-size:13px;"><tr style="color:{MUT};font-size:10px;font-weight:700;"><td style="padding:6px 0;">VERTICAL</td>{hdr}</tr>{rows}</table>'
                 f'<div style="font-size:12px;color:{MUT};margin-top:6px;line-height:1.5;">{E(r["nota"])}</div>'
                 f'<div style="font-size:14px;line-height:1.55;margin-top:10px;"><b>In short:</b> {E(r["sintesi"])}</div></td></tr>')
if d.get("glossario"):
    parts.append(section("WORDS OF THE DAY"))
    rows = "".join(f'<tr><td style="padding:5px 0;font-size:14px;line-height:1.5;"><b>{E(t)}</b> — {E(x)}</td></tr>' for t, x in d["glossario"])
    parts.append(f'<tr><td style="padding:6px 28px 0 28px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">{rows}</table></td></tr>')
parts.append(section("WORTH WATCHING"))
parts[-1] = parts[-1].replace("</div></td></tr>", f'</div><div style="font-size:15px;line-height:1.6;margin-top:10px;">{E(d["occhio"])}</div></td></tr>')
parts.append(f'<tr><td style="padding:26px 28px 24px 28px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#F6F8FA;border-radius:8px;"><tr><td style="padding:14px 16px;font-size:12px;line-height:1.6;color:{MUT};">'
             '<a href="https://claude.ai/artifact/4bCKVECyEyHZrHvYKH9oMS" style="color:#0F766E;font-weight:700;text-decoration:none;">Open the Emerging Technology Radar ↗</a><br>'
             'How to read: takeaways come only from the abstracts; "Why it matters" is Claude\'s reading. Labels say whether a paper has been peer reviewed; "High-impact journal" and "Who wrote it" come from OpenAlex citation statistics. OpenAlex does not check the content.<br>'
             f'{E(d["limiti"])}<br>Sources: OpenAlex, GitHub, Hacker News · automatic collection francyrussotti/data-collector · written by Claude.</td></tr></table></td></tr>')
parts.append('</table></td></tr></table>')
out = "".join(parts)
assert "{{" not in out
open(sys.argv[2], "w", encoding="utf-8").write(out)
print(len(out))
