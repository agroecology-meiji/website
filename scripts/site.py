#!/usr/bin/env python3
"""Generate, preview, and validate the static lab website."""

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_BASE = "/website"
LOCALES = ("ja", "en")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SAFE_PUBLICATION_TAGS = re.compile(r'^(?:[^<]|<i>|</i>|<a href="https://[^"]+">|</a>)*$')


class BuildError(RuntimeError):
    pass


def load_json(name):
    path = ROOT / "data" / name

    def reject_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise BuildError(f"{path}: duplicate key: {key}")
            result[key] = value
        return result

    try:
        with path.open(encoding="utf-8") as stream:
            return json.load(stream, object_pairs_hook=reject_duplicates)
    except (OSError, json.JSONDecodeError) as error:
        raise BuildError(f"Cannot read {path}: {error}") from error


def require_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise BuildError(f"{label} must be a non-empty string")
    return value


def safe_repo_path(relative):
    candidate = (ROOT / relative).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as error:
        raise BuildError(f"Path escapes the repository: {relative}") from error
    return candidate


def validate_and_load():
    news = load_json("news.json")
    publications = load_json("publications.json")
    gallery = load_json("gallery.json")

    news_items = news.get("items")
    if not isinstance(news_items, list) or not news_items:
        raise BuildError("data/news.json: items must be a non-empty array")
    previous = None
    for index, item in enumerate(news_items):
        label = f"data/news.json items[{index}]"
        date = require_text(item.get("date"), f"{label}.date")
        if not DATE_RE.match(date):
            raise BuildError(f"{label}.date must use YYYY-MM-DD")
        if previous and date > previous:
            raise BuildError("data/news.json items must be newest first")
        previous = date
        require_text(item.get("category"), f"{label}.category")
        for locale in LOCALES:
            copy = item.get(locale)
            if not isinstance(copy, dict):
                raise BuildError(f"{label}.{locale} must be an object")
            require_text(copy.get("title"), f"{label}.{locale}.title")
            paragraphs = copy.get("paragraphs")
            if not isinstance(paragraphs, list) or not paragraphs:
                raise BuildError(f"{label}.{locale}.paragraphs must be a non-empty array")
            for p_index, paragraph in enumerate(paragraphs):
                require_text(paragraph, f"{label}.{locale}.paragraphs[{p_index}]")

    sections = publications.get("sections")
    if not isinstance(sections, list) or not sections:
        raise BuildError("data/publications.json: sections must be a non-empty array")
    section_ids = set()
    for s_index, section in enumerate(sections):
        label = f"data/publications.json sections[{s_index}]"
        section_id = require_text(section.get("id"), f"{label}.id")
        if section_id in section_ids:
            raise BuildError(f"Duplicate publication section id: {section_id}")
        section_ids.add(section_id)
        title = section.get("title")
        if not isinstance(title, dict):
            raise BuildError(f"{label}.title must be an object")
        kicker = section.get("kicker")
        if not isinstance(kicker, dict):
            raise BuildError(f"{label}.kicker must be an object")
        for locale in LOCALES:
            require_text(title.get(locale), f"{label}.title.{locale}")
            require_text(kicker.get(locale), f"{label}.kicker.{locale}")
        items = section.get("items")
        if not isinstance(items, list) or not items:
            raise BuildError(f"{label}.items must be a non-empty array")
        for i_index, item in enumerate(items):
            raw = require_text(item.get("html"), f"{label}.items[{i_index}].html")
            if not SAFE_PUBLICATION_TAGS.fullmatch(raw):
                raise BuildError(f"{label}.items[{i_index}].html may contain only <i> and HTTPS <a> tags")
            locales = item.get("locales", list(LOCALES))
            if not isinstance(locales, list) or not locales or any(x not in LOCALES for x in locales):
                raise BuildError(f"{label}.items[{i_index}].locales is invalid")

    image = gallery.get("image")
    if not isinstance(image, dict):
        raise BuildError("data/gallery.json: image must be an object")
    max_pixels = image.get("max_pixels")
    quality = image.get("jpeg_quality")
    if not isinstance(max_pixels, int) or not 320 <= max_pixels <= 4000:
        raise BuildError("data/gallery.json: image.max_pixels must be 320–4000")
    if not isinstance(quality, int) or not 1 <= quality <= 100:
        raise BuildError("data/gallery.json: image.jpeg_quality must be 1–100")
    gallery["_output_dir"] = safe_repo_path(require_text(image.get("output_directory"), "image.output_directory"))
    items = gallery.get("items")
    if not isinstance(items, list) or not items:
        raise BuildError("data/gallery.json: items must be a non-empty array")
    slideshow_count = gallery.get("slideshow_count")
    if not isinstance(slideshow_count, int) or not 1 <= slideshow_count <= len(items):
        raise BuildError("data/gallery.json: slideshow_count is invalid")
    outputs = set()
    previous = None
    for index, item in enumerate(items):
        label = f"data/gallery.json items[{index}]"
        date = require_text(item.get("date"), f"{label}.date")
        if not DATE_RE.match(date):
            raise BuildError(f"{label}.date must use YYYY-MM-DD")
        if previous and date > previous:
            raise BuildError("data/gallery.json items must be newest first")
        previous = date
        source = safe_repo_path(require_text(item.get("source"), f"{label}.source"))
        if not source.is_file():
            raise BuildError(f"{label}.source does not exist: {source.relative_to(ROOT)}")
        output = require_text(item.get("output"), f"{label}.output")
        if Path(output).name != output or Path(output).suffix.lower() not in (".jpg", ".jpeg"):
            raise BuildError(f"{label}.output must be a JPEG filename without directories")
        if output in outputs:
            raise BuildError(f"Duplicate gallery output: {output}")
        outputs.add(output)
        for locale in LOCALES:
            copy = item.get(locale)
            if not isinstance(copy, dict):
                raise BuildError(f"{label}.{locale} must be an object")
            for field in ("date_label", "title", "summary", "body", "alt"):
                require_text(copy.get(field), f"{label}.{locale}.{field}")
    return news, publications, gallery


