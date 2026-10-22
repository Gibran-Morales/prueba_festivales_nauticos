#!/usr/bin/env python3
"""
Mirror recursivo (offline clone) de https://core-62.com/FestivalesNauticos/
Equivalente en Python puro (sin dependencias) a:
  wget --mirror --convert-links --adjust-extension --page-requisites \
       --no-parent --page-requisites -e robots=off <URL>

Uso:
  python mirror_site.py

Salida:
  <OUTPUT_DIR>/core-62.com/FestivalesNauticos/...  (estructura idéntica al sitio)
  manifest.json con el listado de URLs descargadas y su status
"""
import os
import re
import sys
import json
import time
import queue
import urllib.request
import urllib.error
import urllib.parse
import html.parser

BASE_HOST = "core-62.com"
SCHEME = "https"
ROOT_PREFIX = "/FestivalesNauticos/"   # limitamos el rastreo a este microsite
SEED_URLS = [
    "https://core-62.com/FestivalesNauticos/index.html",
    "https://core-62.com/FestivalesNauticos/invitacion-panama.html",
    "https://core-62.com/FestivalesNauticos/concanaco.html",
    "https://core-62.com/FestivalesNauticos/chalchiuhtlicue.html",
    "https://core-62.com/FestivalesNauticos/cdmx-trajinera.html",
    "https://core-62.com/FestivalesNauticos/Reportes/Reporte_Seguimiento_Propuestas_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/propuesta-exafm-fnmx-2026.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Michoacan_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Puebla_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Queretaro_FNMX_2026-2027.html",
    # Descubiertas dentro del dashboard de seguimiento (Reportes/...): 32 propuestas
    # estatales + 19 propuestas de marca, enlazadas pero no visibles en el menu principal.
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Oaxaca_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Jalisco_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Baja_California_Sur_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Nayarit_FNMX_2026-2027_FINAL.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Sinaloa_FNMX_2026-2027_FINAL.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Guerrero_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Tabasco_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Tamaulipas_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Sonora_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Veracruz_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Nuevo_Leon_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Quintana_Roo_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Campeche_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Yucatan_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_San_Luis_Potosi_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Coahuila_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Chihuahua_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Hidalgo_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Estado_de_Mexico_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Aguascalientes_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Chiapas_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Ciudad_de_Mexico_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Colima_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Guanajuato_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Morelos_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Zacatecas_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Baja_California_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Estados/Propuesta_SECTUR_Tlaxcala_FNMX_2026-2027.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/propuesta-heineken-fnmx-2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/propuesta-lacostena-fnmx-2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/propuesta-montana-colors-fnmx-2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/propuesta-the-place-at-cabo-fnmx-2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/Propuesta_BBVA_Bonos_Azules_Festivales_Nauticos_2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/Propuesta_TAJIN_FNMX_2026_2027.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/Propuesta_TELCEL_FNMX_2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/Propuesta_SALSA_HUICHOL_FNMX_2026%283%29.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/Propuesta_FNMX_Nu_Mexico_2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/Propuesta_CONVERSE_FNMX_2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/Propuesta_TEQUILA_PATRON_FNMX_2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/Propuesta_ANDREA_FNMX_2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/Propuesta_AY_GUEY_FNMX_2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/Propuesta_PEPSI_FNMX_2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/Propuesta_NIVADA_FNMX_2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/Propuesta_LIVERPOOL_FNMX_2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/Propuesta_BAJA_FERRIES_FNMX_2026.html",
    "https://core-62.com/FestivalesNauticos/Propuestas/Propuesta_AIRBNB_FNMX_2026.html",
]

OUTPUT_DIR = os.environ.get("MIRROR_OUTPUT", os.path.join(os.getcwd(), "Resplado_WEB"))
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FestivalesNauticosBackupBot/1.0"
DELAY = 0.25  # segundos entre requests, para no saturar el servidor
MAX_PAGES = 500

HTML_EXTS = (".html", ".htm", "")
BINARY_EXTS = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico",
               ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".mp3", ".zip", ".doc",
               ".docx", ".xls", ".xlsx", ".ppt", ".pptx")

visited = set()
manifest = {}
to_visit = queue.Queue()
for u in SEED_URLS:
    to_visit.put(u)


ASSET_EXTS = (".css", ".js", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
              ".ico", ".woff", ".woff2", ".ttf", ".eot", ".pdf", ".mp4", ".mp3")


