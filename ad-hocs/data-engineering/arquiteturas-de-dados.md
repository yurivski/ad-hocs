<div align="center">

# Arquiteturas de Dados: Data Warehouse, Data Lake e Data Lakehouse

</div>

Material de estudos usado para consolidar os conceitos das arquiteturas de dados.

<br>

## Data Warehouse

<div align="center">

### O que é e quando é utilizado.

</div>

Um Data Warehouse é um repositório centralizado de dados **estruturados**, projetado especificamente para consultas analíticas e geração de relatórios. Ele não armazena dados operacionais brutos, armazena dados que já passaram por processos de extração, transformação e carga (ETL), organizados em schemas otimizados para leitura.

A ideia central é separar o ambiente analítico do ambiente operacional. Um banco de dados transacional (OLTP) como o PostgreSQL de uma aplicação em produção é otimizado para escritas rápidas, muitas transações pequenas e concorrentes, e integridade referencial. Um Data Warehouse (OLAP) é otimizado para o oposto: leituras complexas sobre grandes volumes, agregações, JOINs entre tabelas dimensionais e consultas que varrem milhões de linhas.

<div align="center">

### Características fundamentais

</div>

**Dados estruturados e com schema definido (schema-on-write):** os dados precisam ter um schema definido antes de serem carregados. Você não insere um JSON arbitrário num Data Warehouse, os tipos, as colunas e as relações são definidos previamente. Isso garante consistência, mas exige um trabalho de modelagem antes de qualquer ingestão.

**Modelagem dimensional:** a organização dos dados segue modelos como Star Schema ou Snowflake Schema. No Star Schema, uma tabela fato central (que registra eventos mensuráveis como vendas, cliques ou consultas médicas) se conecta a tabelas dimensão (que descrevem o contexto: quem, o quê, onde, quando). Essa modelagem é otimizada para queries analíticas com JOINs previsíveis e agregações rápidas.

**Dados históricos e imutáveis:** um Data Warehouse armazena o histórico. Quando o preço de um produto muda de R$ 200 para R$ 300, ambos os valores são preservados — a venda de janeiro registra R$ 200 na fato, a venda de julho registra R$ 300. Não é um UPDATE, são linhas diferentes com valores diferentes. Isso permite análises temporais e rastreabilidade completa.

**Performance de leitura:** internamente, Data Warehouses usam armazenamento colunar, em vez de armazenar dados linha por linha (como um banco OLTP), armazenam coluna por coluna. Isso é drasticamente mais eficiente para queries analíticas que tipicamente acessam poucas colunas de muitas linhas (`SELECT cidade, SUM(valor) FROM vendas GROUP BY cidade` só precisa ler duas colunas, não a linha inteira).

**Transações ACID:** Data Warehouses garantem Atomicidade, Consistência, Isolamento e Durabilidade. Uma query de leitura nunca vê dados parcialmente escritos. Uma carga que falha no meio é revertida por completo.

<div align="center">

### Limitações

</div>

**Apenas dados estruturados:** não suporta nativamente arquivos JSON aninhados, imagens, vídeos, logs semi-estruturados ou qualquer dado que não se encaixe em linhas e colunas.

**Schema rígido:** qualquer mudança na estrutura dos dados (adicionar uma coluna, mudar um tipo) exige migração. Em ambientes com dados que mudam frequentemente de formato, isso se torna um gargalo.

**Custo de storage acoplado ao compute:** em warehouses tradicionais (on-premises), o armazenamento e o processamento estão na mesma infraestrutura. Escalar storage significa escalar compute, e vice-versa. Warehouses modernos como Snowflake e BigQuery desacoplaram isso, mas o custo por GB ainda é significativamente maior que storage em Data Lake.

**ETL obrigatório antes da carga:** os dados precisam ser transformados antes de entrar. Isso significa que dados brutos são descartados ou armazenados em outro lugar. Se um erro de transformação é descoberto meses depois, não há como reprocessar a partir dos dados originais, eles não estão no Warehouse.

<div align="center">

### Exemplos de tecnologias

</div>

