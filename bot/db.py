import atexit
import datetime
import json
import os


class AskDatabase:
    def __init__(self):
        self.path = r"bot/files/ask.json"

        if self.db_exists():
            self._db = dict()

            with open(self.path, "w") as f:
                json.dump(self._db, f, indent=4)
        else:
            with open(self.path, "r") as f:
                self._db = json.load(f)

    # function loads pre-init - check if db file exists
    def db_exists(self):
        return os.path.exists(self.path) is False or \
               os.path.getsize(self.path) == 0

    def save(self):
        with open(self.path, "w") as db:
            json.dump(self._db, db, indent=4)

    def _get_current_time(self):
        return datetime.datetime.now().strftime("%d %b %Y @ %I:%M %p (GMT)")

    def get_entry(self, question=None, answer=None, id=None):
        query = question or answer or str(id)
        query_type = None

        if question:
            query_type = "question"
        elif answer:
            query_type = "answer"
        else:
            query_type = "id"

        for id, entry in self._db.items():
            queried = entry.get(query_type)

            if str(queried) == query:
                return entry
        return None

    def create_entry(self, ctx, question):
        id = len(self._db)
        entry = {
            "id": id,  # backwards compatibility & integer id
            "question": question,
            "author_id": ctx.author.id,
            "created_at": self._get_current_time()
        }

        return self._db.setdefault(str(id), entry)

    def add_answer_to(self, entry, answer):
        try:
            entry.setdefault("answer", answer)
        except Exception:
            return False
        else:
            return True


Ask = AskDatabase()


@atexit.register
def save_all():
    Ask.save()

    print("Saved all databases")
