<div align="center">

# Framework para facilitar a escrita e leitura de cláusulas SQL

</div>

O framework mapeia diretamente pra ordem de execução do SQL. O SQL não executa na ordem que você escreve. Você escreve `SELECT` primeiro, mas ele executa por último. O framework segue a ordem real de execução:

```text
Ordem que você ESCREVE:     Ordem que EXECUTA:
─────────────────────────   ─────────────────────
1. SELECT                   1. FROM / JOIN
2. FROM                     2. WHERE
3. JOIN                     3. GROUP BY
4. WHERE                    4. HAVING
5. GROUP BY                 5. SELECT
6. HAVING                   6. ORDER BY
7. ORDER BY                 7. LIMIT
8. LIMIT
```

O framework segue a ordem de execução, não a de escrita. Por isso funciona como ferramenta de raciocínio, você pensa na mesma ordem que o banco processa.

## Framework de SQL (psql)

| Passo | Pergunta | Cláusula |
|-------|----------|----------|
| 1. Entidades | Quais tabelas preciso? | `FROM` |
| 2. Relacionamentos | Como se conectam? | `JOIN ... ON` |
| 3. Filtros | Quais linhas? Quais grupos? | `WHERE` (linhas) / `HAVING` (grupos) |
| 4. Agregações | Preciso agrupar? | `GROUP BY` + `COUNT`, `SUM`, `AVG` |
| 5. Ordenação | Como apresentar? | `ORDER BY` + `LIMIT` |

### Regras rápidas

- **WHERE** filtra LINHAS antes de agrupar, nunca usa função de agregação
- **HAVING** filtra GRUPOS depois de agrupar, sempre usa função de agregação
- **INNER JOIN** = dados precisam existir dos dois lados (padrão em Star Schema)
- **LEFT JOIN** = mantém lado esquerdo mesmo sem match no direito
- **SUM** soma valores / **COUNT** conta linhas, não confundir
- Datas como string: `>= '2025-01-01' AND < '2025-04-01'` (início inclusivo, fim exclusivo)

## (1) Exemplo: Cláusula simples (1 tabela, sem JOIN, sem agregação)

Listar produtos acima de R$ 500 do mais caro pro mais barato.

**Framework:**  
1. **Entidades:** dim_produto
2. **Relacionamentos:** nenhum (1 tabela)
3. **Filtros:** preco_tabela > 500
4. **Agregações:** nenhuma
5. **Ordenação:** preco_tabela DESC

```sql
SELECT nome_produto, categoria, preco_tabela
FROM dim_produto
WHERE preco_tabela > 500
ORDER BY preco_tabela DESC;
```

*Aqui o banco executa: lê dim_produto → filtra as linhas com preço > 500 → seleciona as 3 colunas → ordena*.

## (2) Exemplo: JOIN simples (2 tabelas, sem agregação)

Listar todas as vendas com nome do cliente e valor.

**Framework:** 
1. **Entidades:** fact_pedidos, dim_cliente
2. **Relacionamentos:** sk_cliente
3. **Filtros:** nenhum
4. **Agregações:** nenhuma
5. **Ordenação:** valor_total DESC

```sql
SELECT dc.nome, fp.valor_total, fp.quantidade
FROM fact_pedidos fp
INNER JOIN dim_cliente dc ON fp.sk_cliente = dc.sk_cliente
ORDER BY fp.valor_total DESC;
```

*O banco executa: combina as duas tabelas pelo sk_cliente → seleciona as colunas → ordena.*

## (3) Exemplo: JOIN + WHERE + GROUP BY (agregação com filtro de linhas)

Gasto total por cliente do Rio de Janeiro em 2025.

**Framework:**  

1. **Entidades:** fact_pedidos, dim_cliente
2. **Relacionamentos:** sk_cliente
3. **Filtros:** cidade = Rio de Janeiro AND data em 2025 (WHERE — filtra linhas)
4. **Agregações:** SUM(valor_total), GROUP BY nome
5. **Ordenação:** gasto_total DESC

```sql
SELECT 
    dc.nome,
    SUM(fp.valor_total) AS gasto_total,
    COUNT(fp.id_pedido) AS qtd_pedidos
FROM fact_pedidos fp
INNER JOIN dim_cliente dc ON fp.sk_cliente = dc.sk_cliente
WHERE dc.cidade = 'Rio de Janeiro'
    AND fp.data_pedido >= '2025-01-01'
    AND fp.data_pedido < '2026-01-01'
GROUP BY dc.nome
ORDER BY gasto_total DESC;
```

*O banco executa: JOIN → filtra Rio de Janeiro e 2025 → agrupa por nome → calcula SUM e COUNT → seleciona → ordena.*

