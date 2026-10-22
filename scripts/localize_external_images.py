#!/usr/bin/env python3
"""Descarga las imagenes de terceros (hotlinked desde otros dominios,
no core-62.com) que aparecen en el sitio FNMX y reescribe las referencias
en el HTML para que apunten a copias locales, dentro de:
  FestivalesNauticos/external_img/<host>/<archivo>
"""
import os
import re
import glob
import hashlib
import urllib.request
import urllib.parse

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")  # not used; run from FestivalesNauticos dir
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FestivalesNauticosBackupBot/1.0"
IMG_EXT_RE = re.compile(r'https?://[^"\'\s\)]+\.(?:png|jpe?g|gif|webp|svg|ico)(?:\?[^"\'\s\)]*)?', re.I)
EXTERNAL_DIR = "external_img"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Referer": "https://core-62.com/"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read(), resp.headers.get("Content-Type", "")


def local_name(url):
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc
    base = os.path.basename(parsed.path)
    if not base:
        base = "img"
    # avoid collisions: prefix short hash of full url
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    root, ext = os.path.splitext(base)
    if not ext:
        ext = ".jpg"
    safe_root = re.sub(r"[^A-Za-z0-9_.-]", "_", root)[:60]
    return os.path.join(EXTERNAL_DIR, host, f"{safe_root}_{h}{ext}")


def main():
    html_files = glob.glob("**/*.html", recursive=True)
    all_urls = {}
    for path in html_files:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        for m in IMG_EXT_RE.finditer(text):
            url = m.group(0)
            if "core-62.com" in url or "openstreetmap.org" in url:
                continue
            all_urls.setdefault(url, []).append(path)

    print(f"Encontradas {len(all_urls)} imagenes externas unicas en {len(html_files)} paginas.")

    url_to_local = {}
    for url in all_urls:
        local_rel = local_name(url)
        try:
            data, ctype = fetch(url)
        except Exception as e:
            print(f"[ERROR] {url}: {e}")
            continue
        os.makedirs(os.path.dirname(local_rel), exist_ok=True)
        with open(local_rel, "wb") as f:
            f.write(data)
        url_to_local[url] = local_rel
        print(f"[OK] {url}\n     -> {local_rel} ({len(data)} bytes, {ctype})")

    # Segunda pasada: reemplazar cada URL externa por su ruta relativa local en cada HTML
    sorted_urls = sorted(url_to_local.keys(), key=len, reverse=True)
    for path in html_files:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        original = text
        file_dir = os.path.dirname(path)
        for url in sorted_urls:
            if url in text:
                target = url_to_local[url]
                rel = os.path.relpath(target, file_dir if file_dir else ".").replace(os.sep, "/")
                rel_quoted = urllib.parse.quote(rel, safe="/%")
                text = text.replace(url, rel_quoted)
        if text != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"[convert-links externo] actualizado: {path}")

    print(f"\nTotal localizadas: {len(url_to_local)} / {len(all_urls)}")


if __name__ == "__main__":
    main()
