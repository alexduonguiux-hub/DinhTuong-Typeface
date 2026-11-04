#!/usr/bin/env python3
"""Technical QA: run Font Bakery on the built fonts and compare against the accepted list.

    python3 scripts/qa_fontbakery.py            # run Font Bakery, then compare
    python3 scripts/qa_fontbakery.py --no-run   # compare existing out/fontbakery/*.json only

Profiles: check-googlefonts on fonts/ttf/*.ttf and on fonts/variable/*.ttf (profile name gf-variable in the\naccepted list), check-universal on fonts/otf/*.otf.

Every FAIL / FATAL / WARN / ERROR result is reduced to (profile, check id, code). Each one must be
listed in documentation/qa/fontbakery-accepted.txt as `accept` (intentional, with a reason) or `todo`
(a known defect still to fix). The run fails (exit 1) on:
  - any FAIL or FATAL that is not listed;
  - any WARN or ERROR that is not listed (a NEW issue);
  - listed entries that no longer occur are reported as STALE (remove them; not a failure).
ERRORs caused by no network access (Google Fonts metadata, namecheck) are reported as `network`
and do not fail the run unless --strict is given; re-run them where the network is available.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "fontbakery")
ACCEPTED = os.path.join(ROOT, "documentation", "qa", "fontbakery-accepted.txt")
RUNS = [  # (profile name, fontbakery subcommand, font glob)
    ("googlefonts", "check-googlefonts", "fonts/ttf/*.ttf"),
    ("universal", "check-universal", "fonts/otf/*.otf"),
    ("gf-variable", "check-googlefonts", "fonts/variable/*.ttf"),
]
BAD = ("FAIL", "FATAL", "WARN", "ERROR")
NETWORK = re.compile(r"ProxyError|ConnectionError|Max retries exceeded|Tunnel connection failed|"
                     r"NameResolutionError|namecheck-service|Temporary failure in name resolution")
IN_CI = os.environ.get("GITHUB_ACTIONS") == "true"


def run_fontbakery(fontbakery):
    os.makedirs(OUT, exist_ok=True)
    for profile, cmd, pattern in RUNS:
        fonts = sorted(glob.glob(os.path.join(ROOT, pattern)))
        if not fonts:
            sys.exit(f"no fonts match {pattern}; run `make build` first")
        js = os.path.join(OUT, f"{profile}.json")
        md = os.path.join(OUT, f"{profile}.md")
        print(f"== fontbakery {cmd} ({len(fonts)} fonts)", flush=True)
        # Font Bakery exits non-zero whenever something fails; the comparison below decides.
        subprocess.run([fontbakery, cmd, "-l", "WARN", "--succinct", "--full-lists",
                        "--json", js, "--ghmarkdown", md, *fonts],
                       cwd=ROOT, stdout=subprocess.DEVNULL)


def results(profile):
    """{(profile, check, code): {"status", "fonts", "message", "network"}}"""
    path = os.path.join(OUT, f"{profile}.json")
    if not os.path.exists(path):
        sys.exit(f"missing {path}; run without --no-run")
    found = {}
    for section in json.load(open(path, encoding="utf-8"))["sections"]:
        for check in section["checks"]:
            if check["result"] not in BAD:
                continue
            m = re.search(r"<FontBakeryCheck:([^>]+)>", str(check["key"][1]))
            cid = m.group(1) if m else str(check["key"][1])
            for log in check["logs"]:
                if log["status"] not in BAD:
                    continue
                msg = log["message"]
                code = (msg.get("code") if isinstance(msg, dict) else None) or "-"
                text = msg.get("message", "") if isinstance(msg, dict) else str(msg)
                key = (profile, cid, code)
                e = found.setdefault(key, {"status": log["status"], "fonts": set(), "message": text,
                                           "network": False})
                if BAD.index(log["status"]) < BAD.index(e["status"]):
                    e["status"] = log["status"]
                e["fonts"].add(os.path.basename(check.get("filename") or "family"))
                if log["status"] == "ERROR" and NETWORK.search(code + " " + text):
                    e["network"] = True
    return found


def accepted():
    """Lines: `<accept|todo>  <profile>  <check id>  <code>  # reason`"""
    out = {}
    for n, line in enumerate(open(ACCEPTED, encoding="utf-8"), 1):
        body = line.split("#", 1)[0].strip()
        if not body:
            continue
        parts = body.split()
        if len(parts) != 4 or parts[0] not in ("accept", "todo"):
            sys.exit(f"{ACCEPTED}:{n}: expected `accept|todo profile check code  # reason`")
        reason = line.split("#", 1)[1].strip() if "#" in line else ""
        if not reason:
            sys.exit(f"{ACCEPTED}:{n}: every entry needs a reason after #")
        out[tuple(parts[1:])] = (parts[0], reason)
    return out


def short(text, n=220):
    return re.sub(r"\s+", " ", text).strip()[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-run", action="store_true", help="only compare existing JSON reports")
    ap.add_argument("--strict", action="store_true", help="network ERRORs also fail the run")
    ap.add_argument("--fontbakery", default="fontbakery")
    a = ap.parse_args()
    if not a.no_run:
        run_fontbakery(a.fontbakery)

    found = {}
    for profile, _, _ in RUNS:
        found.update(results(profile))
    known = accepted()

    new, todo, ok, network = [], [], [], []
    for key, e in sorted(found.items()):
        if key in known:
            (todo if known[key][0] == "todo" else ok).append((key, e))
        elif e["network"]:
            network.append((key, e))
        else:
            new.append((key, e))
    stale = sorted(k for k in known if k not in found)

    def row(key, e):
        return f"  {e['status']:5} {key[0]:11} {key[1]}  [{key[2]}]  ({', '.join(sorted(e['fonts']))})"

    print(f"\nFont Bakery: {len(found)} non-passing results "
          f"(new {len(new)}, todo {len(todo)}, accepted {len(ok)}, network {len(network)}, stale {len(stale)})")
    for title, items in (("NEW (not in documentation/qa/fontbakery-accepted.txt)", new),
                         ("TODO (known defects, still to fix)", todo),
                         ("NETWORK (could not reach the service; re-run online)", network)):
        if items:
            print(f"\n{title}:")
            for key, e in items:
                print(row(key, e))
                print(f"        {short(e['message'])}")
    if stale:
        print("\nSTALE (listed but no longer reported; remove from the accepted list):")
        for key in stale:
            print(f"  {known[key][0]:6} {' '.join(key)}")
    if IN_CI:
        for key, e in new:
            print(f"::error title=fontbakery NEW {key[1]}::[{key[2]}] {short(e['message'], 600)}")
        for key, e in todo:
            print(f"::warning title=fontbakery TODO {key[1]}::[{key[2]}] {known[key][1]}")

    failed = bool(new) or (a.strict and bool(network))
    print("\nRESULT:", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
