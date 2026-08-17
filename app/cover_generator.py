from __future__ import annotations

import html
import re
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path


from app.models import LayoutConfig


@dataclass(frozen=True)
class GeneratedCover:
    source_name: str
    page_number: int
    title: str
    svg_path: Path


@dataclass(frozen=True)
class GenerationResult:
    output_dir: Path
    multipage_svg: Path
    preview_html: Path
    zip_path: Path
    covers: list[GeneratedCover]


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-.")
    return slug[:80] or "cover"


def extract_pdf_text(pdf_path: Path, max_pages: int = 2) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    chunks: list[str] = []
    for page in reader.pages[:max_pages]:
        chunks.append(page.extract_text() or "")
    return "\n".join(chunks).strip()


def infer_spine_title(pdf_path: Path) -> str:
    text = extract_pdf_text(pdf_path)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    useful_lines = [line for line in lines if len(line) > 6]
    if useful_lines:
        return " | ".join(useful_lines[:4])[:180]
    return pdf_path.stem.replace("_", " ").replace("-", " ").title()


def _wrapped_tspans(text: str, x_mm: float, first_y_mm: float, line_height_mm: float) -> str:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        if len(candidate) > 32 and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    if not lines:
        lines = ["Judul punggung"]

    return "\n".join(
        f'<tspan x="{x_mm:.3f}mm" y="{first_y_mm + idx * line_height_mm:.3f}mm">'
        f"{html.escape(line)}</tspan>"
        for idx, line in enumerate(lines[:8])
    )


def build_cover_svg(
    pdf_filename: str,
    title: str,
    config: LayoutConfig,
    page_number: int,
    embedded_pdf_relative_path: str | None = None,
) -> str:
    front_x = config.front_x_mm
    front_y = config.front_y_mm
    spine_x = config.spine_x_mm
    spine_y = config.spine_y_mm
    spine_text_x = spine_x + config.spine_width_mm / 2
    spine_text_y = spine_y + 18
    pdf_label = html.escape(pdf_filename)
    title_text = _wrapped_tspans(title, spine_text_x, spine_text_y, 4.2)
    pdf_link = html.escape(embedded_pdf_relative_path or pdf_filename)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
    width="{config.canvas_width_mm}mm" height="{config.canvas_height_mm}mm"
    viewBox="0 0 {config.canvas_width_mm} {config.canvas_height_mm}">
  <title>Cover page {page_number}: {pdf_label}</title>
  <rect x="0" y="0" width="{config.canvas_width_mm}" height="{config.canvas_height_mm}" fill="#ffffff"/>
  <g id="page-{page_number:03d}" data-source="{pdf_label}">
    <rect x="4" y="4" width="{config.canvas_width_mm - 8}" height="{config.canvas_height_mm - 8}"
      fill="none" stroke="#b8b8b8" stroke-width="0.25"/>
    <rect x="{spine_x}" y="{spine_y}" width="{config.spine_width_mm}" height="{config.front_height_mm}"
      fill="#ffffff" stroke="#333333" stroke-width="0.35"/>
    <rect x="{front_x}" y="{front_y}" width="{config.front_width_mm}" height="{config.front_height_mm}"
      fill="#ffffff" stroke="#333333" stroke-width="0.35"/>
    <line x1="{spine_x + config.spine_width_mm + config.gap_mm / 2}" y1="{front_y}"
      x2="{spine_x + config.spine_width_mm + config.gap_mm / 2}" y2="{front_y + config.front_height_mm}"
      stroke="#c00000" stroke-width="0.2" stroke-dasharray="2 1"/>
    <text x="{spine_text_x}mm" y="{spine_text_y}mm" font-family="Arial, sans-serif" font-size="3.2mm"
      text-anchor="middle" transform="rotate(-90 {spine_text_x} {spine_text_y})">{title_text}</text>
    <text x="{front_x + config.front_width_mm / 2}" y="{front_y + 18}" font-family="Arial, sans-serif"
      font-size="4" text-anchor="middle" fill="#666666">Area cover depan dari PDF</text>
    <text x="{front_x + config.front_width_mm / 2}" y="{front_y + 26}" font-family="Arial, sans-serif"
      font-size="3" text-anchor="middle" fill="#666666">Import/place halaman pertama: {pdf_label}</text>
    <a xlink:href="{pdf_link}">
      <rect x="{front_x + 8}" y="{front_y + 34}" width="{config.front_width_mm - 16}" height="{config.front_height_mm - 48}"
        fill="none" stroke="#999999" stroke-width="0.2" stroke-dasharray="3 2"/>
    </a>
  </g>
</svg>
'''


def generate_covers(
    pdf_paths: list[Path],
    output_dir: Path,
    config: LayoutConfig,
    custom_titles: dict[str, str] | None = None,
) -> GenerationResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    source_dir = output_dir / "source_pdfs"
    source_dir.mkdir(exist_ok=True)

    covers: list[GeneratedCover] = []
    symbols: list[str] = []
    uses: list[str] = []

    for index, pdf_path in enumerate(pdf_paths, start=1):
        copied_pdf = source_dir / pdf_path.name
        if pdf_path.resolve() != copied_pdf.resolve():
            shutil.copy2(pdf_path, copied_pdf)
        title = (custom_titles or {}).get(pdf_path.name) or infer_spine_title(pdf_path)
        svg_name = f"page_{index:03d}_{safe_slug(pdf_path.stem)}.svg"
        svg_path = output_dir / svg_name
        relative_pdf = f"source_pdfs/{copied_pdf.name}"
        svg = build_cover_svg(pdf_path.name, title, config, index, relative_pdf)
        svg_path.write_text(svg, encoding="utf-8")
        covers.append(GeneratedCover(pdf_path.name, index, title, svg_path))
        inner = svg.split('<g id="page-', 1)[1].rsplit("</g>", 1)[0]
        symbols.append(f'<g id="cover-{index:03d}" data-page="{index:03d}">{inner}</g>')
        uses.append(f'<use href="#cover-{index:03d}" x="0" y="{(index - 1) * config.canvas_height_mm}"/>')

    multipage_svg = output_dir / "cover_auto_multipage.svg"
    multipage_svg.write_text(
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="{config.canvas_width_mm}mm"
 height="{config.canvas_height_mm * max(len(covers), 1)}mm"
 viewBox="0 0 {config.canvas_width_mm} {config.canvas_height_mm * max(len(covers), 1)}">
<defs>
{chr(10).join(symbols)}
</defs>
{chr(10).join(uses)}
</svg>
''',
        encoding="utf-8",
    )

    preview_html = output_dir / "preview.html"
    preview_html.write_text(_build_preview(covers), encoding="utf-8")

    zip_path = output_dir / "cover_auto_output.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for path in [multipage_svg, preview_html, *[cover.svg_path for cover in covers], *source_dir.iterdir()]:
            zip_file.write(path, path.relative_to(output_dir))

    return GenerationResult(output_dir, multipage_svg, preview_html, zip_path, covers)


def _build_preview(covers: list[GeneratedCover]) -> str:
    items = "\n".join(
        f'<li><a href="{html.escape(cover.svg_path.name)}">Page {cover.page_number}: '
        f"{html.escape(cover.source_name)}</a><br><small>{html.escape(cover.title)}</small></li>"
        for cover in covers
    )
    return f"""<!doctype html>
<html lang="id">
<head><meta charset="utf-8"><title>Preview Cover Auto</title></head>
<body><h1>Preview Cover Auto</h1><ol>{items}</ol></body>
</html>
"""
