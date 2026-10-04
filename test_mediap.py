'''Teste Unitário'''

import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from mediap.cli import MediaPlayerCLI
from mediap.doubly_linked_list import DoublyLinkedList, Playlist
from mediap.models import Track
from mediap.player import MediaPlayer, PlayerError


ROOT = Path(__file__).resolve().parent
LIBRARY_FILE = ROOT / "mediap" / "library.json"

#Define uma função auxiliar para os testes (evita a repetição destas linhas)
def make_player():
    player = MediaPlayer()
    player.load_library(str(LIBRARY_FILE))
    return player

#Define a classe de teste para a lista duplamente encadeada
class TestDoublyLinkedListBase(unittest.TestCase):
    #Define um teste para as operações básicas da lista duplamente encadeada
    def test_supplied_list_operations(self):
        lista = DoublyLinkedList()
        lista.insert(0, "a")
        lista.insert(1, "b")
        lista.insert(1, "c")
        self.assertEqual(lista.length(), 3)
        self.assertEqual(lista.index("c"), 1)
        self.assertEqual(lista.index("a"), 0)
        self.assertEqual(lista.index("b"), 2)
        self.assertEqual(lista.count("a"), 1)
        self.assertFalse(lista.empty())
        self.assertEqual(len(lista), 3)
        self.assertEqual(list(lista), ["a", "c", "b"])
        self.assertEqual(str(lista), "|a c b |" )
        lista.remove("a")
        self.assertEqual(list(lista), ["c", "b"])
        lista.append("a")
        lista.remove_all("a")
        self.assertIsNone(lista.index("a"))
        lista.replace(0, "x")
        lista.remove_at(1)
        self.assertEqual(list(lista), ["x"])
        lista.clear()
        self.assertTrue(lista.empty())

    #Define um teste para a inserção de elementos em índices específicos e para a verificação de erros
    def test_insert_index_rules_and_errors(self):
        lista = DoublyLinkedList()
        lista.append("a")
        lista.insert(100, "b")
        lista.insert(-1, "c")
        self.assertEqual(list(lista), ["a", "c", "b"])
        with self.assertRaises(IndexError):
            lista.remove_at(-1)
        with self.assertRaises(IndexError):
            lista.remove_at(3)
        with self.assertRaises(IndexError):
            lista.replace(3, "x")

#Define a classe de teste para a playlist
class TestPlaylist(unittest.TestCase):
    #Define um teste para a inserção, remoção e iteração de faixas na playlist
    def test_insert_remove_and_iteration(self):
        playlist = Playlist()
        first = Track(1, "A", "X", 60, 5, "2025-01-01")
        second = Track(2, "B", "Y", 61, 4, "2025-01-02")
        third = Track(3, "C", "Z", 62, 3, "2025-01-03")
        playlist.append(first)
        playlist.append(second)
        playlist.append(third)
        self.assertEqual([track.id for track in playlist], [1, 2, 3])
        self.assertEqual(playlist.current().id, 1)
        self.assertEqual(playlist.play_next().id, 2)
        self.assertEqual(playlist.play_prev().id, 1)
        self.assertEqual(playlist.play_next().id, 2)
        playlist.remove_at(1)
        self.assertEqual([track.id for track in playlist], [1, 3])
        self.assertEqual(playlist.current().id, 3)
        playlist.play_prev()
        playlist.remove_at(0)
        self.assertEqual([track.id for track in playlist], [3])
        self.assertEqual(playlist.current().id, 3)

    #Define um teste para verificar os limites do cursor da playlist
    def test_cursor_boundaries(self):
        playlist = Playlist()
        playlist.append("A")
        with self.assertRaises(IndexError):
            playlist.play_prev()
        with self.assertRaises(IndexError):
            playlist.play_next()
        playlist.append("B")
        self.assertEqual(playlist.play_next(), "B")
        with self.assertRaises(IndexError):
            playlist.play_next()

    #Define um teste para verificar os métodos especiais e a redefinição do cursor da playlist
    def test_dunder_methods_and_reset(self):
        playlist = Playlist()
        playlist.append("A")
        playlist.append("B")
        self.assertEqual(len(playlist), 2)
        playlist.play_next()
        self.assertEqual(playlist.current(), "B")
        playlist.reset_cursor()
        self.assertEqual(playlist.current(), "A")