## (4) Exemplo: WHERE + HAVING (filtro de linhas e de grupos)

Categorias com receita acima de R$ 5.000 no segundo semestre, mostrando só as que venderam mais de 3 unidades.

**Framework:**  

1. **Entidades:** fact_pedidos, dim_produto
2. **Relacionamentos:** sk_produto
3. **Filtros:** mes >= 7 (WHERE — linhas) + SUM(valor_total) > 5000 AND SUM(quantidade) > 3 (HAVING — grupos)
4. **Agregações:** SUM(valor_total), SUM(quantidade), GROUP BY categoria
5. **Ordenação:** receita DESC

*Aqui precisa de atenção. O WHERE filtra antes de agrupar (remove linhas do 1° semestre). O HAVING filtra depois de agrupar (remove categorias com pouca receita). Se você colocar SUM(valor_total) > 5000 no WHERE, o banco dá erro — porque SUM não existe antes do GROUP BY.*

## (5) Exemplo: Múltiplos JOINs + subquery

Clientes que gastaram acima da média geral, mostrando nome, cidade, gasto total e quanto acima da média estão.

**Framework:**  

1. **Entidades:** fact_pedidos, dim_cliente + subquery pra calcular a média
2. **Relacionamentos:** sk_cliente
3. **Filtros:** HAVING gasto > média (calculada na subquery)
4. **Agregações:** SUM(valor_total), GROUP BY nome e cidade
5. **Ordenação:** gasto DESC

```sql
SELECT 
    dc.nome,
    dc.cidade,
    SUM(fp.valor_total) AS gasto_total,
    SUM(fp.valor_total) - (
        SELECT AVG(sub.total_por_cliente)
        FROM (
            SELECT SUM(valor_total) AS total_por_cliente
            FROM fact_pedidos
            GROUP BY sk_cliente
        ) sub
    ) AS acima_da_media
FROM fact_pedidos fp
INNER JOIN dim_cliente dc ON fp.sk_cliente = dc.sk_cliente
GROUP BY dc.nome, dc.cidade
HAVING SUM(fp.valor_total) > (
    SELECT AVG(sub.total_por_cliente)
    FROM (
        SELECT SUM(valor_total) AS total_por_cliente
        FROM fact_pedidos
        GROUP BY sk_cliente
    ) sub
)
ORDER BY gasto_total DESC;
```

*Aqui a subquery calcula a média de gasto por cliente primeiro, e a query principal filtra quem está acima. A subquery roda independente e retorna um valor escalar que o HAVING usa como referência.*

## (6) Exemplo: Window functions (queries avançadas)

Ranking de clientes por gasto dentro de cada cidade, mostrando posição e porcentagem do gasto total da cidade.

**Framework:**  

1. **Entidades:** fact_pedidos, dim_cliente
2. **Relacionamentos:** sk_cliente
3. **Filtros:** nenhum
4. **Agregações:** SUM + window functions particionadas por cidade
5. **Ordenação:** cidade ASC, ranking ASC

```sql
SELECT 
    dc.cidade,
    dc.nome,
    SUM(fp.valor_total) AS gasto_total,
    RANK() OVER (
        PARTITION BY dc.cidade 
        ORDER BY SUM(fp.valor_total) DESC
    ) AS ranking_na_cidade,
    ROUND(
        SUM(fp.valor_total) * 100.0 / SUM(SUM(fp.valor_total)) OVER (
            PARTITION BY dc.cidade
        ), 2
    ) AS percentual_da_cidade
FROM fact_pedidos fp
INNER JOIN dim_cliente dc ON fp.sk_cliente = dc.sk_cliente
GROUP BY dc.cidade, dc.nome
ORDER BY dc.cidade, ranking_na_cidade;
```

*Window functions são um pouco mais avançado no SQL analítico. O `PARTITION BY` cria "janelas" dentro dos dados, como um `GROUP BY` que não colapsa as linhas. O `RANK()` dá uma posição dentro de cada janela. O `SUM(SUM(...)) OVER (PARTITION BY ...)` calcula o total da cidade pra derivar a porcentagem.*

### Resumo da progressão:

|Exemplo|Cláusulas|Complexidade|
|-----|---------|------------|
|1|SELECT + WHERE + ORDER BY|Uma tabela, filtro direto|
|2|+ JOIN|Duas tabelas conectadas|
|3|+ GROUP BY + funções de agregação|Agrupar e calcular
|4|+ HAVING|Filtro pós-agrupamento|
|5|+ Subqueries|Query dentro de query|
|6|+ Window functions|Cálculos por partição sem colapsar|
