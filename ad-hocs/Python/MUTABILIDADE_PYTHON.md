<div align="center">

# Mutabilidade e Imutabilidade 

**Documento de consulta sobre gerenciamento de memória em Python:**   

referências, mutabilidade e identidade de objetos. Conceitos que o interpretador esconde, mas que aparecem em forma de bug quando ignorados. 

</div>

> [!WARNING]
> *Antes de iniciar, você precisa entender a ordem de execução do interpretador, porque existe um padrão e a ordem lógica é a mesma, havendo apenas mudanças sutis quando a sintaxe define uma classe, função ou apenas variáveis. Saber isso é fundamental pra entender como o Python faz tudo o que faz.*

### Execução de sintaxes em Python (INTRODUÇÃO)

Em Python, a ordem de execução segue um padrão lógico e previsível: primeiro, o interpretador processa as definições (como def para funções ou class para classes), criando os objetos correspondentes na memória sem executar seu corpo; em seguida, as atribuições de variáveis (como `minha_lista = [1, 2, 3]` ou `meu_numero = 42`) criam etiquetas que apontam para objetos mutáveis ou imutáveis.

Apenas no momento da chamada, seja de uma função (adicionar(minha_lista, meu_numero)), de um método de instância ou da criação de um objeto de classe, o corpo é executado, com os parâmetros sendo vinculados por referência. 

Dentro desse escopo, operações in-place como `.append()` ou `+=` (que invoca `__iadd__`) alteram o objeto original se ele for mutável (exemplo: a lista muda fora da função), enquanto operações como `+` (via `__add__`) ou reatribuições simples geram novos objetos, preservando o valor original das variáveis imutáveis. 

Essa lógica se aplica de forma genérica a funções, classes ou apenas variáveis, servindo como base para entender como o Python gerencia referências e mutabilidade sem redundância em explicações mais profundas. 

<br>

<div align="center">

# Gerenciamento de memória em Python <br> (Mão na massa) 

</div>

<div align="center">

## Ponteiros

</div>

Em Python, **ponteiros existem como referências a objetos, mas não são manipulados diretamente pelo programador**. Por exemplo: **variáveis**, em Python **são como etiquetas que apontam para objetos na memória**, funcionando como ponteiros implícitos. Objetos mutáveis, como listas, permitem alterações que afetam todas as referências; objetos imutáveis, como inteiros, criam novos objetos ao modificar.

<div align="center">

## Operadores

</div>

### == (Operador de igualdade)

O operador `==` é usado para verificar se o conteúdo/valor de dois objetos são iguais, normalmente usado pra comparar dados, como números ou strings.

```python
a = [10, 20]
b = a + [30]
c = a    

print(a == b)   # False
print(a == c)   # True
```

Referência a esse operador é o método `__eq__` (de equal). Escrever `a == b` faz o Python executar internamente algo equivalente a `a.__eq__(b)`.

Como ilustrado na sintaxe anterior, quando executamos `b = a + [30]` e comparamos `a == b`, os valores são diferentes (`a` tem `[10, 20]` e `b` tem `[10, 20, 30]`). Já `a == c` é `True` porque `c` aponta para o mesmo objeto que `a` (a etiqueta foi colada via `c = a`), então o conteúdo é exatamente o mesmo.

Importante: `==` compara **valor**, não identidade. Duas listas diferentes na memória podem ter o mesmo conteúdo:

```python
x = [1, 2, 3]
y = [1, 2, 3]   # lista diferente, mesmo conteúdo
print(x == y)   # True (conteúdo igual)
print(x is y)   # False (objetos diferentes)
```

---

### is (Operador de identidade)

O operador `is` é usado pra verificar se duas variáveis (etiquetas) estão apontadas para o mesmo objeto na memória.

```python
a = [10, 20]
b = a + [30]
c = a    

print(a is b)   # False - objetos diferentes (+ criou nova lista)
print(a is c)   # True - mesmo objeto (c = a só colou outra etiqueta)
```

Aqui mora uma armadilha que confunde muita gente: usar `is` junto com `id()`. Observe:

```python
a = [10, 20]
c = a

print(id(a) is id(c))   # False
```

