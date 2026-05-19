<div align="center">

# CI/CD: Integração Contínua e Entrega Contínua

Consolidar conceitos com a prática.

</div>

<br>

<div align="center">

|Tema|Link|-|Tema|link|
|----|----|-|----|----|
|**RESUMO**|[Clique aqui!](#resumo)||||
|**O que é CI/CD**|[Clique aqui!](#o-que-é-cicd)|-|**Meu Githu Actions**|[Clique aqui!](#meu-github-actions)|
|**Exemplo em DE**|[Clique aqui!](#exemplo-na-engenharia-de-dados)|-|**Reconhecer Automações**|[Clique aqui!](#reconhecer-automações)|
|**GitHub Actions**|[Clique aqui!](#github-actions-o-motor-da-ci)|-|**Conceitos mais avançados**|[Clique aqui!](#conceitos-um-pouco-mais-avançados)|
|**CI**|[Clique aqui!](#os-passos-de-uma-ci-python-explicados-um-a-um)|-|**CD**|[Clique aqui!](#cd-continuous-delivery--deployment)|
|**Exemplos de uma CI**|[Clique aqui!](#exemplo-de-ci)|-|**Variáveis de Ambiente**|[Clique aqui!](#segredos-e-variáveis-de-ambiente)|

</div>

<br>

## O que é CI/CD

CI/CD são duas práticas complementares que automatizam o ciclo de vida do código, desde o momento que você faz um commit até o momento que o código chega em produção.

**CI (Continuous Integration)** é a prática de integrar código ao repositório principal com frequência, validando automaticamente cada integração com builds e testes. O objetivo é detectar problemas o mais cedo possível. Sem CI, um bug pode sobreviver por dias ou semanas até alguém descobrir manualmente. Com CI, o bug é detectado em minutos, no mesmo commit que o introduziu.

**CD (Continuous Delivery / Continuous Deployment)** é a extensão da CI que automatiza a entrega do código validado até o ambiente de produção. Continuous Delivery significa que o código está sempre pronto pra ser deployado (mas alguém aperta o botão manualmente). Continuous Deployment significa que o deploy acontece automaticamente assim que a CI passa (sem intervenção humana).

<br>

## Exemplo na engenharia de dados

Em engenharia de dados, o código não é só aplicação web. São pipelines de ingestão, transformações, validações, scripts de migração. Um bug num pipeline pode corromper dados silenciosamente e o efeito só aparece dias depois num dashboard errado ou num relatório inconsistente. CI previne isso ao rodar validações automáticas antes do código chegar na branch principal.

Na prática, CI num projeto de dados garante que: o código segue padrões de estilo (linting), os tipos estão corretos (type checking), as transformações produzem o resultado esperado (testes), as dependências estão consistentes (instalação limpa), e nada quebrou com a mudança que foi feita (regressão).

<br>

## GitHub Actions: o motor da CI

GitHub Actions é a plataforma de automação integrada ao GitHub. Você define workflows em arquivos YAML dentro do diretório `.github/workflows/` do repositório. Cada workflow é disparado por um evento (push, pull request, schedule) e executa uma sequência de passos num ambiente limpo (runner).

### Anatomia de um workflow

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: pytest
```

Cada parte tem uma razão de existir.

**name:** identifica o workflow nos logs e na interface do GitHub. Escolha algo descritivo.

**on:** define o trigger. `push` e `pull_request` na `main` significa que a CI roda quando alguém faz push direto na main (que idealmente não deveria acontecer) e quando alguém abre ou atualiza um PR pra main (que é o fluxo correto). Se o workflow falhar no PR, o GitHub pode bloquear o merge através de branch protection rules.

**jobs:** agrupa os passos. Cada job roda num runner independente (uma máquina virtual limpa). Múltiplos jobs podem rodar em paralelo.

**runs-on:** define o sistema operacional do runner. `ubuntu-latest` é o padrão pra projetos Python. Também existem `windows-latest` e `macos-latest`, mas custam mais minutos de execução e raramente são necessários pra data engineering.

**steps:** a sequência de comandos. Cada step é atômico. Se um step falha, os seguintes não executam (por padrão) e o workflow inteiro é marcado como falho.

<br>

## Os passos de uma CI Python, explicados um a um

### 1. Checkout do código

```yaml
- uses: actions/checkout@v4
```

Esse step conecta o runner ao repositório e baixa os arquivos da branch que disparou o evento. Sem isso, o runner é uma máquina vazia que não sabe nada sobre seu projeto. É sempre o primeiro step. O `@v4` é a versão da action. Usar versões fixas é boa prática porque garante reprodutibilidade.

### 2. Setup do Python

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
```

O runner tem alguma versão de Python pré-instalada, mas não necessariamente a que seu projeto precisa. Esse step instala a versão exata e configura o PATH. Fixar a versão é importante: se seu projeto funciona com 3.12 e o runner atualiza pra 3.13, pode quebrar por incompatibilidades. A versão aqui deve ser a mesma que você usa em desenvolvimento.

### 3. Instalação de dependências

```yaml
- run: pip install -e ".[dev]"
```

Instala o projeto em modo editável com as dependências de desenvolvimento (pytest, ruff, mypy, etc). O `.[dev]` assume que o `pyproject.toml` tem um grupo de dependências opcional chamado `dev`. Alternativas comuns: `pip install -r requirements.txt` pra projetos que usam requirements files, ou `pip install -r requirements-dev.txt` pra separar dependências de produção e desenvolvimento.

Se o projeto usa `uv` como gerenciador de pacotes (que é mais rápido que pip), o step seria:

```yaml
- run: pip install uv && uv pip install -e ".[dev]"
```

### 4. Linting

```yaml
- run: ruff check .
```

Linting verifica se o código segue padrões de estilo e identifica problemas comuns sem executar o código. É uma análise estática. Ruff é escrito em Rust e é ordens de magnitude mais rápido que flake8 (escrito em Python). Ambos fazem a mesma coisa, mas Ruff processa em milissegundos o que flake8 leva segundos.

O que linting pega: imports não utilizados, variáveis definidas mas nunca usadas, linhas muito longas, espaçamento inconsistente, padrões que indicam bugs (como comparar com `==` em vez de `is` pra None), e dezenas de outras regras configuráveis.

O que linting não pega: bugs de lógica, erros de tipo, problemas de runtime. Pra isso existem os próximos steps.

### 5. Type checking (diferencial)

```yaml
- run: mypy src/
```

Mypy verifica se os tipos anotados no código são consistentes. Se uma função declara que retorna `list[dict]` mas na verdade retorna `None` em algum caminho, mypy detecta. Esse step é especialmente relevante em projetos que usam Pydantic (como o Argus), onde os modelos de dados têm tipos explícitos.

Nem todo projeto usa mypy na CI, mas incluir mostra maturidade técnica. Numa entrevista, mencionar type checking como parte do pipeline de CI é diferencial.

### 6. Testes

```yaml
- run: pytest
```

Pytest descobre e executa automaticamente todos os arquivos que começam com `test_` ou terminam com `_test.py`. Cada função que começa com `test_` dentro desses arquivos é um caso de teste. Se algum teste falha (um assert retorna False), o step falha e o workflow inteiro é marcado como falho.

Em projetos de dados, os testes típicos validam: transformações produzem o output esperado, funções de limpeza removem duplicatas corretamente, validações rejeitam dados malformados, e parsers interpretam formatos de API corretamente.

<br>

## Exemplo de CI

No [**Anonbr**](https://github.com/yurivski/anonbr) tem um workflow de CI funcional no GitHub Actions.

O pipeline do anonbr roda em push e pull request na main. Os steps incluem checkout, setup do Python, instalação das dependências (que incluem pytest e as ferramentas de linting), verificação de estilo do código, e execução dos testes que validam as funcionalidades de detecção e mascaramento de dados pessoais (CPF, CNPJ, email, telefone).

Isso significa que se alguém (incluindo eu no futuro) abrir um PR que quebre o mascaramento de CPF, por exemplo, a CI detecta antes do merge. O dado sensível nunca escapa pra main com uma regex quebrada.

### Por que o Anonbr como exemplo de CI

O anonbr é um projeto de treino pessoal para para estudar dados não estruturados e estruturados, uma biblioteca/ ferramenta de proteção de dados. A CI garante que as regras de detecção e mascaramento não regridem. Num contexto de LGPD, isso é particularmente importante: se uma regex de CPF quebra e dados pessoais passam sem mascaramento, é uma violação de compliance. A CI é a primeira linha de defesa.

No meu projeto, a CI roda linting e testes de todas as funções de detecção e mascaramento de dados pessoais. Se uma regex quebra ou um novo formato de CPF não é detectado, o PR é bloqueado antes de chegar na main. Isso é crítico porque o projeto lida com dados sensíveis sob LGPD.

<br>

## Meu GitHub Actions

O workflow de métricas do meu perfil GitHub (`metrics.yml`) é um exemplo diferente de GitHub Actions. Não é CI no sentido clássico (não valida código), mas usa a mesma infraestrutura pra automação.

Esse workflow roda em schedule (cron) pra atualizar automaticamente os gráficos e estatísticas do meu perfil README. Ele usa a action `lowlighter/metrics` pra gerar as imagens de contribuição, linguagens e atividade.

A diferença conceitual é importante: CI é automação de qualidade (validar código). O workflow de métricas é automação de processo (gerar conteúdo). Ambos usam GitHub Actions, mas com propósitos diferentes. O workflow de métricas é mais um exemplo de automação com Actions, não de integração contínua.

<br>

## Reconhecer automações

Quando um repositório tem a presença de `.github/workflows/`, já comunica que o projeto tem automação. Normalmente a arquitetura é:

```
projeto/
├── .github/
│   └── workflows/
│       ├── ci.yml          # CI principal (lint + test)
│       └── release.yml     # CD ou automação de release (se aplicável)
├── src/
│   └── projeto/
│       └── ...
├── tests/
│   ├── test_deteccao.py
│   └── test_mascaramento.py
├── pyproject.toml
└── README.md
```

A separação entre `ci.yml` e outros workflows é uma boa prática. CI é o workflow que valida qualidade. Outros workflows (deploy, métricas, releases) têm triggers e responsabilidades diferentes.

<br>

## Conceitos um pouco mais avançados

### Matrix strategy

Permite rodar o mesmo workflow em múltiplas combinações de Python e sistema operacional. Útil pra bibliotecas open source que precisam funcionar em vários ambientes.

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
    os: [ubuntu-latest, windows-latest]
```

Isso gera 6 jobs (3 versões x 2 sistemas). Cada combinação roda de forma independente. Se o código funciona no Ubuntu com 3.12 mas quebra no Windows com 3.10, a matrix revela.

> Usei esse conceito na numa contribuição simples no ydata-profiling: o PR #1815 incluiu atualização da CI matrix pra corrigir a faixa de versões do Python.

### Caching de dependências

Instalar dependências a cada run consome tempo e banda. O cache salva o diretório de pacotes entre runs.

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
    cache: "pip"
```

O `cache: "pip"` faz o setup-python salvar o cache do pip automaticamente. Na primeira run, instala tudo do zero. Nas runs seguintes, usa o cache e só instala o que mudou. Isso pode reduzir o tempo de instalação de minutos pra segundos.

### Branch protection rules

No GitHub, você pode configurar regras que impedem merge na main se a CI não passar. Isso está em Settings > Branches > Branch protection rules. As opções relevantes: "Require status checks to pass before merging" (obriga CI verde) e "Require branches to be up to date before merging" (obriga que a branch esteja atualizada com a main).

Com essas regras ativas, o fluxo é: você cria uma branch, faz as mudanças, abre um PR, a CI roda automaticamente, e o botão de merge só fica verde quando todos os checks passam. Isso elimina a possibilidade de código quebrado entrar na main por descuido.

<br>

## CD: Continuous Delivery / Deployment

CD é o próximo passo depois da CI. Quando a CI passa e o código é mergeado na main, o CD automatiza o que acontece em seguida.

### Continuous Delivery

O código é automaticamente empacotado e preparado pra deploy, mas o deploy em si requer aprovação manual. Exemplo: a CI passa, o pacote é publicado num registry de staging, e alguém da equipe revisa e aprova o deploy pra produção.

### Continuous Deployment

O deploy acontece automaticamente quando a CI passa. Sem intervenção humana. Exemplo: merge na main dispara a CI, todos os testes passam, e o código é automaticamente deployado no ambiente de produção.

### CD no contexto de engenharia de dados

Em DE, CD pode significar coisas diferentes dependendo do contexto: publicar uma biblioteca atualizada no PyPI (por exemplo: como seria o caso do anonbr se eu publicasse), atualizar uma imagem Docker no registry e redeployar o container (como seria o caso das [**Tias do Zap**](https://github.com/yurivski/tias-do-zap) na AWS), atualizar notebooks ou jobs no Databricks automaticamente após merge, ou rodar migrations de schema no banco de dados.

O padrão mais simples pra começar:

```yaml
name: CD

on:
  push:
    tags:
      - "v*"

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

Esse workflow dispara quando você cria uma tag com prefixo `v` (como `v1.5.0`). Ele builda o pacote Python e publica no PyPI usando um token armazenado nos secrets do repositório. O segredo nunca aparece no código nem nos logs.

<br>

## Segredos e variáveis de ambiente

Credenciais nunca devem estar no código. O GitHub Actions tem um sistema de secrets (Settings > Secrets and variables > Actions) onde você armazena tokens, senhas e chaves de API. No workflow, acessa com `${{ secrets.NOME_DO_SECRET }}`.

```yaml
env:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

No caso, isso é relevante pras [**Tias do Zap**](https://github.com/yurivski/tias-do-zap): se um dia eu quiser automatizar o deploy na AWS via CD, as credenciais do IAM user ficariam nos secrets do GitHub, nunca no código.

<br>

## Resumo

**O que é CI:** automação de build e testes a cada commit. Detecta problemas antes de chegar na main.

**O que é CD:** automação do deploy após a CI passar. Delivery = deploy manual. Deployment = deploy automático.

**GitHub Actions:** plataforma de automação do GitHub. Workflows em YAML, disparados por eventos, executados em runners.

**Passos de uma CI Python:** checkout do código, setup do Python, instalação de dependências, linting (ruff), type checking (mypy), testes (pytest).

**Exemplo prático:** No anonbr, minha CI roda linting e testes de detecção e mascaramento de dados pessoais. Se uma regex de CPF quebra, o PR é bloqueado. Também contribuí com o ydata-profiling atualizando a CI matrix de versões do Python no PR #1815.

**Por que importa:** em engenharia de dados, um bug num pipeline pode corromper dados silenciosamente. CI é a primeira barreira de defesa.