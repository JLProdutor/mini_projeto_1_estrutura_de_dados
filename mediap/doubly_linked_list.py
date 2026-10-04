'''Lista duplamente encadeada (vai e volta) com cursor para reprodução.'''

#Classe da lista duplamente encadeada
class DoublyLinkedList:
    #Classe que representa um nó da lista
    class _DoublyNode:
        #Construtor do nó
        def __init__(self, elem, prev_node, next_node):
            self._elem = elem
            self._prev = prev_node
            self._next = next_node
            
        #Representação do nó
        def __str__(self):
            if self._elem is not None:
                return str(self._elem) + ' '
            else:
                return '|'
        
        #Get e Set dos atributos do nó
        @property
        def element(self):
            return self._elem

        @element.setter
        def element(self, elem):
            self._elem = elem

        @property
        def previous(self):
            return self._prev

        @previous.setter
        def previous(self, node):
            self._prev = node

        @property
        def next(self):
            return self._next

        @next.setter
        def next(self, node):
            self._next = node
            
    #Construtor da lista
    def __init__(self, size=0):
        self._header = self._DoublyNode(None, None, None)
        self._trailer = self._DoublyNode(None, None, None)
        self._header.next = self._trailer
        self._trailer.previous = self._header
        self._length = 0
        for _ in range(size):
            self.append(None)

    #Define a utilização de len() para a lista - Tamanho
    def __len__(self):
        return self._length

    #Define a utilização de iter() para a lista - Iterador
    def __iter__(self):
        current = self._header.next
        while current is not self._trailer:
            yield current.element
            current = current.next

    #Define a inserção de elementos
    def insert(self, index, elem):
        if index >= self._length:
            index = self._length
        elif index < 0:
            index = max(self._length + index, 0)

        if self.empty():
            new_node = self._DoublyNode(elem, self._header, self._trailer)
            self._header.next = new_node
            self._trailer.previous = new_node
        elif index == 0:
            new_node = self._DoublyNode(elem, self._header, self._header.next)
            self._header.next.previous = new_node
            self._header.next = new_node
        else:
            this = self._header.next
            successor = this.next
            pos = 0
            while pos < index - 1:
                this = successor
                successor = successor.next
                pos += 1
            new_node = self._DoublyNode(elem, this, successor)
            this.next = new_node
            successor.previous = new_node

        self._length += 1

    #Define a remoção dos nós
    def remove(self, elemento):
        if not self.empty():
            node = self._header.next
            pos = 0
            found = False
            while not found and pos < self._length:
                if node.element == elemento:
                    found = True
                else:
                    node = node.next
                    pos += 1
            if found:
                node.previous.next = node.next
                node.next.previous = node.previous
                self._length -= 1

    #Define a contagem de elementos
    def count(self, elem):
        result = 0
        this = self._header.next
        while this is not self._trailer:
            if this.element == elem:
                result += 1
            this = this.next
        return result

    #Define a limpeza da lista
    def clear(self):
        self._header = self._DoublyNode(None, None, None)
        self._trailer = self._DoublyNode(None, None, None)
        self._header.next = self._trailer
        self._trailer.previous = self._header
        self._length = 0

    #Define a busca de elementos
    def index(self, elem):
        result = None
        pos = 0
        this = self._header.next
        while pos < self._length:
            if this.element == elem:
                result = pos
                break
            this = this.next
            pos += 1
        return result

    #Define a obtenção do tamanho da lista
    def length(self):
        return self._length

    #Define a verificação se a lista está vazia
    def empty(self):
        return self._length == 0

    #Define a representação da lista como string
    def __str__(self):
        result = ''
        aux = self._header
        result += aux.__str__()
        while aux is not self._trailer:
            aux = aux.next
            result += aux.__str__()
        return result

    #Define a remoção de todos os elementos iguais
    def remove_all(self, item):
        while self.index(item) is not None:
            self.remove(item)

    #Define a remoção em uma posição específica
    def remove_at(self, index):
        if index < 0 or index >= self._length:
            raise IndexError("Index out of range")
        if index == 0:
            self._header.next = self._header.next.next
            self._header.next.previous = self._header
        elif index == self._length - 1:
            self._trailer.previous = self._trailer.previous.previous
            self._trailer.previous.next = self._trailer
        else:
            aux = self._header.next
            for _ in range(index):
                aux = aux.next
            aux.previous.next = aux.next
            aux.next.previous = aux.previous
        self._length -= 1

    #Define a inserção no final da lista
    def append(self, item):
        self.insert(self._length, item)

    #Define a substituição uma posição específica
    def replace(self, index, item):
        if index < 0 or index >= self._length:
            raise IndexError("Index out of range")
        aux = self._header.next
        for _ in range(index):
            aux = aux.next
        aux.element = item

#Classe Playlist
class Playlist(DoublyLinkedList):
    def __init__(self):
        super().__init__()
        self._cursor = None

    #Define a inserção no final da lista e atualiza o cursor
    def append(self, item):
        super().append(item)
        if self._cursor is None:
            self._cursor = self._header.next

    #Define a limpeza da lista e atualiza o cursor
    def clear(self):
        super().clear()
        self._cursor = None

    #Define a remoção de todos os elementos iguais e atualiza o cursor
    def reset_cursor(self):
        if self.empty():
            self._cursor = None
        else:
            self._cursor = self._header.next

    #Define a obtenção do elemento atual do cursor
    def current(self):
        if self._cursor is None or self._cursor is self._trailer:
            return None
        return self._cursor.element

    #Define a movimentação do cursor para o próximo elemento
    def play_next(self):
        if self.empty() or self._cursor is None:
            raise IndexError("A playlist está vazia")
        if self._cursor.next is self._trailer:
            raise IndexError("Já está na última faixa da playlist")
        self._cursor = self._cursor.next
        return self._cursor.element

    #Define a movimentação do cursor para o elemento anterior
    def play_prev(self):
        if self.empty() or self._cursor is None:
            raise IndexError("A playlist está vazia")
        if self._cursor.previous is self._header:
            raise IndexError("Já está na primeira faixa da playlist")
        self._cursor = self._cursor.previous
        return self._cursor.element

    #Define a movimentação do cursor para uma posição específica
    def set_cursor(self, index):
        if self.empty():
            self._cursor = None
            return
        if index < 0 or index >= self._length:
            raise IndexError("Posição de cursor inválida")
        node = self._header.next
        for _ in range(index):
            node = node.next
        self._cursor = node

    #Define a obtenção do índice (posição) do cursor
    def cursor_index(self):
        if self._cursor is None:
            return None
        index = 0
        node = self._header.next
        while node is not self._trailer:
            if node is self._cursor:
                return index
            node = node.next
            index += 1
        return None

    #Define a remoção de um elemento em uma posição específica e atualiza o cursor
    def remove_at(self, index):
        if index < 0 or index >= self._length:
            raise IndexError("Index out of range")
        node = self._header.next
        for _ in range(index):
            node = node.next 
        if node is self._cursor:
            if node.next is not self._trailer:
                new_cursor = node.next
            elif node.previous is not self._header:
                new_cursor = node.previous
            else:
                new_cursor = None
        else:
            new_cursor = self._cursor
        node.previous.next = node.next
        node.next.previous = node.previous
        self._length -= 1
        self._cursor = new_cursor
