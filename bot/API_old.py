from collections import namedtuple

import requests


class DatamuseAPI:
    Result = namedtuple("Result", ["word", "score"])

    def __init__(self):
        self.root = r"https://api.datamuse.com/words"

    def get_synonyms(self, word):
        synonyms = []
        params = {
            "rel_syn": word
        }
        request = requests.get(self.root, params=params)
        json = request.json()

        for entry in json.items():
            synonym = entry.get("word")
            synonyms.append(synonym)

        return synonyms and sorted(synonyms) or None


Datamuse = DatamuseAPI()
