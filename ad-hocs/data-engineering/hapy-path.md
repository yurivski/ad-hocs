# Preocupações Ortogonais

Baseada nos conceitos de Engenharia de Software Aplicada, lembrar de ter uma 
hapy path na mente antes de desenvolver ou antes de entregar um pipeline.

> A robustez do código, ainda que de poucas linhas, é o que molda o caráter 
do homem.

*Tô filósofo hoje.*

<br>

## Contexto

O conceito de `lógica de programação` não é difícil de entender, qualquer macaco entende. Por exemplo, um pipeline de extração (E-TL), é basicamente: conectar -> requisitar -> armazenar *("armazenar" nesse sentido não se trata de "carga" ET-L, tudo que você extrai tem que ir pra algum lugar)*.

Tal etapa foi ridiculamente reduzida a 3 seções. No entanto, como, em nome de Lord, nós, meros júniores mortais, podemos nos certificar de que não estamos fazendo uma aberração vergonhosa no uso de uma linguagem tão flexivel e robusta como Python?

lembrai-vos do recall:

- Autenticação e segredos: de onde vêm as credenciais (env var, nunca hardcoded)
- Ciclo de vida da conexão: quem abre, quem fecha (context manager)
- Falha de rede: timeout, retry com backoff, quantas tentativas até desistir
- Resposta inesperada: status code, payload vazio, schema diferente do esperado
- Volume: cabe na memória ou preciso paginar / fazer streaming
- Rate limit: a origem me bloqueia se eu pedir rápido demais
- Estado / incremental: extraio tudo sempre ou só o que mudou, e onde guardo
- Escrita segura: se o processo morrer no meio da gravação (escrever em temp e renomear no fim)
- Idempotência: rodar duas vezes gera lixo duplicado
- Observabilidade: como eu sei depois que rodou e rodou certo (log estruturado)
- Configuração: o que é fixo no código e o que tem que ser parâmetro

Do que essa linha depende pra existir? (vai te mostrar o que vem antes)
O que pode dar errado aqui? (mostra o tratamento de erro e os edge cases)

> IA é uma megera ingrata, te prende na ilusão e te larga quando os tokens acaba.

> [!WARNING]
> Eu tô muito filósofo pqp
