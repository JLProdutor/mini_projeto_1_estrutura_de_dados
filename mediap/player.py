'''Núcleo do Player'''

import csv
import json
from collections import deque
from datetime import datetime
from pathlib import Path
from queue import PriorityQueue

from .doubly_linked_list import Playlist
from .models import Track


#Exceção personalizada para erros do player
class PlayerError(Exception):
    pass

#Classe MediaPlayer
class MediaPlayer:
    HISTORY_MAXLEN = 20

    #Construtor
    def __init__(self):
        self.library = {}
        self.playlist = Playlist()
        self.playlist_name = None
        self.up_next = deque()
        self.history = deque(maxlen=self.HISTORY_MAXLEN)

    #Define a verificação e obtenção de uma faixa da biblioteca
    def _track_or_error(self, track_id):
        try:
            track_id = int(track_id)
        except (TypeError, ValueError) as exc:
            raise PlayerError("track_id deve ser um inteiro") from exc
        if track_id not in self.library:
            raise PlayerError(f"faixa {track_id} não encontrada na biblioteca")
        return self.library[track_id]

    #Define o carregamento da biblioteca a partir do arquivo JSON ou CSV
    def load_library(self, filename):
        path = self._resolve_existing_path(filename)
        suffix = path.suffix.lower()
        if suffix == ".json":
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        elif suffix == ".csv":
            with path.open("r", encoding="utf-8", newline="") as file:
                data = list(csv.DictReader(file))
        else:
            raise PlayerError("a biblioteca deve estar em formato JSON ou CSV")
        if not isinstance(data, list):
            raise PlayerError("o arquivo da biblioteca deve conter uma sequência de faixas")
        new_library = {}
        for item in data:
            if isinstance(item, dict):
                track = Track.from_dict(item)
            else:
                raise PlayerError("formato inválido para uma faixa")
            if track.id in new_library:
                raise PlayerError(f"id de faixa duplicado: {track.id}")
            new_library[track.id] = track
        self.library = new_library
        return len(self.library)

    #Define a resolução do caminho de um arquivo existente
    def _resolve_existing_path(self, filename):
        path = Path(filename)
        candidates = (path, Path("mediap") / path, Path("library") / path)
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        raise FileNotFoundError(f"arquivo não encontrado: {filename}")

    #Define a obtenção da lista de faixas da biblioteca ordenadas
    def library_list(self, order="id"):
        if order not in ("id", "rating", "title", "artist"):
            raise PlayerError("critério inválido; use id, rating, title ou artist")
        if order == "rating":
            key = lambda track: (-track.rating, track.id)
        elif order == "title":
            key = lambda track: (track.title.casefold(), track.id)
        elif order == "artist":
            key = lambda track: (track.artist.casefold(), track.id)
        else:
            key = lambda track: track.id
        return sorted(self.library.values(), key=key)

    #Define a criação de uma nova playlist
    def new_playlist(self, name):
        name = str(name).strip()
        if not name:
            raise PlayerError("o nome da playlist não pode ser vazio")
        self.playlist = Playlist()
        self.playlist_name = name

    #Define a adição de uma faixa à playlist
    def add_to_playlist(self, track_id):
        track = self._track_or_error(track_id)
        self.playlist.append(track)

    #Define a remoção de uma faixa da playlist em uma posição específica
    def remove_from_playlist(self, position):
        try:
            position = int(position)
        except (TypeError, ValueError) as exc:
            raise PlayerError("pos deve ser um inteiro") from exc
        self.playlist.remove_at(position)

    #Define a adição de uma faixa à fila "Up Next"
    def enqueue(self, track_id):
        track = self._track_or_error(track_id)
        self.up_next.append(track)

    #Define a obtenção da hora atual
    def _now_timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    #Define a reprodução de uma faixa
    def _play_track(self, track):
        print(f'>>> Tocando: "{track.title}" — {track.artist} ({track.format_duration()})')
        self.history.append({"id": track.id, "timestamp": self._now_timestamp()})
        return track

    #Define a reprodução da faixa atual da playlist
    def play(self):
        track = self.playlist.current()
        if track is None:
            raise PlayerError("não há faixa para tocar na playlist atual")
        return self._play_track(track)

    #Define a reprodução da próxima faixa, considerando a fila "Up Next" e a playlist
    def next(self):
        if self.up_next:
            track = self.up_next.popleft()
            return self._play_track(track)
        try:
            track = self.playlist.play_next()
        except IndexError as exc:
            raise PlayerError(str(exc)) from exc
        return self._play_track(track)

    #Define a reprodução da faixa anterior da playlist
    def prev(self):
        try:
            track = self.playlist.play_prev()
        except IndexError as exc:
            raise PlayerError(str(exc)) from exc
        return self._play_track(track)

    #Define a obtenção das posições das faixas no histórico
    def _history_positions(self):
        positions = {}
        for position, item in enumerate(reversed(self.history)):
            track_id = item["id"]
            if track_id not in positions:
                positions[track_id] = position
        return positions

    #Define a prioridade de uma faixa para o "Smart Shuffle"
    def _shuffle_priority(self, track, history_positions):
        poshist = history_positions.get(track.id)
        if poshist is not None and poshist < 5:
            penalty = 5 - poshist
        else:
            penalty = 0
        return -10 * track.rating + penalty

    #Define a criação de uma nova playlist com base no "Smart Shuffle"
    def smart_shuffle(self, n):
        try:
            n = int(n)
        except (TypeError, ValueError) as exc:
            raise PlayerError("n deve ser um inteiro") from exc
        if n <= 0:
            raise PlayerError("n deve ser maior que zero")
        if n > len(self.library):
            raise PlayerError("n não pode ser maior que o número de faixas da biblioteca")
        history_positions = self._history_positions()
        priority_queue = PriorityQueue()
        for track in self.library.values():
            priority = self._shuffle_priority(track, history_positions)
            priority_queue.put((priority, track.id, track))
        new_playlist = Playlist()
        for _ in range(n):
            _, _, track = priority_queue.get()
            new_playlist.append(track)
        self.playlist = new_playlist
        self.playlist_name = "smart-shuffle"
        return self.playlist

    #Define a obtenção das linhas de exibição da playlist
    def playlist_lines(self):
        lines = []
        cursor = self.playlist.cursor_index()
        for position, track in enumerate(self.playlist, start=1):
            marker = ">" if position - 1 == cursor else " "
            lines.append(f"{marker} {position}. {track}")
        return lines

    #Define a obtenção das linhas de exibição da fila "Up Next"
    def queue_lines(self):
        return [f"{position}. {track}" for position, track in enumerate(self.up_next, start=1)]

    #Define a obtenção das linhas de exibição do histórico
    def history_lines(self):
        lines = []
        for position, item in enumerate(reversed(self.history), start=1):
            track = self.library.get(item["id"])
            if track is None:
                description = f"Faixa {item['id']}"
            else:
                description = f"{track.title} — {track.artist}"
            lines.append(f"{position}. {description} [{item['timestamp']}]")
        return lines

    #Define o salvamento do estado do player
    def save(self, filename):
        state = {
            "library": [track.to_dict() for track in self.library.values()],
            "playlist": {
                "name": self.playlist_name,
                "tracks": [track.id for track in self.playlist],
                "cursor": self.playlist.cursor_index(),
            },
            "up_next": [track.id for track in self.up_next],
            "history": list(self.history),
        }
        path = Path(filename)
        with path.open("w", encoding="utf-8") as file:
            json.dump(state, file, ensure_ascii=False, indent=2)

    #Define o carregamento do estado do player
    def load(self, filename):
        path = Path(filename)
        if not path.is_file():
            raise FileNotFoundError(f"arquivo não encontrado: {filename}")
        with path.open("r", encoding="utf-8") as file:
            state = json.load(file)
        if not isinstance(state, dict):
            raise PlayerError("estado salvo inválido")
        if "playlist" not in state or "up_next" not in state or "history" not in state:
            raise PlayerError("estado salvo incompleto")
        if "library" in state:
            new_library = {}
            for item in state["library"]:
                track = Track.from_dict(item)
                new_library[track.id] = track
            self.library = new_library
        playlist_data = state["playlist"]
        playlist = Playlist()
        try:
            for track_id in playlist_data.get("tracks", []):
                playlist.append(self._track_or_error(track_id))
            cursor = playlist_data.get("cursor")
            if cursor is None and len(playlist) > 0:
                playlist.reset_cursor()
            elif cursor is not None:
                playlist.set_cursor(int(cursor))
        except (TypeError, ValueError, IndexError) as exc:
            raise PlayerError(f"playlist salva inválida: {exc}") from exc
        try:
            new_queue = deque()
            for track_id in state["up_next"]:
                new_queue.append(self._track_or_error(track_id))
        except (TypeError, ValueError) as exc:
            raise PlayerError(f"fila Up Next inválida: {exc}") from exc
        new_history = deque(maxlen=self.HISTORY_MAXLEN)
        for item in state["history"]:
            if not isinstance(item, dict) or "id" not in item or "timestamp" not in item:
                raise PlayerError("item inválido no histórico salvo")
            if item["id"] not in self.library:
                raise PlayerError(f"faixa {item['id']} do histórico não está na biblioteca")
            new_history.append({"id": int(item["id"]), "timestamp": str(item["timestamp"])})
        self.playlist = playlist
        self.playlist_name = playlist_data.get("name")
        self.up_next = new_queue
        self.history = new_history