Amazon Redshift, Google BigQuery, Snowflake, Azure Synapse Analytics, Teradata, Oracle Exadata.

<div align="center">

### Exemplo de quando usar

</div>

Quando os dados são majoritariamente estruturados, os casos de uso são analíticos (dashboards, relatórios, KPIs), e existe uma equipe de modelagem que define os schemas. Ambientes corporativos com cultura de BI estabelecida se beneficiam de um Data Warehouse.


<br>

## Data Lake

<div align="center">

### O que é e por que ele surgiu.

</div>

Um Data Lake é um repositório centralizado que armazena dados **em qualquer formato**, estruturados, semi-estruturados e não-estruturados, no seu formato bruto original, sem exigir transformação prévia. Surgiu como resposta às limitações do Data Warehouse em lidar com o volume, a variedade e a velocidade de dados que as organizações começaram a gerar.

A ideia central é inverter a abordagem: em vez de definir o schema antes de carregar (schema-on-write), você carrega tudo primeiro e define o schema quando for consumir (schema-on-read). Isso elimina o gargalo do ETL e permite armazenar dados que ainda não têm um caso de uso definido, dados que podem se tornar valiosos no futuro.

<div align="center">

### Características fundamentais

</div>

**Schema-on-read:** os dados entram sem schema definido. Um JSON de uma API, um CSV de um sensor IoT, um arquivo de log, uma imagem de satélite, tudo é armazenado como está. O schema só é aplicado quando alguém lê os dados para uma análise específica. Isso dá flexibilidade máxima, mas transfere a responsabilidade de entender a estrutura para quem consome.

**Armazenamento de baixo custo:** o storage é tipicamente object storage distribuído (Amazon S3, Azure Blob Storage, Google Cloud Storage). O custo por GB é uma fração do custo de um Data Warehouse. Isso viabiliza armazenar tudo, inclusive dados que seriam descartados no modelo Warehouse, por anos.

**Formatos abertos:** os dados são armazenados em formatos abertos como Parquet, Avro, ORC, JSON ou CSV. Isso evita vendor lock-in, qualquer ferramenta que leia Parquet pode acessar os dados, independente de quem os armazenou.

**Suporte a qualquer tipo de dado:** texto, tabelas, imagens, vídeos, áudio, logs, streams. Não existe restrição de formato. Isso é fundamental para casos de uso como machine learning, que frequentemente trabalham com dados não-estruturados.

**Desacoplamento de storage e compute:** o armazenamento (S3, por exemplo) é independente do processamento (Spark, Presto, Athena). Você pode escalar um sem afetar o outro. Pode ter petabytes armazenados e só pagar pelo processamento quando precisar analisar.

<div align="center">

### Limitações, o "Data Swamp"

</div>

**Sem transações ACID:** operações de escrita não são atômicas. Se uma carga falha no meio, pode deixar arquivos parciais. Uma leitura pode ver dados inconsistentes, metade de um lote novo misturado com dados antigos.

**Sem schema enforcement:** qualquer coisa pode ser escrita em qualquer lugar. Sem governança rigorosa, o Data Lake se torna um pântano de dados (Data Swamp), arquivos duplicados, formatos inconsistentes, dados sem documentação, ninguém sabe o que está lá ou se é confiável.

**Sem UPDATE/DELETE eficiente:** formatos como Parquet são imutáveis. Para "atualizar" um registro, é necessário reescrever a partição inteira. Isso torna operações de compliance como LGPD (direito a exclusão de dados pessoais) extremamente custosas.

**Sem time travel nativo:** não há versionamento. Se alguém sobrescreve um arquivo, a versão anterior desapareceu. Não há como consultar "como os dados estavam ontem".

**Performance ruim para BI:** queries interativas de dashboards esperam respostas em segundos. Um Data Lake sem otimização pode levar minutos ou horas para uma query que um Warehouse faria em segundos. Isso levou muitas empresas a manter um Lake E um Warehouse em paralelo, duplicando dados, aumentando custos e criando inconsistências entre os dois ambientes.

<div align="center">

### Exemplos de tecnologias