def e(value):
    return html.escape(str(value), quote=True)


def display_date(value):
    return value.replace("-", ".")


def news_page_block(items, locale):
    lines = []
    for item in items:
        copy = item[locale]
        lines += [
            '        <article class="card news-card">',
            f'          <div><div class="news-date">{e(display_date(item["date"]))}</div><span class="tag">{e(item["category"])}</span></div>',
            "          <div>",
            f'            <h2 class="news-title">{e(copy["title"])}</h2>',
        ]
        lines += [f'            <p class="news-text">{e(paragraph)}</p>' for paragraph in copy["paragraphs"]]
        lines += ["          </div>", "        </article>"]
    return "\n".join(lines)


def latest_news_block(items, locale):
    href = f"{PUBLIC_BASE}{'/en' if locale == 'en' else ''}/news/"
    lines = []
    for item in items[:3]:
        lines += [
            f'          <a class="latest-item" href="{href}">',
            f'            <time class="latest-date" datetime="{e(item["date"])}">{e(display_date(item["date"]))}</time>',
            f'            <span class="latest-text">{e(item[locale]["title"])}</span>',
            "          </a>",
        ]
    return "\n".join(lines)


def publications_block(sections, locale):
    blocks = []
    for section in sections:
        items = [item for item in section["items"] if locale in item.get("locales", list(LOCALES))]
        if not items:
            continue
        kicker = section["kicker"][locale]
        title = section["title"][locale]
        lines = [
            '        <section class="card pub-section">',
            f'          <p class="section-kicker">{e(kicker)}</p>',
            f'          <h2 class="card-title">{e(title)}</h2>',
            '          <ul class="publication-list">',
        ]
        for item in items:
            raw = re.sub(r'<a href="([^"]+)">', r'<a href="\1" target="_blank" rel="noopener noreferrer">', item["html"])
            lines.append(f"            <li>{raw}</li>")
        lines.append("          </ul>")
        more = section.get("more_link")
        if more:
            lines.append(f'          <p style="margin:22px 0 0;"><a class="btn btn--small" href="{e(more["url"])}" target="_blank" rel="noopener noreferrer">{e(more["label"][locale])}</a></p>')
        lines.append("        </section>")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def image_url(gallery, item):
    directory = gallery["_output_dir"].relative_to(ROOT).as_posix()
    return f"{PUBLIC_BASE}/{directory}/{item['output']}"