#Define a classe de teste para os recursos do player
class TestPlayerFeatures(unittest.TestCase):
    #Define um teste para verificar se a fila "Up Next" tem precedência sobre a playlist
    def test_up_next_has_precedence_over_playlist(self):
        player = make_player()
        player.new_playlist("fila")
        player.add_to_playlist(1)
        player.add_to_playlist(2)
        player.add_to_playlist(3)
        player.play()
        player.enqueue(5)
        player.next()
        self.assertEqual(player.playlist.current().id, 1)
        self.assertEqual(len(player.up_next), 0)
        self.assertEqual(player.history[-1]["id"], 5)
        player.next()
        self.assertEqual(player.playlist.current().id, 2)
        self.assertEqual(player.history[-1]["id"], 2)

    #Define um teste para verificar se o histórico descarta os itens mais antigos após atingir vinte itens
    def test_history_discards_oldest_after_twenty_items(self):
        player = make_player()
        player.new_playlist("hist")
        player.add_to_playlist(1)
        player._now_timestamp = lambda: "00:00:00"
        for track_id in range(1, 11):
            for _ in range(3):
                player.history.append({"id": track_id, "timestamp": "00:00:00"})
        self.assertEqual(len(player.history), 20)
        self.assertEqual(player.history[0]["id"], 4)
        self.assertEqual(player.history[-1]["id"], 10)

    #Define um teste para verificar se a "smart_shuffle" utiliza a fórmula de prioridade corretamente
    def test_smart_shuffle_uses_priority_formula(self):
        player = MediaPlayer()
        player.library = {
            1: Track(1, "A", "X", 60, 5, "2025-01-01"),
            2: Track(2, "B", "Y", 60, 5, "2025-01-01"),
            3: Track(3, "C", "Z", 60, 4, "2025-01-01"),
            4: Track(4, "D", "W", 60, 4, "2025-01-01"),
        }
        player.history.extend([
            {"id": 1, "timestamp": "00:00:03"},
            {"id": 2, "timestamp": "00:00:02"},
        ])
        player.smart_shuffle(4)
        ids = [track.id for track in player.playlist]
        self.assertEqual(ids, [1, 2, 3, 4])

    #Define um teste para verificar se a "smart_shuffle" rejeita tamanhos inválidos
    def test_smart_shuffle_rejects_invalid_size(self):
        player = make_player()
        with self.assertRaises(PlayerError):
            player.smart_shuffle(0)
        with self.assertRaises(PlayerError):
            player.smart_shuffle(11)

    #Define um teste para verificar se o estado do player é preservado ao salvar e carregar
    def test_save_and_load_preserve_visible_state(self):
        player = make_player()
        player.new_playlist("minha")
        player.add_to_playlist(1)
        player.add_to_playlist(2)
        player.add_to_playlist(3)
        player.enqueue(5)
        player.history.append({"id": 1, "timestamp": "10:00:00"})
        player.history.append({"id": 5, "timestamp": "10:00:05"})
        player.playlist.set_cursor(1)
        expected_playlist = player.playlist_lines()
        expected_queue = player.queue_lines()
        expected_history = player.history_lines()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "estado.json")
            player.save(path)
            restored = MediaPlayer()
            restored.load(path)
            self.assertEqual(restored.playlist_lines(), expected_playlist)
            self.assertEqual(restored.queue_lines(), expected_queue)
            self.assertEqual(restored.history_lines(), expected_history)
            self.assertEqual(restored.playlist_name, "minha")

    #Define um teste para verificar se a biblioteca pode ser carregada a partir de um arquivo CSV
    def test_library_can_load_csv(self):
        csv_content = (
            "id,title,artist,duration,rating,date_added\n"
            "1,Teste,Artista,90,5,2025-01-01\n"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "library.csv")
            with open(path, "w", encoding="utf-8", newline="") as file:
                file.write(csv_content)
            player = MediaPlayer()
            self.assertEqual(player.load_library(path), 1)
            self.assertEqual(player.library[1].title, "Teste")

    #Define um teste para verificar se a exibição da faixa atual e a duração do histórico estão corretas
    def test_display_and_duration(self):
        player = make_player()
        player.new_playlist("show")
        player.add_to_playlist(1)
        output = StringIO()
        with redirect_stdout(output):
            player._now_timestamp = lambda: "12:34:56"
            player.play()
        self.assertIn('>>> Tocando: "Águas de Março" — Elis Regina (3:32)', output.getvalue())
        self.assertEqual(player.history_lines()[0], "1. Águas de Março — Elis Regina [12:34:56]")

#Define a classe de teste para a interface de linha de comando (CLI)
class TestCLI(unittest.TestCase):
    #Define um teste para verificar se os comandos desconhecidos e a ajuda funcionam corretamente
    def test_help_unknown_and_quit(self):
        cli = MediaPlayerCLI(make_player())
        output = StringIO()
        with redirect_stdout(output):
            self.assertTrue(cli.execute("unknown"))
            self.assertTrue(cli.execute("help"))
            self.assertFalse(cli.execute("quit"))
        text = output.getvalue()
        self.assertIn("comando desconhecido", text)
        self.assertIn("smart-shuffle <n>", text)

    #Define um teste para verificar se a playlist, a fila e o salvamento/carregamento funcionam corretamente na CLI
    def test_cli_playlist_queue_and_save_load(self):
        cli = MediaPlayerCLI(make_player())
        self.assertTrue(cli.execute("playlist new cli"))
        self.assertTrue(cli.execute("playlist add 1"))
        self.assertTrue(cli.execute("playlist add 2"))
        self.assertTrue(cli.execute("enqueue 5"))
        output = StringIO()
        with redirect_stdout(output):
            cli.execute("playlist show")
            cli.execute("queue show")
        text = output.getvalue()
        self.assertIn("Águas de Março", text)
        self.assertIn("Asa Branca", text)

    #Define um teste para verificar se a CLI lida corretamente com sintaxe inválida
    def test_cli_invalid_syntax(self):
        cli = MediaPlayerCLI(make_player())
        output = StringIO()
        with redirect_stdout(output):
            cli.execute("playlist")
            cli.execute("library list --by invalid")
            cli.execute("enqueue")
        text = output.getvalue()
        self.assertIn("Erro:", text)
        self.assertIn("critério inválido", text)

#Define a execução do teste unitário quando o script é executado diretamente
if __name__ == "__main__":
    unittest.main()
