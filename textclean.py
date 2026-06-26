"""Shared, deterministic text normalisation used at BOTH train and serve time.

Kept in its own module so the function reference pickled inside model.joblib
(TfidfVectorizer.preprocessor) resolves correctly wherever the model is loaded.
"""
import re

URL_RE = re.compile(r"http\S+|www\.\S+")
MENTION_RE = re.compile(r"@\w+")
WS_RE = re.compile(r"\s+")


def clean(text: str) -> str:
    text = str(text).lower()
    text = URL_RE.sub(" url ", text)
    text = MENTION_RE.sub(" user ", text)
    text = text.replace("#", " ")
    text = re.sub(r"&amp;", " and ", text)
    text = re.sub(r"[^a-z0-9'\s]", " ", text)
    text = WS_RE.sub(" ", text).strip()
    return text