def gallery_slideshow_block(gallery, locale):
    labels = {"ja": ("前の写真", "次の写真", "写真の選択"), "en": ("Previous photo", "Next photo", "Choose a photo")}[locale]
    items = gallery["items"][:gallery["slideshow_count"]]
    lines = []
    for index, item in enumerate(items):
        copy = item[locale]
        active = " is-active" if index == 0 else ""
        lines.append(f'      <div class="slide{active}"><img class="no-save" src="{e(image_url(gallery, item))}" alt="{e(copy["alt"])}"><div class="slide__caption"><div class="slide__label">{e(display_date(item["date"]))}</div><h2 class="slide__title">{e(copy["title"])}</h2><p class="slide__text">{e(copy["summary"])}</p></div></div>')
    lines += [
        f'      <button class="slide-btn slide-btn--prev" type="button" data-slide-prev aria-label="{labels[0]}">‹</button>',
        f'      <button class="slide-btn slide-btn--next" type="button" data-slide-next aria-label="{labels[1]}">›</button>',
        f'      <div class="slide-dots" role="tablist" aria-label="{labels[2]}">',
    ]
    for index in range(len(items)):
        active = " is-active" if index == 0 else ""
        selected = "true" if index == 0 else "false"
        label = f"{index + 1}枚目" if locale == "ja" else f"Photo {index + 1}"
        lines.append(f'        <button class="slide-dot{active}" type="button" data-slide-to="{index}" aria-label="{label}" aria-selected="{selected}"></button>')
    lines.append("      </div>")
    return "\n".join(lines)


def gallery_log_block(gallery, locale):
    groups = []
    for item in gallery["items"]:
        year = item["date"][:4]
        if not groups or groups[-1][0] != year:
            groups.append((year, []))
        groups[-1][1].append(item)
    sections = []
    for year, items in groups:
        lines = [
            '    <section class="section reveal">', '      <div class="section-head">', "        <div>",
            f'          <p class="section-kicker">{year}</p>', '          <h2 class="section-title">Activity log</h2>',
            "        </div>", "      </div>", '      <div class="gallery-grid">',
        ]
        for item in items:
            copy = item[locale]
            lines.append(f'        <article class="gallery-entry"><div class="gallery-date">{e(copy["date_label"])}</div><div class="gallery-entry__text"><p>{e(copy["body"])}</p></div><img class="gallery-entry__img no-save" src="{e(image_url(gallery, item))}" alt="{e(copy["alt"])}" draggable="false"></article>')
        lines += ["      </div>", "    </section>"]
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def replace_block(path, block_id, generated, write):
    text = path.read_text(encoding="utf-8")
    start, end = f"<!-- AUTO:{block_id}:START -->", f"<!-- AUTO:{block_id}:END -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if len(pattern.findall(text)) != 1:
        raise BuildError(f"{path.relative_to(ROOT)} must contain exactly one {block_id} marker pair")
    result = pattern.sub(lambda _: f"{start}\n{generated}\n{end}", text)
    changed = result != text
    if changed and write:
        path.write_text(result, encoding="utf-8")
    return changed


def html_updates(news, publications, gallery, write):
    jobs = [
        ("news/index.html", "NEWS", news_page_block(news["items"], "ja")),
        ("en/news/index.html", "NEWS", news_page_block(news["items"], "en")),
        ("index.html", "LATEST_NEWS", latest_news_block(news["items"], "ja")),
        ("en/index.html", "LATEST_NEWS", latest_news_block(news["items"], "en")),
        ("publications/index.html", "PUBLICATIONS", publications_block(publications["sections"], "ja")),
        ("en/publications/index.html", "PUBLICATIONS", publications_block(publications["sections"], "en")),
        ("gallery/index.html", "GALLERY_SLIDES", gallery_slideshow_block(gallery, "ja")),
        ("en/gallery/index.html", "GALLERY_SLIDES", gallery_slideshow_block(gallery, "en")),
        ("gallery/index.html", "GALLERY_LOG", gallery_log_block(gallery, "ja")),
        ("en/gallery/index.html", "GALLERY_LOG", gallery_log_block(gallery, "en")),
    ]
    return [path for path, block_id, generated in jobs if replace_block(ROOT / path, block_id, generated, write)]