</div>

Amazon S3 + Athena, Azure Data Lake Storage + Synapse, Google Cloud Storage + BigQuery (modo externo), Hadoop HDFS (legado).

<div align="center">

### Exemplo de quando usar

</div>

Quando o volume de dados é muito grande, os formatos são variados (estruturados + semi-estruturados + não-estruturados), ou quando o caso de uso ainda não está definido e você quer preservar os dados brutos para exploração futura. Ambientes de data science e machine learning se beneficiam do Data Lake pela flexibilidade.

<br>

## Data Lakehouse

<div align="center">

### O que é e por que ele surgiu.

</div>

O Data Lakehouse é uma arquitetura que combina o armazenamento de baixo custo e a flexibilidade do Data Lake com a confiabilidade, a performance e a governança do Data Warehouse. Surgiu para eliminar a necessidade de manter dois ambientes separados (Lake + Warehouse), que gerava duplicação de dados, inconsistência entre pipelines analíticos e de ML, e complexidade operacional.

A inovação técnica que viabilizou o Lakehouse é uma **camada de metadados transacional** que roda em cima do object storage (S3, ADLS, GCS). Essa camada, implementada por tecnologias como Delta Lake, Apache Iceberg e Apache Hudi, adiciona funcionalidades que o Data Lake puro não tinha, sem abrir mão do storage barato e dos formatos abertos.

<div align="center">

### Como funciona tecnicamente

</div>

O Lakehouse armazena os dados em formatos abertos (tipicamente Parquet) no object storage, exatamente como um Data Lake. A diferença está na camada de metadados.

No caso do Delta Lake (formato padrão do Databricks), cada tabela tem um diretório `_delta_log/` que contém arquivos JSON registrando cada operação: quais arquivos Parquet foram adicionados, quais foram removidos, qual o schema da tabela, quais checkpoints existem. Esse transaction log é o que viabiliza tudo.

<div align="center">

### O que a camada de metadados adiciona

</div>

**Transações ACID:** cada operação (INSERT, UPDATE, DELETE, MERGE) é atômica. Se uma carga falha no meio, a tabela permanece no estado anterior, os arquivos Parquet novos foram escritos, mas o transaction log não foi atualizado, então nenhum leitor os vê. Leituras e escritas são isoladas, uma query de leitura sempre vê um snapshot consistente dos dados, mesmo que uma escrita esteja acontecendo simultaneamente.

**Schema enforcement e schema evolution:** a camada de metadados registra o schema da tabela. Se alguém tenta inserir dados com tipos incompatíveis, a operação é rejeitada (enforcement). Ao mesmo tempo, mudanças controladas no schema são suportadas, adicionar uma coluna, por exemplo, sem reescrever os dados existentes (evolution). Isso resolve o problema do Data Swamp sem impor a rigidez do Warehouse.

**UPDATE, DELETE e MERGE eficientes:** diferente do Parquet puro (que é imutável), o Delta Lake permite operações de atualização e exclusão. Internamente, ele não modifica os arquivos existentes, marca os antigos como removidos no log e cria novos arquivos com os dados atualizados. Isso é copy-on-write. A operação MERGE (upsert) é particularmente importante para pipelines de dados: "se o registro já existe, atualize; se não, insira".

**Time travel (versionamento de dados):** cada operação cria uma nova versão da tabela. Você pode consultar qualquer versão anterior por número de versão ou por timestamp.

```sql
-- Por versão
SELECT * FROM minha_tabela VERSION AS OF 3;

-- Por timestamp
SELECT * FROM minha_tabela TIMESTAMP AS OF '2025-01-01';
```

Isso é essencial para auditoria ("como estavam os dados antes daquela carga?"), debug de pipelines ("qual carga introduziu esse dado corrompido?") e rollback ("reverta a tabela para a versão de ontem").

**Otimizações de performance:**

