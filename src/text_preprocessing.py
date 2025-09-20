import spacy
import logging
from spacy.cli.download import download
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class TextPreProcessor:
    def __init__(
        self,
        spacy_model_lang_code: str,
        delimiting_token: str,
        sent_limit_per_chunk: int = 5,
        sent_joiner: str = "",
    ):
        try:
            self.nlp = spacy.load(spacy_model_lang_code)
        except OSError:
            print(f"Model '{spacy_model_lang_code}' not found. Downloading now...")
            download(spacy_model_lang_code)
            self.nlp = spacy.load(spacy_model_lang_code)
        self.delimiting_token = delimiting_token
        self.sent_limit_per_chunk = sent_limit_per_chunk
        self.sent_joiner = sent_joiner

    def remove_extra_chars(self, text: str):
        return text.replace("\n", "")

    def get_sections(self, text: str):
        return re.split(
            f"({re.escape(self.delimiting_token)})", self.remove_extra_chars(text)
        )

    def get_partitions(self, text: str):
        sents_in_next_chunk = []
        for sent in self.nlp(text).sents:
            sents_in_next_chunk.append(sent.text)
            if len(sents_in_next_chunk) == self.sent_limit_per_chunk:
                yield self.sent_joiner.join(sents_in_next_chunk)
                sents_in_next_chunk = []
        if len(sents_in_next_chunk) > 0:
            yield self.sent_joiner.join(sents_in_next_chunk)
