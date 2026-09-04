#!/usr/bin/env python3
"""Torti の公開サイトを生成する。

プライバシーポリシーの原本は store/metadata/privacy-policy-en-US.md 側に置き、
ここではそれを HTML に変換するだけにしている。原本を2つ持つと必ずズレるため。

    python3 site/build.py            # site/ 配下に HTML を書き出す
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# 問い合わせ先。公開されるので、実在して本人が読めるアドレスにすること。
SUPPORT_EMAIL = "torti.app.support@gmail.com"
UPDATED = "August 8, 2026"


def md_to_html(md: str) -> str:
    """このサイトで使う範囲だけの最小 Markdown 変換。

    行単位ではなく**空行区切りのブロック単位**で処理する。行ごとに見ると、
    複数行にまたがる `**強調**` が変換されず、段落も勝手に連結される。
    """
    # 日本語の実装メモ以降は社内向けなので公開しない
    md = md.split("## 実装メモ")[0]
    # 先頭の H1 と更新日はテンプレート側で出す
    md = re.sub(r"\A#\s+.*\n", "", md)
    md = re.sub(r"\*\*Last updated:.*?\*\*\n", "", md)

    html = []
    for block in re.split(r"\n\s*\n", md.strip()):
        lines = [l.rstrip() for l in block.strip().split("\n") if l.strip()]
        if not lines:
            continue
        if lines[0] == "---":
            html.append("<hr>")
        elif lines[0].startswith("### "):
            html.append(f"<h3>{inline(lines[0][4:])}</h3>")
            if len(lines) > 1:
                html.append(f"<p>{inline(' '.join(lines[1:]))}</p>")
        elif lines[0].startswith("## "):
            html.append(f"<h2>{inline(lines[0][3:])}</h2>")
        elif lines[0].startswith("- "):
            items, current = [], ""
            for line in lines:
                if line.startswith("- "):
                    if current:
                        items.append(current)
                    current = line[2:]
                else:
                    current += " " + line.strip()   # 折り返した箇条書きの続き
            if current:
                items.append(current)
            body = "".join(f"<li>{inline(i)}</li>" for i in items)
            html.append(f"<ul>{body}</ul>")
        else:
            html.append(f"<p>{inline(' '.join(lines))}</p>")
    return "\n".join(html)


def inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w/])(https?://[^\s<]+)", r'<a href="\1">\1</a>', text)
    text = re.sub(r"\b([\w.+-]+@[\w.-]+\.\w+)\b", r'<a href="mailto:\1">\1</a>', text)
    return text


def page(title: str, heading: str, body: str, updated: bool = True, depth: int = 0) -> str:
    """depth はサイトルートからの階層。リンクを相対パスで書くのに使う。

    絶対パス(/torti/...)にするとリポジトリ名を変えた瞬間に全部壊れるうえ、
    ローカルで開いても崩れる。相対にしておけばどこに置いても動く。
    """
    base = "../" * depth if depth else "./"
    stamp = f'<p class="updated">Last updated: {UPDATED}</p>' if updated else ""
    body = body.replace("/torti/", base)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{base}style.css">
<link rel="icon" href="{base}icon.png">
</head>
<body>
<div class="wrap">
<header class="site">
  <img src="{base}icon.png" alt="">
  <a class="brand" href="{base}">Torti</a>
  <nav class="site">
    <a href="{base}support/">Support</a>
    <a href="{base}privacy/">Privacy</a>
    <a href="{base}terms/">Terms</a>
  </nav>
</header>
<h1>{heading}</h1>
{stamp}
{body}
<footer class="site">
  <p>Torti is an independent app and is not affiliated with, endorsed by, or
  sponsored by Eli Lilly, Novo Nordisk, or any pharmaceutical company. All
  trademarks belong to their respective owners.</p>
  <p>Questions? <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a></p>
  <p>© 2026 Z, K.K. · Tokyo, Japan</p>
</footer>
</div>
</body>
</html>
"""


def write(rel: str, html: str) -> None:
    path = SITE / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


def main() -> int:
    policy_md = (ROOT / "store/metadata/privacy-policy-en-US.md").read_text(encoding="utf-8")
    policy = md_to_html(policy_md).replace("support@usetorti.com", SUPPORT_EMAIL)
    write("privacy/index.html", page("Privacy Policy — Torti", "Privacy Policy", policy, depth=1))

    write("index.html", page("Torti — GLP-1 Shot Tracker", "Torti", LANDING, updated=False))
    write("terms/index.html", page("Terms of Use — Torti", "Terms of Use", TERMS, depth=1))
    write("support/index.html", page("Support — Torti", "Support",
                                     SUPPORT.replace("{EMAIL}", SUPPORT_EMAIL),
                                     updated=False, depth=1))
    return 0