def strip_jpeg_metadata(path):
    data = path.read_bytes()
    if not data.startswith(b"\xff\xd8"):
        raise BuildError(f"Generated image is not a JPEG: {path}")
    output, pos = bytearray(data[:2]), 2
    while pos < len(data):
        if data[pos] != 0xFF:
            raise BuildError(f"Invalid JPEG segment in {path}")
        marker_start = pos
        while pos < len(data) and data[pos] == 0xFF:
            pos += 1
        marker, pos = data[pos], pos + 1
        if marker == 0xDA:
            output.extend(data[marker_start:])
            break
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            output.extend(data[marker_start:pos])
            continue
        length = struct.unpack(">H", data[pos:pos + 2])[0]
        segment_end = pos + length
        if length < 2 or segment_end > len(data):
            raise BuildError(f"Invalid JPEG segment length in {path}")
        if marker == 0xE0 or not (0xE0 <= marker <= 0xEF or marker == 0xFE):
            output.extend(data[marker_start:segment_end])
        pos = segment_end
    path.write_bytes(output)


def jpeg_info(path):
    data, pos, width, height, metadata = path.read_bytes(), 2, None, None, []
    if not data.startswith(b"\xff\xd8"):
        raise BuildError(f"Not a JPEG: {path.relative_to(ROOT)}")
    sof = set(range(0xC0, 0xD0)) - {0xC4, 0xC8, 0xCC}
    while pos < len(data) and data[pos] == 0xFF:
        while pos < len(data) and data[pos] == 0xFF:
            pos += 1
        marker, pos = data[pos], pos + 1
        if marker == 0xDA:
            break
        if marker in (0xD8, 0xD9):
            continue
        length = struct.unpack(">H", data[pos:pos + 2])[0]
        if marker in sof and length >= 7:
            height, width = struct.unpack(">HH", data[pos + 3:pos + 7])
        if 0xE1 <= marker <= 0xEF or marker == 0xFE:
            metadata.append(marker)
        pos += length
    if width is None or height is None:
        raise BuildError(f"Cannot read JPEG dimensions: {path.relative_to(ROOT)}")
    return width, height, metadata


