import logging
import pathlib
from typing import Any

import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector

logger = logging.getLogger(__name__)

# Configure LanceDB and embeddings
# Using a local, fast model for 2026 SOTA standards
registry = get_registry().get("sentence-transformers")
model = registry.create(name="all-MiniLM-L6-v2")


class GuideChunk(LanceModel):
    vector: Vector(model.ndims()) = model.VectorField()
    text: str = model.SourceField()
    filename: str
    title: str


class ResoniteRAG:
    def __init__(self, db_path: str = "./.lancedb"):
        self.db_path = db_path
        self.db = lancedb.connect(db_path)
        self.table_name = "resonite_guides"
        self.table = None

    async def initialize(self, force_reindex: bool = False):
        """Initialize the database and index guides if necessary."""
        if self.table_name in self.db.table_names() and not force_reindex:
            self.table = self.db.open_table(self.table_name)
            logger.info(f"Connected to existing LanceDB table: {self.table_name}")
            return

        logger.info("Indexing Resonite guides...")
        data = self._load_guides()
        self.table = self.db.create_table(self.table_name, schema=GuideChunk, mode="overwrite")
        self.table.add(data)
        logger.info(f"Indexed {len(data)} chunks from guides.")

    def _load_guides(self) -> list[dict[str, Any]]:
        """Scan repository for *.md files and chunk them."""
        chunks = []
        repo_root = pathlib.Path(__file__).parent.parent.parent
        guide_patterns = ["*.md", "docs/**/*.md"]

        for pattern in guide_patterns:
            for file_path in repo_root.glob(pattern):
                if ".gemini" in str(file_path) or "node_modules" in str(file_path):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8")
                    title = self._extract_title(content) or file_path.name

                    # Simple chunking by paragraph/section
                    sections = content.split("\n## ")
                    for section in sections:
                        if not section.strip():
                            continue

                        chunks.append(
                            {
                                "text": section.strip(),
                                "filename": file_path.name,
                                "title": title,
                            }
                        )
                except Exception as e:
                    logger.error(f"Failed to read {file_path}: {e}")

        return chunks

    def _extract_title(self, content: str) -> str | None:
        """Extract first H1 from markdown."""
        for line in content.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return None

    async def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Perform semantic search."""
        if not self.table:
            await self.initialize()

        results = self.table.search(query).limit(limit).to_list()
        return [
            {
                "text": r["text"],
                "title": r["title"],
                "filename": r["filename"],
                "score": r["_distance"],
            }
            for r in results
        ]


# Global instance
rag_engine = ResoniteRAG()
