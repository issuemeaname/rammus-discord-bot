from collections import namedtuple

import aiohttp


class DatamuseAPI:
    Result = namedtuple("Result", ["word", "score"])

    def __init__(self):
        self.root = r"https://api.datamuse.com/words"

    async def get_synonyms(self, word):
        synonyms = []
        json = None
        params = {
            "rel_syn": word
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.root, params=params) as response:
                json = await response.json()

        for entry in json:
            synonym = entry.get("word")
            synonyms.append(synonym)

        return synonyms and sorted(synonyms) or None


Datamuse = DatamuseAPI()