def generate_images(gallery):
    if not Path("/usr/bin/qlmanage").is_file() or not Path("/usr/bin/sips").is_file():
        raise BuildError("Image generation requires the standard macOS image tools")
    output_dir = gallery["_output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    settings = gallery["image"]
    for item in gallery["items"]:
        source, destination = safe_repo_path(item["source"]), output_dir / item["output"]
        # Quick Look may finish writing just after its process exits. Keep its
        # scratch directory outside the repository so no temporary artifact
        # can enter a commit even in that edge case.
        with tempfile.TemporaryDirectory(prefix="agroecology-gallery-") as preview_dir:
            preview = Path(preview_dir)
            result = subprocess.run(
                ["/usr/bin/qlmanage", "-t", "-s", str(settings["max_pixels"]), "-o", str(preview), str(source)],
                capture_output=True, text=True,
            )
            previews = list(preview.iterdir())
            if result.returncode or len(previews) != 1:
                raise BuildError(f"Cannot decode {source.relative_to(ROOT)}: {result.stderr.strip()}")
            handle, temporary_name = tempfile.mkstemp(prefix=".gallery-", suffix=".jpg", dir=output_dir)
            temporary = Path(temporary_name)
            os.close(handle)
            temporary.unlink()
            result = subprocess.run(
                ["/usr/bin/sips", "-s", "format", "jpeg", "-s", "formatOptions", str(settings["jpeg_quality"]), str(previews[0]), "--out", str(temporary)],
                capture_output=True, text=True,
            )
            if result.returncode:
                raise BuildError(f"Cannot encode {source.relative_to(ROOT)}: {result.stderr.strip()}")
            strip_jpeg_metadata(temporary)
            temporary.replace(destination)


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.images_without_alt = [], []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag in ("a", "link", "script", "img"):
            attribute = "href" if tag in ("a", "link") else "src"
            if values.get(attribute):
                self.links.append(values[attribute])
        if tag == "img" and not values.get("alt"):
            self.images_without_alt.append(self.getpos())


def check_html_links():
    errors = []
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        parser = LinkCollector()
        parser.feed(path.read_text(encoding="utf-8"))
        for line, column in parser.images_without_alt:
            errors.append(f"{path.relative_to(ROOT)}:{line}:{column}: image has no alt text")
        for link in parser.links:
            parsed = urlsplit(link)
            if parsed.scheme or link.startswith(("#", "mailto:", "tel:", "//")):
                continue
            clean = unquote(parsed.path)
            if clean.startswith(PUBLIC_BASE + "/"):
                target = ROOT / clean[len(PUBLIC_BASE) + 1:]
            elif clean.startswith("/"):
                errors.append(f"{path.relative_to(ROOT)}: unexpected site-root link: {link}")
                continue
            else:
                target = path.parent / clean
            if clean.endswith("/"):
                target /= "index.html"
            if not target.exists():
                errors.append(f"{path.relative_to(ROOT)}: missing internal target: {link}")
    return errors


def build():
    news, publications, gallery = validate_and_load()
    generate_images(gallery)
    changed = html_updates(news, publications, gallery, True)
    print(f"Site generated: {len(changed)} HTML file(s) updated, {len(gallery['items'])} image(s) optimized.")


def check():
    news, publications, gallery = validate_and_load()
    errors = [f"Generated content is stale: {path} (run site generation)" for path in html_updates(news, publications, gallery, False)]
    source_hashes, output_hashes = {}, {}
    expected_outputs = {item["output"] for item in gallery["items"]}
    if gallery["_output_dir"].is_dir():
        for child in gallery["_output_dir"].iterdir():
            if child.name not in expected_outputs:
                errors.append(f"Unexpected file in generated image directory: {child.relative_to(ROOT)}")
    for item in gallery["items"]:
        path = gallery["_output_dir"] / item["output"]
        if not path.is_file():
            errors.append(f"Missing generated gallery image: {path.relative_to(ROOT)}")
            continue
        width, height, metadata = jpeg_info(path)
        if max(width, height) > gallery["image"]["max_pixels"]:
            errors.append(f"{path.relative_to(ROOT)} is {width}x{height}, above the configured maximum")
        if metadata:
            errors.append(f"{path.relative_to(ROOT)} contains metadata segments: {metadata}")
        source_hash = hashlib.sha256(safe_repo_path(item["source"]).read_bytes()).hexdigest()
        output_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if output_hash in output_hashes and source_hash != source_hashes[output_hash]:
            errors.append(f"Different source images produced identical output: {output_hashes[output_hash]} and {path.relative_to(ROOT)}")
        source_hashes[output_hash] = source_hash
        output_hashes[output_hash] = path.relative_to(ROOT)
    errors += check_html_links()
    if errors:
        print("Pre-publication check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print("Pre-publication check passed: JSON, generated HTML, images, metadata, links, and alt text are valid.")


class PreviewHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        parsed = urlsplit(path).path
        if parsed == PUBLIC_BASE:
            parsed += "/"
        if parsed.startswith(PUBLIC_BASE + "/"):
            parsed = parsed[len(PUBLIC_BASE):]
        return str(ROOT / unquote(parsed).lstrip("/"))

    def do_GET(self):
        if urlsplit(self.path).path == "/":
            self.send_response(302)
            self.send_header("Location", PUBLIC_BASE + "/")
            self.end_headers()
            return
        super().do_GET()


def serve(port):
    build()
    server = ThreadingHTTPServer(("127.0.0.1", port), PreviewHandler)
    print(f"Preview: http://localhost:{port}{PUBLIC_BASE}/")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPreview stopped.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("build")
    preview = commands.add_parser("serve")
    preview.add_argument("--port", type=int, default=8000)
    commands.add_parser("check")
    args = parser.parse_args()
    try:
        {"build": build, "check": check}.get(args.command, lambda: serve(args.port))()
    except BuildError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
