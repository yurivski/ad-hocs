<div align="center">

# Chaves e Relacionamentos em Bancos de Dados

Essa documentação é uma fonte de consulta filtrada sobre Chaves e relacionamentos em Bancos de Dados.

</div>

<br>

<div align="center">

|Tema|Link|Tema|Link|
|----|----|----|----|
|**RESUMO**|[Clique aqui](#resumo)|**Identificar SK em Star Schema**|[Clique aqui](#como-identificar-surrogate-keys-num-schema-que-você-não-conhece)
|**Explicação**|[Clique aqui](#o-que-é-uma-chave)|**Chave Composta**|[Clique aqui](#composite-key-chave-composta)|
|**Primary Key (PK)**|[Clique aqui](#primary-key-pk)|**Conexão com Star Schema**|[Clique aqui](#como-tudo-se-conecta-no-star-schema)|
|**Foreign Key (FK)**|[Clique aqui](#foreign-key-fk)|**Integridade Referencial**|[Clique aqui](#integridade-referencial-na-prática)|
|**Natural key (NK)**|[Clique aqui](#natural-key-business-key)|**Slowly Changing Dimensions (SCD)**|[Clique aqui](#slowly-changing-dimensions-scd)|
|**Problemas de NK**|[Clique aqui](#por-que-natural-keys-são-problemáticas-como-pks)|**SCD tipo 1**|[Clique aqui](#scd-tipo-1-sobrescreve)|
|**Surrogate key (SK)**|[Clique aqui](#surrogate-key-sk)|**SCD tipo 2**|[Clique aqui](#scd-tipo-2-cria-nova-linha)|
|**Escolha certa para Star Schema**|[Clique aqui](#por-que-surrogate-keys-são-a-escolha-certa-em-star-schema)|**SCD tipo 3**|[Clique aqui](#scd-tipo-3-coluna-adicional)|

</div>

<br>

## O que é uma chave

Uma chave é uma coluna (ou combinação de colunas) que identifica uma linha dentro de uma tabela. Sem chaves, um banco de dados relacional é só um monte de tabelas soltas sem relação entre si. As chaves são o mecanismo que conecta tudo.

Existem vários tipos de chave, mas os que importam pra engenharia de dados no dia a dia são: Primary Key, Foreign Key, Natural Key, Surrogate Key e Composite Key. Cada uma tem um papel diferente e saber quando usar cada uma é o que separa um schema bem modelado de um que vai dar dor de cabeça no futuro.

---

## Primary Key (PK)

A Primary Key é a coluna que identifica cada linha de forma única dentro da tabela. Duas regras absolutas: nunca pode ser NULL e nunca pode se repetir. Se você tem uma tabela com 10 milhões de linhas, cada uma delas precisa ter um valor de PK diferente de todas as outras.

```sql
CREATE TABLE dim_cliente (
    sk_cliente INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);
```

Nesse exemplo, `sk_cliente` é a PK. O banco garante automaticamente que nenhuma linha terá o mesmo `sk_cliente` e que nenhuma linha terá `sk_cliente` NULL. Se você tentar inserir uma linha com um valor duplicado, o banco rejeita a operação.

Uma tabela só pode ter uma Primary Key. Pode ter múltiplas colunas com valores únicos (UNIQUE constraints), mas PK é uma só.

---

## Foreign Key (FK)

A Foreign Key é uma coluna numa tabela que referencia a Primary Key de outra tabela. É o mecanismo que cria o relacionamento entre tabelas. A FK diz: "o valor nessa coluna precisa existir como PK na outra tabela".

```sql
CREATE TABLE fact_vendas (
    id_venda INT PRIMARY KEY,
    sk_cliente INT NOT NULL,
    valor_total NUMERIC(12, 2),

    FOREIGN KEY (sk_cliente) REFERENCES dim_cliente(sk_cliente)
);
```

Aqui, `sk_cliente` na `fact_vendas` é uma FK que aponta pra `sk_cliente` na `dim_cliente`. Isso garante integridade referencial: você não consegue inserir uma venda com um `sk_cliente` que não existe na tabela de clientes. E se tentar deletar um cliente que tem vendas associadas, o banco bloqueia a operação (por padrão).

No contexto de Star Schema, a regra é simples: a tabela fato contém as FKs, as tabelas dimensão contêm as PKs. Nunca o contrário. A fato é o ponto de encontro onde todas as dimensões se conectam.

---

## Natural Key (Business Key)

Uma Natural Key é um identificador que já existe naturalmente nos dados do negócio. Não foi inventado pelo banco de dados. Já existia antes do banco ser criado. Exemplos: CPF de uma pessoa, CNPJ de uma empresa, código de produto no ERP, matrícula de um aluno, número de protocolo.

```sql
CREATE TABLE dim_cliente (
    cpf VARCHAR(11) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cidade VARCHAR(50)
);
```

Nesse exemplo, o CPF é a PK e também é uma natural key. Parece ideal, mas tem problemas sérios que aparecem com o tempo.

### Por que natural keys são problemáticas como PKs

**Podem mudar.** Um CPF pode ser corrigido (erro de digitação no cadastro). Um código de produto pode ser reformulado quando a empresa troca de ERP. Uma matrícula de aluno pode mudar quando ele transfere de unidade. Quando uma PK muda, todas as FKs que referenciam ela precisam ser atualizadas em cascata. Em tabelas fato com milhões de linhas, isso é uma operação pesada e arriscada.

**Podem ter formatos inconsistentes.** O mesmo CPF pode aparecer como "12345678901", "123.456.789-01" ou com espaços. O mesmo código de produto pode vir com zeros à esquerda num sistema e sem zeros em outro. Essas inconsistências quebram JOINs silenciosamente.

**São mais pesadas.** Um CPF como VARCHAR(11) ocupa mais bytes que um INT. Um código alfanumérico de produto como VARCHAR(20) é ainda pior. Em tabelas fato com dezenas de milhões de linhas e múltiplas FKs, cada byte a mais por FK se multiplica rapidamente. JOINs entre colunas VARCHAR são mais lentos que entre colunas INT.

**Podem não ser únicas na prática.** Um número de telefone parece único, mas duas pessoas podem compartilhar. Um email parece único, mas uma pessoa pode ter vários. Um endereço parece identificar um imóvel, mas o formato muda entre sistemas. A unicidade que parece garantida no mundo real frequentemente não é.

Isso não significa que natural keys são inúteis. Elas devem ser armazenadas como atributos na dimensão (pra referência e pra buscas), mas não devem ser a PK que sustenta os JOINs do schema.

---

## Surrogate Key (SK)

Uma Surrogate Key é um identificador artificial, gerado pelo banco de dados, sem nenhum significado de negócio. É um número sequencial (1, 2, 3...) ou um UUID cujo único propósito é identificar linhas de forma única, estável e eficiente.

```sql
CREATE TABLE dim_cliente (
    sk_cliente INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cpf VARCHAR(11) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    cidade VARCHAR(50)
);
```

Aqui, `sk_cliente` é a surrogate key (PK) e `cpf` é a natural key (armazenada como atributo). O JOIN entre fato e dimensão usa `sk_cliente`, não `cpf`.

### Por que surrogate keys são a escolha certa em Star Schema

**Imutáveis.** Uma SK nunca muda. O cliente pode trocar de CPF, mudar de nome, mudar de cidade. A SK permanece a mesma. Todas as FKs na fato que referenciam aquele cliente continuam funcionando sem nenhuma alteração.

**Leves.** Um INT ocupa 4 bytes. Um BIGINT ocupa 8 bytes. Comparado com um VARCHAR(11) de CPF (11 bytes + overhead) ou um VARCHAR(20) de código de produto (20 bytes + overhead), a diferença é significativa. Em tabelas fato com 100 milhões de linhas e 5 FKs, estamos falando de gigabytes de diferença no armazenamento e na performance de JOINs.

**Independentes do sistema de origem.** Se a empresa troca de ERP e os códigos de produto mudam, as SKs na dimensão permanecem. Você adiciona o novo código como atributo, mas o relacionamento com a fato não quebra.

**Simples de gerar.** `SERIAL`, `GENERATED ALWAYS AS IDENTITY` ou `BIGSERIAL` no PostgreSQL. O banco gera automaticamente, sem colisão, sem lógica de negócio.

**Universais.** Toda dimensão segue o mesmo padrão: SK como INT auto-increment. Isso cria consistência no schema inteiro. Quem lê o modelo sabe que qualquer coluna `sk_*` é uma surrogate key.

### Como identificar surrogate keys num schema que você não conhece

Quando você entra num projeto e vê o modelo pela primeira vez, é fácil identificar as surrogate keys. Elas são a menor coluna numérica da tabela, sempre INT ou BIGINT, sempre auto-increment, sempre PK, e não carregam nenhum significado se você olhar o valor. Se a PK é `47283`, isso não te diz nada sobre o cliente. Se a PK é `123.456.789-01`, você sabe que é um CPF. Surrogate keys são propositalmente sem significado.

---

## Composite Key (Chave Composta)

Uma Composite Key é uma PK formada por mais de uma coluna. Nenhuma das colunas individualmente é única, mas a combinação delas é.

```sql
CREATE TABLE matricula (
    aluno_id INT,
    disciplina_id INT,
    semestre VARCHAR(6),
    nota NUMERIC(4, 2),

    PRIMARY KEY (aluno_id, disciplina_id, semestre)
);
```

Aqui, um aluno pode aparecer várias vezes (em disciplinas diferentes), uma disciplina pode aparecer várias vezes (com alunos diferentes), e um semestre pode aparecer várias vezes. Mas a combinação aluno + disciplina + semestre é única: o aluno 1 só pode estar matriculado na disciplina 2 uma vez no semestre 2025.1.

Composite keys são mais comuns em tabelas de relacionamento muitos-para-muitos (tabelas associativas) e em cenários OLTP. Em Star Schema analítico, a preferência é usar surrogate key simples na fato e composite keys ficam mais restritas a tabelas de bridge (ponte) quando necessário.

---

## Como tudo se conecta no Star Schema

Num Star Schema bem modelado, o padrão é sempre o mesmo:

1. Cada tabela dimensão tem uma **surrogate key** como PK (sk_cliente, sk_produto, sk_tempo).
2. A **natural key** (cpf, codigo_produto, data) fica como atributo na dimensão, com UNIQUE constraint se necessário.
3. A tabela fato contém **uma FK pra cada dimensão**, referenciando a SK da dimensão.
4. A fato tem sua própria PK (id_venda, id_pedido), que também é uma surrogate key.
5. As **métricas** (valor_total, quantidade, desconto) ficam na fato.
6. Os **atributos descritivos** (nome, cidade, categoria) ficam nas dimensões.

```
dim_cliente              fact_vendas              dim_produto
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│ sk_cliente PK│◄───────│ sk_cliente FK│        │ sk_produto PK│
│ cpf          │        │ sk_produto FK│───────►│ codigo_erp   │
│ nome         │        │ id_venda  PK │        │ nome_produto │
│ cidade       │        │ valor_total  │        │ categoria    │
└──────────────┘        │ quantidade   │        └──────────────┘
                        │ data_venda   │
                        └──────────────┘
```

As setas mostram a direção da referência: a fato aponta pras dimensões. Nunca o contrário.

---

## Integridade referencial na prática

Integridade referencial é a garantia de que toda FK na fato tem uma PK correspondente na dimensão. Existem três cenários que violam isso e que você precisa saber tratar.

### Registro órfão

Uma venda com `sk_cliente = 999` quando não existe `sk_cliente = 999` na `dim_cliente`. Isso acontece quando dados chegam fora de ordem (a venda chega antes do cadastro do cliente) ou quando há erro na ingestão. Em bancos com FK constraint, a inserção é rejeitada. Em Data Lakes e Lakehouses (que nem sempre têm constraints), o registro entra e produz NULL nos JOINs, gerando linhas fantasma nos relatórios.

### Tratamento padrão

A solução clássica é ter uma linha padrão na dimensão pra representar "desconhecido":

```sql
INSERT INTO dim_cliente (sk_cliente, cpf, nome, cidade)
VALUES (0, 'N/A', 'Desconhecido', 'Desconhecido');
```

Toda FK que não tem correspondência aponta pra `sk_cliente = 0`. Isso evita NULLs nos JOINs e torna as linhas órfãs visíveis e rastreáveis nos relatórios.

### Exclusão em cascata vs restrição

Quando você tenta deletar um cliente que tem vendas associadas, o banco pode reagir de duas formas, configuráveis na FK:

**RESTRICT (padrão):** rejeita a exclusão. O cliente não pode ser deletado enquanto tiver vendas.

**CASCADE:** deleta o cliente e todas as vendas associadas. Perigoso em produção. Em tabelas fato com milhões de linhas, um CASCADE acidental pode destruir dados irrecuperáveis.

```sql
FOREIGN KEY (sk_cliente) REFERENCES dim_cliente(sk_cliente) ON DELETE RESTRICT
```

Em ambientes analíticos, RESTRICT é quase sempre a escolha correta. Dados históricos não devem ser deletados.

---

## Slowly Changing Dimensions (SCD)

Esse é um conceito avançado que conecta diretamente com surrogate keys. Quando um atributo da dimensão muda (cliente muda de cidade, produto muda de categoria), o que fazer?

### SCD Tipo 1: sobrescreve

Atualiza o valor antigo com o novo. O cliente morava em São Paulo, agora mora no Rio. Você faz UPDATE e pronto. Simples, mas perde o histórico. Todas as vendas antigas que usam aquela SK agora mostram Rio, mesmo as que foram feitas quando ele morava em São Paulo.

### SCD Tipo 2: cria nova linha

Em vez de atualizar, cria uma nova linha na dimensão com uma nova SK, mantendo a linha antiga. Assim, vendas antigas apontam pra SK antiga (São Paulo) e vendas novas apontam pra SK nova (Rio).

```
sk_cliente | cpf         | nome       | cidade         | valido_de  | valido_ate  | atual
1          | 12345678901 | Ana Costa  | São Paulo      | 2023-01-01 | 2025-06-30  | false
2          | 12345678901 | Ana Costa  | Rio de Janeiro | 2025-07-01 | NULL        | true
```

A mesma pessoa (mesmo CPF) tem duas surrogate keys. Cada uma representa uma "versão" da dimensão. Isso preserva o histórico completo e é o padrão em Data Warehouses e Lakehouses sérios.

É também por isso que surrogate keys existem. Se a PK fosse o CPF, você não poderia ter duas linhas com o mesmo CPF. Com surrogate key, cada versão tem seu próprio identificador.

### SCD Tipo 3: coluna adicional

Adiciona uma coluna pra guardar o valor anterior: `cidade_atual` e `cidade_anterior`. Simples, mas só guarda uma mudança. Se o cliente mudou 3 vezes de cidade, você só sabe a atual e a penúltima. Pouco usado na prática.

Para nível júnior, saber que SCD Tipo 2 existe e por que surrogate keys viabilizam ele já te diferencia. Não vão te pedir pra implementar, mas se o entrevistador mencionar "como você lidaria com mudanças de atributos na dimensão?", responder "SCD Tipo 2 com surrogate keys e colunas de validade" mostra maturidade.

---

## Resumo

**Natural Key:** identificador do mundo real (CPF, código do ERP). Armazene como atributo, não como PK. Pode mudar, pode ter formato inconsistente, é mais pesada.

**Surrogate Key:** identificador artificial (INT auto-increment). Use como PK. Imutável, leve, independente do sistema de origem.

**Primary Key:** identifica cada linha de forma única. Nunca NULL, nunca duplica. Uma por tabela.

**Foreign Key:** referencia a PK de outra tabela. Cria o relacionamento. Na Star Schema, todas as FKs ficam na fato.

**Composite Key:** PK formada por múltiplas colunas. Mais comum em OLTP e tabelas associativas.

**SCD Tipo 2:** cria nova linha na dimensão quando um atributo muda, preservando histórico. Viabilizado por surrogate keys.