from functools import lru_cache
from .paths import QUERIES_DIR

@lru_cache(maxsize=None)
def load_sql(filename: str)-> str:
    path = QUERIES_DIR/filename
    return path.read_text(encoding='utf-8')


