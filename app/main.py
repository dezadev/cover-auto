from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.cover_generator import GenerationResult, generate_covers
from app.models import LayoutConfig

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

app = FastAPI(title="Cover Auto", version="0.1.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")


def render_template(request: Request, template_name: str, context: dict | None = None) -> HTMLResponse:
    page_context = {"request": request}
    if context:
        page_context.update(context)
    return templates.TemplateResponse(request, template_name, page_context)


def output_url(path: Path) -> str:
    relative_path = path.resolve().relative_to(OUTPUT_DIR.resolve())
    return f"/output/{relative_path.as_posix()}"


LAST_RESULT: GenerationResult | None = None


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return render_template(request, "index.html")


@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    files: list[UploadFile] = File(...),
    spine_width_mm: float = Form(18.0),
    gap_mm: float = Form(5.0),
    spine_left_mm: float = Form(57.0),
    margin_top_mm: float = Form(32.0),
) -> HTMLResponse:
    if not files:
        raise HTTPException(status_code=400, detail="Upload minimal satu file PDF.")
    if spine_width_mm <= 0 or gap_mm < 0:
        raise HTTPException(status_code=400, detail="Ukuran punggung harus positif dan gap tidak boleh negatif.")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_dir = OUTPUT_DIR / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_pdfs: list[Path] = []
    with tempfile.TemporaryDirectory(prefix="cover-auto-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        for upload in files:
            if not upload.filename or not upload.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Semua file harus berformat PDF.")
            target = temp_dir / Path(upload.filename).name
            target.write_bytes(await upload.read())
            saved_pdfs.append(target)

        config = LayoutConfig(
            spine_width_mm=spine_width_mm,
            gap_mm=gap_mm,
            spine_left_mm=spine_left_mm,
            margin_top_mm=margin_top_mm,
        )
        result = generate_covers(saved_pdfs, output_dir, config)

    global LAST_RESULT
    LAST_RESULT = result
    preview_items = [
        {
            "page_number": cover.page_number,
            "source_name": cover.source_name,
            "title": cover.title,
            "svg_url": output_url(cover.svg_path),
        }
        for cover in result.covers
    ]
    return render_template(
        request,
        "result.html",
        {
            "result": result,
            "preview_items": preview_items,
            "multipage_url": output_url(result.multipage_svg),
        },
    )


@app.get("/output/{file_path:path}")
def generated_output(file_path: str) -> FileResponse:
    requested_path = (OUTPUT_DIR / file_path).resolve()
    output_root = OUTPUT_DIR.resolve()
    if output_root != requested_path and output_root not in requested_path.parents:
        raise HTTPException(status_code=404, detail="File output tidak ditemukan.")
    if not requested_path.is_file():
        raise HTTPException(status_code=404, detail="File output tidak ditemukan.")
    return FileResponse(requested_path)


@app.get("/download/latest")
def download_latest() -> FileResponse:
    if LAST_RESULT is None or not LAST_RESULT.zip_path.exists():
        raise HTTPException(status_code=404, detail="Belum ada hasil generate.")
    return FileResponse(LAST_RESULT.zip_path, filename="cover_auto_output.zip")


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
