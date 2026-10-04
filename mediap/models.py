'''Classe que representa uma música (Track)'''

class Track:
    def __init__(self, track_id, title, artist, duration, rating, date_added):
        if not isinstance(track_id, int):
            raise ValueError("id deve ser inteiro")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title deve ser uma string não vazia")
        if not isinstance(artist, str) or not artist.strip():
            raise ValueError("artist deve ser uma string não vazia")
        if not isinstance(duration, int) or duration < 0:
            raise ValueError("duration deve ser um inteiro não negativo")
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise ValueError("rating deve ser um inteiro entre 1 e 5")
        if not isinstance(date_added, str) or not date_added.strip():
            raise ValueError("date_added deve ser uma string ISO")

        self.id = track_id
        self.title = title
        self.artist = artist
        self.duration = duration
        self.rating = rating
        self.date_added = date_added

    def __str__(self):
        return f'{self.title} — {self.artist} ({self.format_duration()})'

    def __repr__(self):
        return (
            f"Track(id={self.id!r}, title={self.title!r}, artist={self.artist!r}, "
            f"duration={self.duration!r}, rating={self.rating!r}, "
            f"date_added={self.date_added!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, Track):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def format_duration(self):
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "duration": self.duration,
            "rating": self.rating,
            "date_added": self.date_added,
        }

    @classmethod
    def from_dict(cls, data):
        required = ("id", "title", "artist", "duration", "rating", "date_added")
        for field in required:
            if field not in data:
                raise ValueError(f"campo ausente na faixa: {field}")
        try:
            track_id = int(data["id"])
            duration = int(data["duration"])
            rating = int(data["rating"])
        except (TypeError, ValueError) as exc:
            raise ValueError("id, duration e rating devem ser inteiros") from exc

        return cls(
            track_id,
            data["title"],
            data["artist"],
            duration,
            rating,
            data["date_added"],
        )