Na primeira leitura, sua cabeça buga, porque "não faz sentido". `a` e `c` apontam para o mesmo objeto, então o ID deveria ser o mesmo, certo? E é. O problema é que aquela sintaxe não compara os objetos `a` e `c`, ela compara os **resultados** que a função `id()` retornou.

A função `id()` retorna um número inteiro (ex: `140015269180288`), que no CPython é o endereço de memória do objeto. Se você chamar `id(a)` cem vezes com `a` apontando pro mesmo objeto, você recebe o mesmo número cem vezes. Ela não "gera" nada novo, ela lê e devolve.

O detalhe técnico que explica o `False` é o seguinte: no CPython, inteiros pequenos (de `-5` a `256`) são cacheados, ou seja, existe um único objeto `10`, um único objeto `42`, etc. Mas inteiros grandes (como endereços de memória, que são números enormes) **não são cacheados**. Cada vez que `id()` retorna um número grande, o CPython pode criar um novo objeto inteiro pra representar aquele valor.

Então quando fazemos `id(a) is id(c)`:

- `id(a)` retorna um objeto inteiro com valor `140015269180288`.
- `id(c)` retorna outro objeto inteiro com o mesmo valor `140015269180288`.
- `is` compara: são o mesmo objeto inteiro na memória? Não, são dois objetos inteiros diferentes que por acaso representam o mesmo valor numérico.
- Resultado: `False`.

**Grave o seguinte:**

A forma correta de comparar identidade é uma das duas:
- `a is c`: compara diretamente os objetos referenciados por `a` e `c`.
- `id(a) == id(c)`: compara os valores numéricos retornados por `id()` usando `==`, que é comparação de valor.

**Regra prática:**
- Para saber se duas etiquetas apontam para o mesmo objeto: use `is`.
- Para saber se dois objetos têm conteúdo igual: use `==`.
- Nunca misture `id()` com `is`, porque você acaba comparando identidade de inteiros retornados, não identidade dos objetos originais.

> [!WARNING]
> Nunca use `is` pra comparar números ou strings, porque o Python pode criar cópias diferentes na memória para o mesmo valor (especialmente fora do range cacheado de `-5` a `256`).

O operador `is` não possui um método especial associado, ele é um operador de baixo nível que não pode ser customizado ou sobrescrito. Uma referência funcional é a função `id()`: fazer `a is b` é equivalente a `id(a) == id(b)`. Observe que aqui o operador de igualdade está fazendo a comparação entre os valores numéricos dos identificadores dos objetos.

---

### += (atribuição de adição)

O operador `+=`, conhecido como atribuição de adição, permite adicionar elementos a uma coleção já existente de forma concisa. Quando aplicado a listas (objetos mutáveis), ele modifica o objeto original in-place, sem criar uma nova lista na memória. Isso o torna equivalente ao método `.extend()` na maioria dos casos práticos. No entanto, seu comportamento muda completamente dependendo da mutabilidade do objeto à esquerda do operador: em tipos imutáveis (como int, str ou tuple), ele se transforma internamente em uma operação de criação de novo objeto.

```python
lista = [1, 2, 3]
lista += [4]          # adiciona os elementos de [4] à lista original
print(lista)          # [1, 2, 3, 4]
```
```python
lista = [1, 2, 3]
lista.extend([4])
print(lista)          # [1, 2, 3, 4]
```

O comportamento do `+=` depende totalmente da mutabilidade do tipo à esquerda:

Objetos mutáveis (ex: list): o operador modifica o objeto existente no local (in-place). A etiqueta (referência/ variável) continua apontando para o mesmo objeto na memória, apenas “esticando” seu conteúdo.
Objetos imutáveis (ex: int, str, tuple): o Python não consegue alterar o objeto. Internamente, ele executa `t = t + outro`, criando um novo objeto e recolando a etiqueta nele. O objeto original permanece intacto.

Essa diferença conceitual é a mais importante do operador e explica por que listas “mudam” enquanto números ou tuplas não.

Por baixo dos panos, `lista += [4]` é equivalente a `lista.__iadd__([4])`.
O método especial `__iadd__` (in-place add) é implementado em `C` dentro do interpretador e, para listas, tem o mesmo efeito prático do `.extend()`. Não é uma chamada literal ao método `.extend()`, mas o resultado final é idêntico: o ID do objeto não muda.