- **OPTIMIZE:** compacta arquivos Parquet pequenos em arquivos maiores, reduzindo o número de operações de I/O e melhorando a performance de leitura.
- **VACUUM:** remove arquivos Parquet antigos que não são mais referenciados pelo transaction log, liberando espaço de storage. Após um VACUUM, time travel para versões anteriores ao período de retenção não é mais possível.
- **Z-ORDER:** reorganiza os dados dentro dos arquivos para colocar valores semelhantes de uma coluna próximos fisicamente, acelerando queries com filtros nessa coluna.

<div align="center">

### Medallion Architecture (Bronze / Silver / Gold)

</div>

O padrão arquitetural mais comum em Lakehouses é a arquitetura Medallion, que organiza os dados em três camadas com níveis crescentes de qualidade e refinamento.

**Bronze (Raw):** armazena os dados exatamente como foram recebidos da fonte, JSON de APIs, CSVs de sistemas legados, dumps de bancos. Sem transformação nenhuma. A Bronze é imutável: os dados originais nunca são alterados. Isso garante que qualquer camada posterior pode ser reconstruída a partir da Bronze se algo der errado.

**Silver (Cleaned):** contém os dados limpos, validados, deduplicados e padronizados. As transformações incluem: correção de tipos de dados (strings para datas, inteiros), remoção de duplicatas, tratamento de valores nulos, padronização de nomes e formatos, e validação de regras de qualidade. A Silver é genérica, não é modelada para um caso de negócio específico. Qualquer time (analytics, data science, ML) pode consumir a Silver.

**Gold (Business):** dados modelados para casos de uso específicos do negócio. Aqui entram as tabelas fato e dimensão do Star Schema, as métricas pré-calculadas, os agregados que alimentam dashboards. A Gold é específica, cada tabela foi construída para responder perguntas concretas do negócio.

A regra fundamental: **cada camada só transforma cópias da camada anterior, nunca modifica os dados originais.** Se a Silver for corrompida, reconstrói a partir da Bronze. Se a Gold estiver errada, reconstrói a partir da Silver.

<div align="center">

### Comparação direta: Data Lake e Data Lakehouse

</div>

| Característica | Data Lake | Data Lakehouse |
|---|---|---|
| Transações ACID | Não | Sim |
| Schema enforcement | Não | Sim |
| UPDATE / DELETE | Reescreve partição inteira | Copy-on-write eficiente |
| MERGE (upsert) | Não nativo | Nativo |
| Time travel | Não | Sim (por versão ou timestamp) |
| Formato de storage | Parquet, JSON, CSV, etc | Parquet + transaction log |
| Custo de storage | Baixo (object storage) | Baixo (mesmo object storage) |
| Performance BI | Ruim sem otimização | Boa (OPTIMIZE, Z-ORDER, cache) |
| Governança | Manual | Schema enforcement + audit log |

<div align="center">

### Exemplos de tecnologias

</div>

**Camada de metadados:** Delta Lake (Databricks), Apache Iceberg (Netflix/Apple), Apache Hudi (Uber).

**Plataformas completas:** Databricks (Delta Lake nativo), Snowflake (suporte a Iceberg), AWS (Lake Formation + Iceberg/Hudi), Azure (Synapse + Delta Lake), Google (BigLake + Iceberg).

<div align="center">

### Exemplo de quando usar

</div>

O Lakehouse é a resposta padrão quando a organização precisa servir analytics (BI/dashboards) e data science (ML/experimentação) a partir da mesma base de dados, sem duplicação. É a arquitetura dominante em projetos modernos de engenharia de dados porque elimina a complexidade de manter Lake e Warehouse separados.

<br>

## Comparação Consolidada

<div align="center">

### Comparação entre as três arquiteturas.

</div>

| Característica | Data Warehouse | Data Lake | Data Lakehouse |
|---|---|---|---|
| Tipos de dados | Estruturados | Qualquer formato | Qualquer formato |
| Schema | On-write (antes de carregar) | On-read (ao consumir) | Enforcement + Evolution |
| Transações ACID | Sim | Não | Sim |
| Custo de storage | Alto | Baixo | Baixo |
| Storage + Compute | Acoplado (tradicional) | Desacoplado | Desacoplado |
| UPDATE / DELETE | Nativo | Custoso (reescreve) | Eficiente (copy-on-write) |
| Time travel | Limitado | Não | Sim |
| Performance BI | Excelente | Ruim | Boa (com otimizações) |
| Machine Learning | Limitado | Excelente | Excelente |
| Governança | Forte (schema rígido) | Fraca (Data Swamp) | Forte (enforcement + log) |
| Formato de dados | Proprietário | Aberto | Aberto |
| Pipeline dominante | ETL | ELT | ELT |