def in_scope(url):
    """Pages we are allowed to recurse INTO (follow their outgoing links)."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    if parsed.netloc != BASE_HOST:
        return False
    if not parsed.path.startswith(ROOT_PREFIX):
        return False
    return True


def is_same_host_asset(url):
    """Static assets on the same host we should download even if outside
    ROOT_PREFIX (shared /css/, /js/, /img/ style folders), but never recurse
    into them as HTML pages."""
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc != BASE_HOST:
        return False
    return parsed.path.lower().endswith(ASSET_EXTS)


def normalize(url, base):
    url = url.strip()
    if not url or url.startswith(("mailto:", "tel:", "javascript:", "data:", "#")):
        return None
    joined = urllib.parse.urljoin(base, url)
    joined, _frag = urllib.parse.urldefrag(joined)
    return joined


def url_to_local_path(url):
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    if path.endswith("/"):
        path += "index.html"
    segments = [urllib.parse.unquote(s) for s in path.split("/")]
    local = os.path.join(OUTPUT_DIR, parsed.netloc, *[s for s in segments if s != ""])
    root, ext = os.path.splitext(local)
    if ext == "" :
        local = local + ".html"
    if parsed.query:
        root, ext = os.path.splitext(local)
        safe_q = re.sub(r"[^A-Za-z0-9_.-]", "_", parsed.query)[:80]
        local = f"{root}__{safe_q}{ext}"
    return local


class LinkExtractor(html.parser.HTMLParser):
    ATTRS_WITH_URLS = {
        "a": ["href"],
        "link": ["href"],
        "script": ["src"],
        "img": ["src", "data-src"],
        "source": ["src", "srcset"],
        "iframe": ["src"],
        "embed": ["src"],
        "object": ["data"],
        "video": ["src", "poster"],
        "audio": ["src"],
        "form": [],  # ignore form actions (no submission during mirror)
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        wanted = self.ATTRS_WITH_URLS.get(tag, [])
        for a in wanted:
            v = d.get(a)
            if not v:
                continue
            if a == "srcset":
                for part in v.split(","):
                    u = part.strip().split(" ")[0]
                    if u:
                        self.links.append(u)
            else:
                self.links.append(v)
        style = d.get("style")
        if style:
            self.links.extend(re.findall(r"url\((['\"]?)(.*?)\1\)", style))


CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)")


def extract_links_from_html(content, base_url):
    parser = LinkExtractor()
    try:
        parser.feed(content)
    except Exception:
        pass
    links = []
    for l in parser.links:
        if isinstance(l, tuple):
            l = l[1]
        n = normalize(l, base_url)
        if n:
            links.append(n)
    # also catch inline <style> blocks CSS url()
    for m in CSS_URL_RE.finditer(content):
        n = normalize(m.group(2), base_url)
        if n:
            links.append(n)
    return links


def extract_links_from_css(content, base_url):
    links = []
    for m in CSS_URL_RE.finditer(content):
        n = normalize(m.group(2), base_url)
        if n:
            links.append(n)
    for m in re.finditer(r"@import\s+['\"](.*?)['\"]", content):
        n = normalize(m.group(1), base_url)
        if n:
            links.append(n)
    return links


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
        ctype = resp.headers.get("Content-Type", "")
        status = resp.status
    return data, ctype, status


def save(local_path, data):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "wb") as f:
        f.write(data)


def main():
    count = 0
    while not to_visit.empty() and count < MAX_PAGES:
        url = to_visit.get()
        if url in visited:
            continue
        visited.add(url)
        count += 1
        try:
            data, ctype, status = fetch(url)
        except urllib.error.HTTPError as e:
            manifest[url] = {"status": e.code, "error": str(e)}
            print(f"[HTTP {e.code}] {url}")
            continue
        except Exception as e:
            manifest[url] = {"status": "ERROR", "error": str(e)}
            print(f"[ERROR] {url}: {e}")
            continue

        local_path = url_to_local_path(url)
        save(local_path, data)
        manifest[url] = {"status": status, "local": os.path.relpath(local_path, OUTPUT_DIR), "content_type": ctype}
        print(f"[{status}] {url} -> {os.path.relpath(local_path, OUTPUT_DIR)}")

        is_html = "text/html" in ctype or local_path.endswith((".html", ".htm"))
        is_css = "text/css" in ctype or local_path.endswith(".css")

        if is_html:
            try:
                text = data.decode("utf-8", errors="replace")
            except Exception:
                text = data.decode("latin-1", errors="replace")
            for link in extract_links_from_html(text, url):
                if link in visited:
                    continue
                if in_scope(link) or is_same_host_asset(link):
                    to_visit.put(link)
        elif is_css:
            try:
                text = data.decode("utf-8", errors="replace")
            except Exception:
                text = data.decode("latin-1", errors="replace")
            for link in extract_links_from_css(text, url):
                if link not in visited and (in_scope(link) or is_same_host_asset(link)):
                    to_visit.put(link)

        time.sleep(DELAY)

    convert_links()

    with open(os.path.join(OUTPUT_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\nTotal URLs procesadas: {len(visited)}")
    print(f"Guardado en: {OUTPUT_DIR}")


def convert_links():
    """Reescribe URLs absolutas (https://core-62.com/...) en los HTML/CSS
    guardados para que apunten a los archivos locales del espejo, de modo
    que el sitio funcione 100% offline (equivalente a wget --convert-links)."""
    url_to_local = {}
    for url, info in manifest.items():
        if not isinstance(info, dict) or "local" not in info:
            continue
        local_abs = os.path.join(OUTPUT_DIR, info["local"])
        variants = {url}
        if url.startswith("https://"):
            variants.add("http://" + url[len("https://"):])
            variants.add("//" + url[len("https://"):])
        elif url.startswith("http://"):
            variants.add("https://" + url[len("http://"):])
            variants.add("//" + url[len("http://"):])
        for v in variants:
            url_to_local[v] = local_abs

    sorted_urls = sorted(url_to_local.keys(), key=len, reverse=True)

    for url, info in manifest.items():
        if not isinstance(info, dict) or "local" not in info:
            continue
        local_path = os.path.join(OUTPUT_DIR, info["local"])
        if not local_path.lower().endswith((".html", ".htm", ".css")):
            continue
        try:
            with open(local_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except Exception:
            continue
        original = text
        file_dir = os.path.dirname(local_path)
        for u in sorted_urls:
            if u in text:
                target = url_to_local[u]
                rel = os.path.relpath(target, file_dir).replace(os.sep, "/")
                rel_quoted = urllib.parse.quote(rel, safe="/%")
                text = text.replace(u, rel_quoted)
        if text != original:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"[convert-links] actualizado: {os.path.relpath(local_path, OUTPUT_DIR)}")


if __name__ == "__main__":
    main()
