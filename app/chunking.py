import re
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


def normalize_text(text: str) -> str:
    """Normalize whitespace while preserving paragraph boundaries."""

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")

    normalized_text = re.sub(
        r"[ \t]+",
        " ",
        normalized_text,
    )

    normalized_text = re.sub(
        r" *\n *",
        "\n",
        normalized_text,
    )

    normalized_text = re.sub(
        r"\n{3,}",
        "\n\n",
        normalized_text,
    )

    return normalized_text.strip()


def read_pdf(file_path: Path) -> str:
    """Extract and normalize text from a PDF document."""

    reader = PdfReader(file_path)
    pages: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text()

        if not page_text:
            continue

        normalized_page = normalize_text(page_text)

        if normalized_page:
            pages.append(normalized_page)

    return "\n\n".join(pages)


def read_txt(file_path: Path) -> str:
    """Read and normalize a UTF-8 encoded TXT document."""

    text = file_path.read_text(
        encoding="utf-8",
    )

    return normalize_text(text)


def read_document(file_path: Path) -> str:
    """Read a supported document according to its file extension."""

    if not isinstance(file_path, Path):
        raise TypeError(
            "file_path must be a pathlib.Path instance."
        )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Path is not a file: {file_path}"
        )

    suffix = file_path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {suffix}. "
            f"Supported types: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    if suffix == ".pdf":
        document_text = read_pdf(file_path)
    else:
        document_text = read_txt(file_path)

    if not document_text:
        raise ValueError(
            "No readable text could be extracted from "
            f"the document: {file_path}"
        )

    return document_text


def chunk_text(
    text: str,
    chunk_size: int = 600,
    overlap: int = 80,
    minimum_chunk_size: int = 50,
) -> list[str]:
    """
    Split text into word-safe overlapping character chunks.

    Paragraph boundaries are preserved where possible. Chunk size and
    overlap are measured in characters rather than tokens.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    if (
        not isinstance(chunk_size, int)
        or isinstance(chunk_size, bool)
    ):
        raise TypeError(
            "chunk_size must be an integer."
        )

    if (
        not isinstance(overlap, int)
        or isinstance(overlap, bool)
    ):
        raise TypeError(
            "overlap must be an integer."
        )

    if (
        not isinstance(minimum_chunk_size, int)
        or isinstance(minimum_chunk_size, bool)
    ):
        raise TypeError(
            "minimum_chunk_size must be an integer."
        )

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero."
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative."
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    if minimum_chunk_size <= 0:
        raise ValueError(
            "minimum_chunk_size must be greater than zero."
        )

    normalized_text = normalize_text(text)

    if not normalized_text:
        return []

    words = normalized_text.split()

    if not words:
        return []

    chunks: list[str] = []
    start_index = 0

    while start_index < len(words):
        current_words: list[str] = []
        current_length = 0
        index = start_index

        while index < len(words):
            word = words[index]
            added_length = len(word)

            if current_words:
                added_length += 1

            if (
                current_words
                and current_length + added_length > chunk_size
            ):
                break

            current_words.append(word)
            current_length += added_length
            index += 1

        if not current_words:
            current_words.append(
                words[start_index]
            )
            index = start_index + 1

        chunk = " ".join(current_words).strip()

        if chunk:
            chunks.append(chunk)

        if index >= len(words):
            break

        overlap_words: list[str] = []
        overlap_length = 0

        for previous_word in reversed(
            current_words
        ):
            candidate_length = len(
                previous_word
            )

            if overlap_words:
                candidate_length += 1

            if (
                overlap_length + candidate_length
                > overlap
            ):
                break

            overlap_words.insert(
                0,
                previous_word,
            )
            overlap_length += candidate_length

        overlap_word_count = len(
            overlap_words
        )

        next_start_index = (
            index - overlap_word_count
        )

        if next_start_index <= start_index:
            next_start_index = index

        start_index = next_start_index

    if (
        len(chunks) > 1
        and len(chunks[-1]) < minimum_chunk_size
    ):
        merged_chunk = (
            f"{chunks[-2]} {chunks[-1]}"
        ).strip()

        maximum_merged_size = (
            chunk_size + minimum_chunk_size
        )

        if len(merged_chunk) <= maximum_merged_size:
            chunks[-2] = merged_chunk
            chunks.pop()

    return chunks


def main() -> None:
    """Run local parsing and chunk-size comparison tests."""

    sample_path = Path(
        "data/sample.txt"
    )

    if not sample_path.exists():
        print(
            f"Sample file not found: {sample_path}"
        )
        return

    document_text = read_document(
        sample_path
    )

    test_sizes = [
        300,
        600,
        900,
    ]

    print("=" * 70)
    print("Chunk Size Comparison")
    print("=" * 70)
    print(f"Document: {sample_path}")
    print(
        "Document Character Count: "
        f"{len(document_text)}"
    )

    for size in test_sizes:
        chunks = chunk_text(
            document_text,
            chunk_size=size,
            overlap=80,
            minimum_chunk_size=50,
        )

        average_length = (
            sum(
                len(chunk)
                for chunk in chunks
            )
            / len(chunks)
            if chunks
            else 0
        )

        print()
        print(f"Chunk Size: {size}")
        print(
            f"Chunk Count: {len(chunks)}"
        )
        print(
            "Average Chunk Length: "
            f"{average_length:.1f}"
        )

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):
            print()
            print(f"Chunk {index}")
            print("-" * 70)
            print(chunk)
            print(
                f"Characters: {len(chunk)}"
            )
            print("-" * 70)


if __name__ == "__main__":
    main()