<div align="center">

### Evolução histórica

</div>

**Fase 1 — Data Warehouse (anos 90–2010):** dados estruturados, ETL pesado, relatórios corporativos. Funcionava bem para BI, mas não escalava para volume de dados moderno nem suportava dados não-estruturados.

**Fase 2 — Data Lake (2010–2018):** surgiu com o Hadoop e o big data. Armazenar tudo, barato, sem schema. Flexibilidade máxima, mas sem confiabilidade. Muitas empresas acabaram com Data Swamps e precisaram manter um Warehouse em paralelo para análises confiáveis.

**Fase 3 — Data Lakehouse (2018–presente):** camada de metadados (Delta Lake lançado em 2019 como open source pela Databricks) adicionou confiabilidade ao Data Lake, eliminando a necessidade do Warehouse separado. Storage barato + transações ACID + formatos abertos. Arquitetura dominante em projetos greenfield.

---

## Resumo

### "Por que não usar só um Data Warehouse?"

Porque Warehouses só lidam com dados estruturados, o custo de storage é alto para volumes grandes, e o schema rígido cria gargalos quando os dados mudam frequentemente de formato. Para ML e dados não-estruturados, o Warehouse não serve.

### "Por que não usar só um Data Lake?"

Porque sem ACID, sem schema enforcement e sem UPDATE/DELETE, o Data Lake não garante a confiabilidade que analytics e BI precisam. Na prática, empresas que usam só Data Lake acabam criando um Warehouse separado para consultas confiáveis — duplicando dados e aumentando complexidade.

### "O que é Delta Lake?"

É uma camada open source de armazenamento que roda sobre arquivos Parquet em object storage, adicionando transações ACID, schema enforcement, time travel, e suporte a UPDATE/DELETE/MERGE. É o formato padrão de tabelas no Databricks e o componente que transforma um Data Lake em Lakehouse.

### "Qual a diferença entre Delta Lake e Apache Iceberg?"

Ambos são camadas de metadados transacionais que transformam Data Lakes em Lakehouses. Delta Lake foi criado pela Databricks e é o padrão no ecossistema Databricks. Iceberg foi criado pela Netflix e adotado pela Apple, AWS e Snowflake. As funcionalidades são similares (ACID, time travel, schema evolution). A escolha geralmente depende do ecossistema: Databricks tende a usar Delta Lake, multi-cloud/vendor-neutral tende a usar Iceberg.

### "O que é ACID e por que importa?"

ACID é um conjunto de propriedades que garantem confiabilidade em transações de banco de dados. Atomicidade: a operação completa ou reverte por inteiro, sem estados parciais. Consistência: os dados sempre respeitam as regras definidas. Isolamento: transações concorrentes não interferem entre si. Durabilidade: dados confirmados sobrevivem a falhas. Sem ACID, um pipeline que falha no meio pode deixar dados parciais que corrompem análises downstream.

### "Me explica schema-on-write e schema-on-read."

Schema-on-write (Warehouse): o schema é definido antes da carga. Os dados são validados e rejeitados se não conformam. Vantagem: dados sempre consistentes. Desvantagem: trabalho de modelagem antes de qualquer ingestão, inflexível para dados que mudam.

Schema-on-read (Data Lake): os dados são armazenados sem schema. O schema é aplicado quando alguém lê. Vantagem: ingestão rápida e flexível. Desvantagem: sem garantia de qualidade, o consumidor precisa entender a estrutura.

O Lakehouse combina ambos: schema enforcement (rejeita dados incompatíveis), mas com schema evolution (permite mudanças controladas sem reescrever dados).