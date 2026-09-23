from pathlib import Path


def parse_txt(filename: str, file_bytes: bytes) -> str:
    if Path(filename).suffix.lower() != ".txt":
        raise ValueError("only .txt files are supported")

    try:
        text = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("the text file must use UTF-8 encoding") from error

    text = text.strip()
    if not text:
        raise ValueError("the text file is empty")

    return text
