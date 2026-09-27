"""
Ingestion: load knowledge-base markdown files and split them into chunks
suitable for embedding + retrieval. Chunking is by section (## headers)
rather than fixed character windows, since these documents are short and
already well-structured — section-level chunks keep retrieved context
coherent (a whole "Key Indicators" section, not half of one).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

KB_DIR = Path(__file__).resolve().parent.parent / "data" / "knowledge_base"


@dataclass
class Chunk:
    chunk_id: str
    doc_name: str          # filename, e.g. "02_credential_abuse.md"
    doc_title: str         # "Credential Abuse and Valid Accounts"
    section: str           # "Key Indicators"
    text: str
    topic_tags: list[str] = field(default_factory=list)


def _slugify_topic(doc_name: str) -> list[str]:
    stem = doc_name.replace(".md", "")
    parts = re.sub(r"^\d+_", "", stem).split("_")
    return parts


def load_and_chunk() -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(KB_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        doc_title = lines[0].lstrip("# ").strip() if lines else path.stem
        tags = _slugify_topic(path.name)

        section_name = "Overview"
        buffer: list[str] = []
        idx = 0

        def flush():
            nonlocal idx
            body = "\n".join(buffer).strip()
            if body:
                chunks.append(Chunk(
                    chunk_id=f"{path.stem}::{idx}",
                    doc_name=path.name,
                    doc_title=doc_title,
                    section=section_name,
                    text=f"{section_name}\n{body}",
                    topic_tags=tags,
                ))
                idx += 1

        for line in lines[1:]:
            if line.startswith("## "):
                flush()
                buffer = []
                section_name = line.lstrip("# ").strip()
            else:
                buffer.append(line)
        flush()

    return chunks