```python
# += em tupla (imutável) ID muda
t = (1, 2, 3)
print(id(t))    # 140425825893824
t += (4, 5)
print(id(t))    # 140426385388496 (DIFERENTE)
# Como tupla é imutável, o Python fez t = t + (4, 5),
# criou tupla nova e recolou a etiqueta t.
```

**Comparação rápida com outros métodos:**   
`.append()`: adiciona um único elemento (pode ser outro objeto, inclusive uma lista).
`.extend()`: adiciona vários elementos (precisa receber um iterável).

#### Comparação .extend() e .append()

```python
lst = [1, 2, 3]

lst.extend([4]) #  [1, 2, 3, 4]
lst.append(321)  #  [1, 2, 3, 4, 321]
lst.append([321]) #  [1, 2, 3, 4, 321, [321]]
lst.extend('abc') #  [1, 2, 3, 4, 321, [321], 'a', 'b', 'c']
lst.extend(123)  #  TypeError: 'int' object is not iterable
```

Cada linha modifica o `lst` resultante da operação anterior, demonstrando que `.extend()` e `.append()` mutam in-place.

#### Operador += com diferentes tipos

```python
lst = [1, 2, 3]

lst += [4] #  [1, 2, 3, 4]   (OK)
lst += ('a',) #  [1, 2, 3, 4, 'a']
lst += (1, 2) #  [1, 2, 3, 4, 'a', 1, 2]
lst += '123' #  [..., '1', '2', '3']

# Caso que falha
lst = [1, 2, 3]
lst += (4)   # TypeError: (4) é o inteiro 4, não uma tupla
             # Para tupla de um elemento, use (4,)
```

Em todos os casos válidos com listas, o id(lst) permanece o mesmo antes e depois da operação, confirmando que o objeto foi modificado in-place e não foi criado um novo.

---

### + (adição)

O operador `+` em listas é definido pelo método especial `__add__`. Por design da linguagem, ele sempre retorna um novo objeto (uma nova lista) em vez de modificar a lista original. Mesmo que a lista seja mutável, o operador `+` não realiza nenhuma alteração in-place (no lugar), ele cria uma cópia concatenada e devolve essa nova lista.

```python
lista = [1, 2, 3]
nova_lista = lista + [4, 5]   # cria uma NOVA lista
print(nova_lista)             # [1, 2, 3, 4, 5]
```

> [!NOTE]
> Diferente do `+=`, o operador `+` não depende da mutabilidade do tipo à esquerda para decidir se altera ou não o objeto. Ele foi projetado para sempre gerar um novo objeto. A lista original permanece intacta (e continua mutável, você ainda pode chamar `.append()` nela). A operação cria uma nova lista na memória com o conteúdo concatenado.

A etiqueta da variável à esquerda só é atualizada se você fizer uma reatribuição explícita `(lista = lista + [...])`. Essa escolha de design garante consistência: o operador `+` sempre significa “crie algo novo”.

Por baixo dos panos, a expressão lista + outra_lista é convertida pelo interpretador em: `lista.__add__(outra_lista)`

O método `__add__` das listas é implementado para retornar uma nova lista contendo os elementos de ambas, sem alterar nenhum dos objetos originais.

```python
original = [1, 2, 3]
print("ID original:", id(original))        # ID original: 140015398771328

nova = original + [4, 5]
print("ID nova:", id(nova))                # ID nova: 140015397875392
print("Original após + :", original)       # Original após + : [1, 2, 3]

# A original continua mutável
original.append(99)
print("Original após append:", original)   # Original após append: [1, 2, 3, 99]

# Comparação lado a lado
a = [10, 20]
b = a + [30]          # novo objeto
c = a                 # mesma referência

print(id(a))            # 140015269180288
print(id(a) == id(b))   # False
print(id(a) is id(b))   # False
print(b)                # [10, 20, 30]
print(id(a) is id(c))   # False
print(id(a) == id(c))   # True
print(c)                # [10, 20]
```

Em todos os casos, o operador `+` cria uma nova lista, preservando o objeto original.