LANDING = """
<p class="lede">A calm, private tracker for GLP-1 medications — built to fit your
real protocol, not a rigid weekly template.</p>

<div class="callout">
<p><strong>Your data stays yours.</strong> No account, no sign-up. Everything lives
on your iPhone and syncs through your own iCloud. Free CSV export, anytime —
including if you decide to leave.</p>
</div>

<h2>What Torti does</h2>
<ul>
<li>Tracks shots and pills — dose, time, and injection site, with automatic site rotation</li>
<li>Handles any schedule: weekly, every 10 days, split across the week, or a daily oral</li>
<li>Weight with a 7-day trend line, side effects, water and protein</li>
<li>Reminders for your next dose</li>
<li>Progress photos, stored in the app on your device</li>
</ul>

<h2>What Torti does not do</h2>
<p><strong>Torti does not calculate doses.</strong> You enter the dose and the syringe
units you were prescribed, and the app records them. It is a record-keeping tool,
not medical advice — always follow the instructions your care team gave you.</p>

<h2>Links</h2>
<ul>
<li><a href="/torti/support/">Support and contact</a></li>
<li><a href="/torti/privacy/">Privacy Policy</a></li>
<li><a href="/torti/terms/">Terms of Use</a></li>
</ul>
"""

TERMS = """
<p>These terms cover your use of the Torti iPhone app, published by
<strong>Z, K.K.</strong> (Tokyo, Japan). "We" and "us" below refer to Z, K.K.
Please read them before using the app.</p>

<h2>Torti is not medical advice</h2>
<p>Torti is a record-keeping tool. It does not provide medical advice, diagnosis,
or treatment, and it does not calculate medication doses. You enter the dose and
syringe units your prescriber gave you, and the app stores them.</p>
<p>The estimated medication level chart is a mathematical estimate based on
published half-life values. It is not a measurement of your body and must not be
used to decide when or how much to take. Always follow your care team's
instructions, and contact them with any medical question.</p>

<h2>Your account and data</h2>
<p>Torti does not require an account. Your records are stored on your device and,
if you enable iCloud, in your own Apple account. You are responsible for keeping
your device and Apple account secure, and for exporting your data if you want a
copy you control. How we handle information is described in the
<a href="/torti/privacy/">Privacy Policy</a>.</p>

<h2>Subscriptions</h2>
<p>Core tracking is free. Torti Pro is offered as an auto-renewing subscription
(monthly or yearly) or as a one-time lifetime purchase.</p>
<ul>
<li>Payment is charged to your Apple Account at confirmation of purchase.</li>
<li>Subscriptions renew automatically unless canceled at least 24 hours before the
end of the current period. Your account is charged for renewal within 24 hours
before the period ends.</li>
<li>You can manage or cancel a subscription in your Apple Account settings.</li>
<li>A free trial, where offered, converts to a paid subscription unless canceled
at least 24 hours before it ends. Any unused portion of a trial is forfeited when
you buy a subscription.</li>
<li>The lifetime option is a one-time purchase and does not renew.</li>
<li>Refunds are handled by Apple under the Apple Media Services Terms.</li>
</ul>

<h2>Acceptable use</h2>
<p>Please do not attempt to reverse engineer, resell, or interfere with the app or
its services, and do not use it in a way that breaks the law.</p>

<h2>No warranty, and limits on liability</h2>
<p>Torti is provided "as is," without warranties of any kind. We do not warrant
that the app will be uninterrupted, error-free, or that estimates or reminders
will be accurate or delivered on time. Do not rely on Torti as your only reminder
for a medical treatment.</p>
<p>To the maximum extent permitted by law, our total liability arising out of your
use of the app is limited to the amount you paid for it in the twelve months
before the claim.</p>

<h2>Changes</h2>
<p>We may update these terms. Material changes will be noted here with a new date
above and, where appropriate, in the app's release notes.</p>

<h2>Contact</h2>
<p>Questions about these terms: see the <a href="/torti/support/">support page</a>.</p>
"""

SUPPORT = """
<p class="lede">Something not working, or a feature you want? Write to us — a real
person reads it.</p>

<div class="callout">
<p><strong>Email:</strong> <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p>To help us help you faster, include your iPhone model, your iOS version, and
what you were doing when it happened. Please do not send screenshots containing
information you would rather keep private.</p>
</div>

<h2>Common questions</h2>

<h3>Does Torti work with compounded medication?</h3>
<p>Yes. Turn on "Compounded (vial + syringe)" in the medication settings to track
your vial and log the units you draw. Torti records the units you enter — it does
not calculate them.</p>

<h3>Can I use a schedule other than once a week?</h3>
<p>Yes. Torti supports any interval (every 10 days, every 14 days, and so on),
splitting one weekly dose across two days, and daily oral medication.</p>

<h3>How do I get my data out?</h3>
<p>Settings → Export. You get a CSV of every dose, weight, side effect and intake
entry. It is free, and it works whether or not you subscribe. The same file can be
imported back into Torti.</p>

<h3>I switched phones and my data is missing</h3>
<p>Torti syncs through your own iCloud account. Make sure the new device is signed
into the same Apple Account with iCloud Drive enabled, then open the app and give
it a moment to sync.</p>

<h3>How do I cancel my subscription?</h3>
<p>Subscriptions are managed by Apple: open the Settings app, tap your name, then
Subscriptions, and select Torti. Canceling stops future renewals; you keep Pro
until the current period ends.</p>

<h3>My reminders are not appearing</h3>
<p>Check that notifications are allowed for Torti in iOS Settings → Notifications.
If they were denied at first launch, enabling them there and reopening the app
will restore your reminders.</p>

<h2>Medical questions</h2>
<p>We cannot answer questions about your medication, dosing, or side effects.
Please contact your prescriber or pharmacist — they know your situation and we
do not.</p>
"""

if __name__ == "__main__":
    sys.exit(main())
