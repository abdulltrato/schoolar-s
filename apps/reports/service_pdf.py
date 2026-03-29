from io import BytesIO


def _escape_pdf_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .replace("\r", " ")
        .replace("\n", " ")
    )


def render_pdf_from_context(context: dict) -> bytes:
    student_snapshot = context.get("content", {}).get("student_snapshot", {})
    summary = context.get("content", {}).get("summary", {})
    rows = context.get("content", {}).get("rows", [])
    metadata = context.get("content", {}).get("metadata", {})

    lines = [
        context["title"],
        f"Código: {context['verification_code']}",
        f"Gerado em: {context['generated_at']}",
        f"Periodo: {metadata.get('academic_year') or context.get('period') or 'Sem periodo'}",
    ]
    if student_snapshot:
        lines.append("")
        lines.append("Estudante")
        for key, value in student_snapshot.items():
            lines.append(f"{key}: {value}")
    if summary:
        lines.append("")
        lines.append("Resumo")
        for key, value in summary.items():
            if isinstance(value, (dict, list)):
                continue
            lines.append(f"{key}: {value}")
    if rows:
        lines.append("")
        lines.append("Linhas")
        for index, row in enumerate(rows[:25], start=1):
            lines.append(f"Linha {index}")
            for key, value in row.items():
                if isinstance(value, (dict, list)):
                    continue
                lines.append(f"  {key}: {value}")
    lines.append("")
    lines.append(f"Assinatura: {context['verification_hash']}")

    page_width = 595
    page_height = 842
    current_y = 800
    commands = ["BT", "/F1 11 Tf", "40 800 Td"]
    first_line = True
    for line in lines:
        if current_y < 50:
            break
        safe_line = _escape_pdf_text(line)
        if first_line:
            commands.append(f"({_escape_pdf_text(line)}) Tj")
            first_line = False
        else:
            commands.append("0 -16 Td")
            commands.append(f"({safe_line}) Tj")
        current_y -= 16
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1", errors="replace")

    objects = []

    def add_object(data):
        objects.append(data)
        return len(objects)

    font_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    content_id = add_object(f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1") + stream + b"\nendstream")
    page_id = add_object(
        f"<< /Type /Page /Parent 4 0 R /MediaBox [0 0 {page_width} {page_height}] /Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>".encode(
            "latin-1"
        )
    )
    pages_id = add_object(f"<< /Type /Pages /Kids [{page_id} 0 R] /Count 1 >>".encode("latin-1"))
    catalog_id = add_object(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("latin-1"))

    output = BytesIO()
    output.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(output.tell())
        output.write(f"{index} 0 obj\n".encode("latin-1"))
        output.write(obj)
        output.write(b"\nendobj\n")
    xref_start = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    output.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode("latin-1"))
    output.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode("latin-1")
    )
    return output.getvalue()
