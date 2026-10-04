'''Interface do Terminal'''

import shlex

from .player import MediaPlayer, PlayerError

#Classe MediaPlayerCLI
class MediaPlayerCLI:
    
    #Construtor
    def __init__(self, player=None):
        self.player = player or MediaPlayer()

    #Define a verificação de argumentos mínimos
    def _require_args(self, args, minimum, usage):
        if len(args) < minimum:
            raise PlayerError(f"sintaxe: {usage}")

    #Define a execução do comando
    def execute(self, line):
        try:
            parts = shlex.split(line)
        except ValueError as exc:
            print(f"Erro de sintaxe: {exc}")
            return True
        if not parts:
            return True
        command = parts[0].lower()
        args = parts[1:]
        try:
            if command == "library":
                self._library(args)
            elif command == "playlist":
                self._playlist(args)
            elif command == "play":
                self._no_args(args, "play")
                self.player.play()
            elif command == "next":
                self._no_args(args, "next")
                self.player.next()
            elif command == "prev":
                self._no_args(args, "prev")
                self.player.prev()
            elif command == "enqueue":
                self._require_args(args, 1, "enqueue <track_id>")
                if len(args) != 1:
                    raise PlayerError("sintaxe: enqueue <track_id>")
                self.player.enqueue(args[0])
            elif command == "queue":
                self._queue(args)
            elif command == "history":
                self._no_args(args, "history")
                for line_text in self.player.history_lines():
                    print(line_text)
            elif command == "smart-shuffle":
                self._require_args(args, 1, "smart-shuffle <n>")
                if len(args) != 1:
                    raise PlayerError("sintaxe: smart-shuffle <n>")
                self.player.smart_shuffle(args[0])
                print(f"Smart shuffle criado com {len(self.player.playlist)} faixas.")
            elif command == "save":
                self._require_args(args, 1, "save <arquivo>")
                if len(args) != 1:
                    raise PlayerError("sintaxe: save <arquivo>")
                self.player.save(args[0])
                print(f"Estado salvo em: {args[0]}")
            elif command == "load":
                self._require_args(args, 1, "load <arquivo>")
                if len(args) != 1:
                    raise PlayerError("sintaxe: load <arquivo>")
                self.player.load(args[0])
                print(f"Estado carregado de: {args[0]}")
            elif command == "help":
                self._no_args(args, "help")
                self.show_help()
            elif command == "quit":
                self._no_args(args, "quit")
                return False
            else:
                print(f"Erro: comando desconhecido: {parts[0]}")
        except (PlayerError, FileNotFoundError, IndexError, ValueError) as exc:
            print(f"Erro: {exc}")
        return True

    #Define a verificação dos argumentos (nenhum ou errado)
    def _no_args(self, args, usage):
        if args:
            raise PlayerError(f"sintaxe: {usage}")

    #Define a execução do comando "library"
    def _library(self, args):
        if not args:
            raise PlayerError("sintaxe: library load <arquivo> | library list [--by rating|title|artist]")
        action = args[0].lower()
        if action == "load":
            if len(args) != 2:
                raise PlayerError("sintaxe: library load <arquivo>")
            count = self.player.load_library(args[1])
            print(f"Biblioteca carregada: {count} faixas.")
        elif action == "list":
            order = "id"
            if len(args) == 3 and args[1] == "--by":
                order = args[2]
            elif len(args) != 1:
                raise PlayerError("sintaxe: library list [--by rating|title|artist]")
            for position, track in enumerate(self.player.library_list(order), start=1):
                print(f"{position}. {track}")
        else:
            raise PlayerError("sintaxe: library load <arquivo> | library list [--by rating|title|artist]")

    #Define a execução do comando "playlist"
    def _playlist(self, args):
        if not args:
            raise PlayerError("sintaxe de playlist: new, add, remove ou show")
        action = args[0].lower()
        if action == "new":
            if len(args) != 2:
                raise PlayerError("sintaxe: playlist new <nome>")
            self.player.new_playlist(args[1])
            print(f'Playlist "{args[1]}" criada.')
        elif action == "add":
            if len(args) != 2:
                raise PlayerError("sintaxe: playlist add <track_id>")
            self.player.add_to_playlist(args[1])
        elif action == "remove":
            if len(args) != 2:
                raise PlayerError("sintaxe: playlist remove <pos>")
            self.player.remove_from_playlist(args[1])
        elif action == "show":
            self._no_args(args[1:], "playlist show")
            for line_text in self.player.playlist_lines():
                print(line_text)
        else:
            raise PlayerError("sintaxe de playlist: new, add, remove ou show")

    #Define a execução do comando "queue"
    def _queue(self, args):
        if len(args) != 1 or args[0].lower() != "show":
            raise PlayerError("sintaxe: queue show")
        for line_text in self.player.queue_lines():
            print(line_text)

    #Define a exibição da ajuda (lista de comandos disponíveis)
    def show_help(self):
        print("library load <arquivo>")
        print("library list [--by rating|title|artist]")
        print("playlist new <nome>")
        print("playlist add <track_id>")
        print("playlist remove <pos>")
        print("playlist show")
        print("play")
        print("next")
        print("prev")
        print("enqueue <track_id>")
        print("queue show")
        print("history")
        print("smart-shuffle <n>")
        print("save <arquivo>")
        print("load <arquivo>")
        print("help")
        print("quit")

    #Define a execução do loop principal do CLI
    def run(self):
        while True:
            try:
                line = input("mediap> ")
            except EOFError:
                print()
                break
            if not self.execute(line):
                break
