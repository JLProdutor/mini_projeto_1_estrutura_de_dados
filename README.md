# Mini Projeto 1 - "Media Player"
Implementação em Python do sequenciador/reprodutor de mídia.

## Informações do Trabalho
Aluno: João Lucas Lima Alexandre

Curso: Sistemas e Mídias Digitais - Diurno (UFC)

Professor: Ernesto Trajano

Matéria: Estrutura de Dados

## Como executar?
### Apenas uma simulação no Terminal. NÃO HÁ REPRODUÇÃO DE ÁUDIO REAL.

Na raiz do projeto, execute:

```text
python -m mediap
```

No prompt `mediap>`, carregue a biblioteca de exemplo:

```text
library load mediap/library.json
```

Também é possível carregar arquivos JSON ou CSV que tenham os campos `id`, `title`, `artist`, `duration`, `rating` e `date_added`.

Para executar os testes:

```text
python -m unittest discover -v
```

## Estruturas de dados utilizadas:

A Playlist é uma lista duplamente encadeada própria. 

O "Cursor" é um nó da própria lista; por isso `next` e `prev` apenas deslocam a referência para o nó seguinte/anterior e têm custo O(1).

A fila "Up Next" usa `collections.deque`, com `append` no final e `popleft` no início, respeitando o comportamento de uma fila.

O histórico usa outro `deque`, com `maxlen=20`. A inserção ocorre no final e, ao atingir a capacidade, o item mais antigo é descartado automaticamente.

O smart-shuffle usa efetivamente `queue.PriorityQueue`: todas as faixas da biblioteca entram na fila com sua chave de prioridade e as faixas selecionadas saem com `get()`.

## Fórmula do "Smart Shuffle" (Embaralho Inteligente):

Foi adotada a fórmula proposta:

```text
chave(f) = -10 * rating(f) + penalty_rec(f)
```

Para a posição `poshist(f)` no histórico, com `0` para a faixa mais recentemente tocada:

```text
penalty_rec(f) = { 5 - poshist(f), se poshist(f) < 5
                   0,             se poshist(f) >= 5
```

O termo negativo do rating é necessário porque `PriorityQueue` retorna primeiro o menor valor.

Em caso de empate completo da prioridade, o `id` da faixa é usado apenas como critério determinístico de desempate.

## Exemplo de sessão:

```text
mediap> library load mediap/library.json
Biblioteca carregada: 10 faixas.
mediap> playlist new minha
Playlist "minha" criada.
mediap> playlist add 1
mediap> playlist add 2
mediap> playlist add 3
mediap> playlist show
> 1. Águas de Março — Elis Regina (3:32)
  2. Construção — Chico Buarque (6:21)
  3. Carinhoso — Pixinguinha (3:05)
mediap> play
>>> Tocando: "Águas de Março" — Elis Regina (3:32)
mediap> enqueue 5
mediap> next
>>> Tocando: "Asa Branca" — Luiz Gonzaga (2:45)
mediap> next
>>> Tocando: "Construção" — Chico Buarque (6:21)
mediap> history
1. Construção — Chico Buarque [11:42:17]
2. Asa Branca — Luiz Gonzaga [11:42:08]
3. Águas de Março — Elis Regina [11:42:00]
mediap> quit
```

## Organização

```text
mediap/
├── __init__.py
├── __main__.py
├── models.py
├── doubly_linked_list.py
├── player.py
├── cli.py
├── main.py
└── library.json
README.md
test_mediap.py
```
