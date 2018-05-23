import os
import sys
# 別ディレクトリからでもこの階層にあるモジュールを呼び出すようにするため
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .yuragi import Yuragi
from .shortened_word import SingleShortenedWord, CombinedShortenedWord
