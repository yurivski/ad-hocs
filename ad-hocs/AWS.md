<div align="center">

## AD-HOC <br><br> ADAPTAR PROJETOS AO AWS FREE TIER 

</div>

Este documento é um quebra galho para adaptar o seu projeto para o AWS Free Tier, permitindo estudo e prática com custo zero durante até 6 meses (plano Free) ou 12 meses de créditos (plano Paid). O plano cobre: criação da conta com proteção contra cobranças, deploy seguro em EC2, e integração com S3 para backup, tudo dentro dos limites gratuitos.

> [!IMPORTANT]
> Esse documento exemplifica o deploy de um Lakehouse adaptado para aproveitar o máximo do **plano free com t3.micro**, desde a criação da conta ao deploy com Docker com segurança.

<br>

## Glossário Complementar (importante)

**EC2 (Elastic Compute Cloud):** Servidor virtual na nuvem da AWS. É como alugar um computador que roda num datacenter da Amazon. Você escolhe o tamanho (tipo de instância), o sistema operacional, e paga por hora de uso.
 
**t3.micro:** O menor tipo de instância EC2 disponível no Free Tier. Tem 2 vCPU e 1 GiB de RAM. Os 2 vCPUs são "burstáveis", funcionam em capacidade baixa na maior parte do tempo, mas podem "estourar" para performance total por períodos curtos. Imagine um Gol quadrado turbinado com escada no teto, funciona normal no dia a dia, mas tem um boost quando você precisa ultrapassar os lamborghinis.
 
**AMI (Amazon Machine Image):** Template pré-configurado para criar uma instância EC2. É como um print do disco rígido de um computador já configurado. Você escolhe uma AMI (com Ubuntu 24.04) e a instância nasce com o SO já instalado.
 
**Security Group:** Firewall virtual da AWS que controla o tráfego de entrada e saída de uma instância EC2. Funciona como o `ufw` de uma VPS, mas é configurado no painel da AWS em vez de dentro do servidor. A diferença é que o Security Group opera no nível da rede (antes do tráfego chegar ao servidor), enquanto `ufw` opera dentro do servidor.
 
**EBS (Elastic Block Store):** Disco virtual da instância EC2. É o "HD" do servidor. O Free Tier dá 30GB de armazenamento EBS. Importante: EBS continua existindo (e cobrando) mesmo se você desligar a instância, a menos que você explicitamente delete o volume.
 
**S3 (Simple Storage Service):** Armazenamento de objetos (arquivos). Diferente de um disco (EBS), o S3 funciona como um repositório de arquivos acessível via URL/API. Free Tier dá 5GB. Pensa num Google Drive, mas acessível via código.
 
**Elastic IP:** Endereço IP público fixo que você pode associar a uma instância EC2. Gratuito enquanto está anexado a uma instância rodando. Se a instância estiver parada ou o IP estiver desanexado, a AWS cobra. É como um número do seu telefone fixo antigo que você nunca usa, gratuito enquanto a linha está ativa, mas cobrado se você reservar o número sem usar.
 
**IAM (Identity and Access Management):** Sistema de permissões da AWS. Define quem pode fazer o quê. O famoso cara crachá, cada pessoa (ou programa) recebe um crachá com permissões específicas. O root tem acesso a tudo; um usuário IAM tem acesso apenas ao que você definir.
 
**Região (Region):** Localização física dos datacenters da AWS. Você escolhe o estado, São Paulo, Acre, Casa da mãe Joana, alguns estados do Tio Sam ou dos tomadores de Chás. Importante: o Free Tier é global, 750 horas compartilhadas entre TODAS as regiões. Se você rodar uma instância em São Paulo e outra na Virgínia (por exemplo), as duas consomem do mesmo limite.
 
**Budget / Billing Alarm:** Ferramentas para monitorar gastos. Um Budget te avisa quando os gastos atingem um valor definido por você. É como configurar um alerta no banco, "me avise se gastar mais de R$0, porque eu tõ desempregado e tô raspando o toba com a unha."

<br>

## Limites do Free Tier
 
### Contas criadas após 15 de julho de 2025
 
| Recurso | Limite Gratuito | Obs. |
|---------|----------------|------|
| Créditos iniciais | US$100 no cadastro | Automático |
| Créditos adicionais | Até US$100 (completando atividades) | Configurar Budget, usar EC2, etc. |
| Plano Free | 6 meses | Conta fecha automaticamente após |
| Plano Paid | Créditos duram 12 meses | Cobra se exceder créditos |
| EC2 t3.micro | 750 horas/mês | = 1 instância 24/7 por 31 dias |
| EBS | 30 GB total | Todos os volumes somados |
| S3 | 5 GB + 20.000 GETs + 2.000 PUTs/mês | Always Free |
| Data Transfer Out | 100 GB/mês | Always Free |
| Lambda | 1M requests + 400K GB-s/mês | Always Free |
| CloudWatch | 10 métricas + 10 alarmes | Always Free |

<br>

### Exemplo de uso para rodar um projeto no 0800
 
| Necessidade | Free Tier | Obs. |
|---------------------|-----------|--------|
| Servidor para rodar pipeline | EC2 t3.micro (2 vCPU, 1 GiB RAM) | Suficiente para pipeline batch |
| Armazenamento de dados | 30 GB EBS | Suficiente (DuckDB + dados) |
| Backup offsite | 5 GB S3 | Suficiente para backups comprimidos |
| Monitoramento | 10 alarmes CloudWatch | Suficiente |
| Tráfego de rede | 100 GB/mês | Muito mais que suficiente |
 
**Limitação real:** 1 GiB de RAM é apertado. Um projeto com Python + DuckDB funciona, mas sem espaço pra Uptime Kuma ou outros serviços simultâneos. Docker também consome memória. Se for usar Docker, usa um Docker leve, um container por vez, swap como segurança, senão vamos ter que usar o cheque especial do banco.

<br>

<div align="center">

## **MÃO NA MASSA** <br> (Antes de tudo)

</div>

> [!warning]
> **Objetivo:** garantir que você não será cobrado por nada. Se der mole aqui, prepara o cheque especial no banco.
 
<div align="center">

### Criando a conta

</div>

Na criação da conta, a AWS pergunta qual plano você quer:
 
**Free Plan:**
- Duração: 6 meses (ou até acabar os créditos)
- Sem cobrança: a conta fecha automaticamente no fim
- Limitação: não acessa todos os serviços (mas EC2, S3, CloudWatch estão disponíveis)
- Segurança financeira: você não vai ser cobrado
 
**Paid Plan:**
- Duração: créditos duram 12 meses
- Cobrança: cobra automaticamente se exceder créditos
- Acesso: todos os serviços
- Risco: se não monitorar, pode gerar custo
 
### Criar a Conta AWS
 
1. Acesse https://aws.amazon.com/free
2. Clique em "Create an AWS Account"
3. Use um email somente pra estudos (não o pessoal principal)
4. Escolha **Free Plan**
5. Forneça cartão de crédito (calma xovem, é obrigatório para verificação, não será cobrado no Free Plan)
6. Complete a verificação por telefone

### Configurar alertas de custo (Imediatamente após login)

Essa é a primeira coisa que você vai fazer:
 
```
1. Vá em: Console → Billing and Cost Management → Budgets
2. Clique em "Create budget"
3. Selecione "Zero-spend budget"
   - Isso te avisa no momento em que QUALQUER gasto for detectado
4. Configure o email de notificação
5. Crie o budget
 
Segundo alarme (redundância, precaução né...):
1. Vá em: Console → Billing and Cost Management → Billing preferences
2. Ative "Free Tier usage alerts"
   - A AWS envia email quando você atingir 85% de qualquer limite do Free Tier
3. Configure o email
```

*Se um alerta falhar, o outro pega. O zero-spend budget é a rede de segurança mais importante, se algo gerar custo, você sabe imediatamente.*

---

### Ativar MFA no Root (Autenticação multi-fator)
 
Evite a qualquer custo ficar acessando a conta com acesso hoot, mesmo que esteja usando pra testar ou estudar, não importa. Já adiquire aqui uma boa prática de segurança.
 
```text
1. Console → IAM → Security credentials (canto superior direito → "Security credentials")
2. Na seção "Multi-factor authentication (MFA)", clique "Assign MFA device"
3. Escolha "Authenticator app"
4. Use um app pra isso, como Google Authenticator, Authy, ou Aegis (open source) ou até mesmo o gerenciador de senhas do Iphone (não sei se funciona com Android, nunca fiz)
5. Escaneie o QR code e confirme com dois códigos consecutivos
```

---

### Criar Usuário IAM para uso diário
 
Aqui você vai criar um usuário com permissões limitadas pra acessar o console ao invés de usar o usuário hoot. 
 
```text
1. Console → IAM → Users → Create user
2. Nome: gafanhoto-admin
3. Selecione "Provide user access to the AWS Management Console"
4. Crie uma senha forte
5. Attach policies directly (selecione as permissões):
   - AmazonEC2FullAccess
   - AmazonS3FullAccess
   - CloudWatchFullAccess
   - IAMReadOnlyAccess

6. Crie o usuário
7. Salve as credenciais em local seguro
8. Ative MFA neste usuário também (IAM → Users → gafanhoto-admin → Security credentials → Assign MFA. Mesma coisa do Hoot, se for usar o gerenciador de senhas do Iphone, adiciona outro "site", o MFA é individual)
```
<br>

**Resumo sobre as permissões**

**AmazonEC2FullAccess:** permite gerenciar instâncias.   
**AmazonS3FullAccess:** permite gerenciar backups.   
**CloudWatchFullAccess:** permite monitoramento.   
**IAMReadOnlyAccess:** permite visualizar (mas não modificar) permissões.   

Depois de criar o usuário, só entre novamente com ele. Se o dispositivo MFA for perdido, recuperar acesso à conta root exige suporte da AWS e deve demorar. Não perca os códigos de recuperação do MFA.


## Criar e Acessar a Instância EC2

### Escolher a Região

Se for um pipeline batch, a região não importa muito, mas dependendo do seu objetivo, pesquise sobre as regiões. Algumas possuem maior variedade de serviços, mais documentação e exemplo, outras possuem menor latência pra APIs nacionais, caso a performance de fetch for prioridade, etc. Por via das dúvidas, escolha us-east-1 (N. Virginia) ou sa-east-1 (São Paulo).

Depois de acessar o console com o novo usuário, é normal aparecer uma mensagem em vermelho, não se assuste, o widget "Applications" usa servicecatalog:ListApplications, que não está nas permissões do seu usuário. Lembre-se de conferir se a região, se tiver mudado, volte para a anterior.

## Gerar key pair

```
1. Console → EC2 → Key Pairs (menu lateral, seção Network & Security)
2. Create key pair
3. Nome: gafanhoto-key
4. Tipo: ED25519 (mais seguro que RSA)
5. Formato: .pem pra Linux ou Mac
6. O download do arquivo é automático, salve em local seguro
```

## Criar diretório para a SSH

Você provavelmente não vai ter o diretório, então copie e cole os seguntes comandos no terminal:

```
mkdir -p ~/.ssh
chmod 700 ~/.ssh
mv ~/Documents/gafanhoto-key.pem ~/.ssh/gafanhoto-key.pem
chmod 400 ~/.ssh/gafanhoto-key.pem
```

**Obs:**

`chmod 700 ~/.ssh` é uma exigência de segurança do ssh, torna a pasta privada, só você pode acessar, ler e escrever (executar)   
`chmod 400 ~/.ssh/gafanhoto-key.pem` deixa a chave extremamente restrita. O SSH recusa usar chaves privadas que tenham permissão de escrita ou que outros usuários possam ler. Essa é a permissão mais recomendada e segura pra chaves privadas. 

## Criar Security Group
O Security Group é o firewall da AWS. Você vai criar antes da instância:

```
1. Console → EC2 → Security Groups → Create security group
2. Nome: gafanhoto-sg
3. Descrição: "Firewall do Gafanhoto - SSH restrito"
4. VPC: deixe a default

Regras de Entrada (Inbound):
┌──────────┬──────────┬────────────────────┬───────────────────────────────────┐
│ Tipo     │ Porta    │ Origem             │ Justificativa                     │
├──────────┼──────────┼────────────────────┼───────────────────────────────────┤
│ SSH      │ 22       │ Meu IP             │ Acesso administrativo             │
│ HTTPS    │ 443      │ 0.0.0.0/0          │ Interface web (Caso preciso)      │
│ HTTP     │ 80       │ 0.0.0.0/0          │ Redirect para HTTPS (Caso precise)│
└──────────┴──────────┴────────────────────┴───────────────────────────────────┘

Regras de Saída (Outbound):
┌──────────┬──────────┬────────────────────┬─────────────────────────────────┐
│ Tipo     │ Porta    │ Destino            │ Justificativa                   │
├──────────┼──────────┼────────────────────┼─────────────────────────────────┤
│All Trafic│All Trafic│ 0.0.0.0/0          │ Para acessar IPs externas       │
└──────────┴──────────┴────────────────────┴─────────────────────────────────┘
```
<br>

**Clique "Create security group"**   

> [!NOTE]
> Caso não saiba, a primeira coisa a fazer em um servidor é mudar a porta padrão (22), por causa dos BOTs que tentam invadir automaticamente sem parar, mas o SSH da porta 22 na AWS é diferente de um VPS, o Security Group com "Meu IP" já restringe o acesso ao seu IP público. Você pode mudar se quiser, é uma camada extra de segurança, porém, se seu IP público mudar caso você reinicie o roteador, mude de rede, ou falte energia, ou coisas do tipo, você vai precisar atualizar p Security Group manualmente.

Se seu provedor de internet fornece IP dinâmico, use a opção "My IP" no console da AWS cada vez que for acessar, o console detecta e preenche automaticamente.

## Lançar instância EC2

Antenção aqui. Assim uma intância for lançada a cobrança de horas começa, então certifique-se de que o projeto esteja pronto. Caso esteja executando por curiosidade, lembre-se disso.

```text

1. Console → EC2 → Instances → Launch instances

2. Nome: gafanhoto-server

3. AMI: Ubuntu Server 24.04 LTS (HVM) - Free tier eligible
   - Verifique o selo "Free tier eligible" ao lado da AMI
   (Só clicar na umagem do ubuntu em: Application and OS Images (Amazon Machine Image))

4. Instance type: t3.micro
   - 2 vCPU (burstable), 1 GiB RAM
   - Verifique o selo "Free tier eligible"
   (Não precisa marcar "All generations", se marcar, isso mostra todos os tipos de instância que existem na AWS (incluindo as caras, com GPUs, centenas de GBs de RAM, etc.). Com ele desmarcado, o filtro já te entregou o t3.micro Free tier eligible)

5. Key pair: gafanhoto-key (a que você criou no passo anteriormente)
    - Clica na lista e seleciona

6. Network settings:
    - Seleciona "Select existing security group" para selecionar o que já foi criado (gafanhoto-sg)

7. Configure storage, edita e põe:
   - 20 GiB gp3 (General Purpose SSD), deixar 10 de  margem pra snapshots e outros volumes (os 30GB do Free Tier são compartilhados entre TODOS os volumes)
   - Desmarque "Delete on termination" APENAS se quiser manter dados, recomendação: marque YES, se deixar NO, quando você terminar a instância o volume EBS continua existindo e consumindo os 20GB do seu Free Tier, vai gastar dinheiro que não tem (porque nois é pobre).

8. Advanced details (expandir):
   - Não precisa mexer em nada

9. Launch instance
```

### Primeiro Acesso

```bash
# Aguarde até receber o sinal verde, pode demorar ou ser rápido.
# Conectar via SSH (substitua o IP público da instância)
ssh -i ~/.ssh/gafanhoto-key.pem ubuntu@IP_PUBLICO_DA_INSTANCIA (Public IPv4 address)

# O usuário padrão do Ubuntu na AWS é 'ubuntu', não 'root', ele já tem sudo configurado
```

> [!NOTE]
> Se seu IP local mudar, você precisa lembrar de voltar no Security Groups do EC2 e Edit inbound rules. Ao lado do IP, clica na lista e seleciona "My IP" pra ele reconhecer seu novo IP local.   
> Se você executar `ssh -i ~/.ssh/gafanhoto-key.pem ubuntu@Public_IPv4_address` e aparecer no terminal `ssh: connect to host Public_IPv4_address port 22: Connection timed out`, já sabe que precisa atualizar o IP no security group.

<br>

## Hardening do Sistema (Dentro do EC2)

O hardening dentro do servidor.

### Atualizar o sistema, execute no terminal:

```
sudo apt update && sudo apt upgrade -y
```

### Criar usuário dedicado

```bash
# Criar usuário, ao executar irá pedir pra registrar uma senha, após isso, exibirá "Enter the new value, or press ENTER for the default", pode só dar Enter:
sudo adduser seu_nome
```

O output será:

```
 Changing the user information for seu_nome
 Enter the new value, or press ENTER for the default
	Full Name []: 
	Room Number []: 
	Work Phone []: 
	Home Phone []: 
	Other []: 
 Is the information correct? [Y/n] Y
 info: Adding new user `seu_nome' to supplemental / extra groups `users' ...
 info: Adding user `seu_nome' to group `users' ...
```
Em seguida:

```bash
sudo usermod -aG sudo seu_nome

# Copiar a chave SSH do ubuntu para o novo usuário
sudo mkdir -p /home/seu_nome/.ssh
sudo cp /home/ubuntu/.ssh/authorized_keys /home/seu_nome/.ssh/
sudo chown -R seu_nome:seu_nome /home/seu_nome/.ssh
sudo chmod 700 /home/seu_nome/.ssh
sudo chmod 600 /home/seu_nome/.ssh/authorized_keys

# Testar (em novo terminal)
ssh -i ~/.ssh/gafanhoto-key.pem seu_nome@IP_PUBLICO_DA_INSTANCIA
sudo whoami
# Deve retornar: root
```

<br>

## Blindar o SSH

Na AWS, o Security Group já filtra tráfego antes de chegar ao servidor. O hardening do SSH é uma segunda camada de defesa (defense in depth).

No mesmo terminal que você executou whoami:

```
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
sudo nano /etc/ssh/sshd_config
```
Configuração, pode apagar tudo (mantém o cursor na primeira linha e pressiona Ctrl+K), copia e cola:

```
# === AUTENTICAÇÃO ===
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthenticationMethods publickey
KbdInteractiveAuthentication no
PermitEmptyPasswords no
MaxAuthTries 3
MaxSessions 2
LoginGraceTime 30

# === REDE ===
# Não precisa alterar a porta como eu já mencionei, mas é uma boa prática
Port 22
AddressFamily inet

# === RESTRIÇÕES ===
AllowUsers gafanhoto
X11Forwarding no
AllowTcpForwarding no
AllowAgentForwarding no

# === CRIPTOGRAFIA ===
Ciphers aes256-gcm@openssh.com,chacha20-poly1305@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org
HostKeyAlgorithms ssh-ed25519

# === BANNERS ===
Banner /etc/issue.net
DebianBanner no

# === PAM ===
UsePAM yes

# === SFTP ===
Subsystem sftp /usr/lib/openssh/sftp-server
```

Se der algum erro ou você fizer alguma cagada, pode restaurar com: `sudo cp /etc/ssh/sshd_config.backup /etc/ssh/sshd_config`

Após isso precisa reiniciar, mas valida antes.

<br>

## Validação

```
sudo sshd -t
sudo systemctl restart ssh
```

Se aparecer `"Failed to restart sshd.service: Unit sshd.service not found."` você digitou errado, no Ubuntu 24.04 o serviço mudou de nome para apenas `"ssh"`, antes era `"sshd"`

Não fecha o terminal, abre outro e cola:

```
ssh -i ~/.ssh/gafanhoto-key.pem seu_nome@SEU_IP_PUBLICO
```

Deve entrar direto sem precisar digitar senha.


**Após confirmar que seu_nome funciona, desabilitar o usuário ubuntu:**

```
# Logar como seu_nome, depois:
sudo usermod -L ubuntu
# -L: lock (bloqueia login do usuário ubuntu)
# Se precisar reverter: sudo usermod -U ubuntu
```

<br>

## Instalar Fail2ban

Fail2ban é um programa que vigia os logs do servidor e bane automaticamente IPs que tentam invadir.

Na prática, se alguém tenta conectar via SSH no seu servidor e erra a senha 3 vezes. O fail2ban detecta essas tentativas no log (/var/log/auth.log), identifica o IP do atacante, e cria uma regra no firewall que bloqueia esse IP por um tempo (1 hora, 1 dia, 1 semana, você define).   

Por exemplo: bots tentam a todo momento invadir sua rede pela porta 22 (padrão, se preocupe com isso se usar VPS), sem fail2ban, um bot pode ficar tentando milhares de combinações de senha por hora no seu servidor. Com fail2ban, depois de 3 tentativas erradas o IP é banido e não consegue mais nem tentar.
Nesse caso em específico, o SSH já está configurado para aceitar apenas chaves (sem senha), então brute force de senha não funciona. Mesmo assim, o fail2ban ainda é útil porque reduz o ruído nos logs (bots ficam tentando e enchendo o log de lixo) e adiciona uma camada extra de proteção caso algo mude no futuro.

Dentro do servidor, logado no seu usuário `seu_nome@ip-000-00-00-00:~$`:

```
sudo apt install -y fail2ban
sudo nano /etc/fail2ban/jail.local
```

Vai abrir o terminal nano, cole essas regras:

Em: `ignoreip = 127.0.0.0/0`, substitua pelo seu IP local (localhost)

```
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
banaction = ufw
ignoreip = 127.0.0.0/0

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[recidive]
enabled = true
logpath = /var/log/fail2ban.log
bantime = 604800
findtime = 86400
maxretry = 3
```

Reinicie


```bash
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban
```

<br>

## Configurar UFW (Camada Interna de Firewall)

Mesmo que o Security Group filtre tráfego, o `ufw` dentro do servidor é defense in depth

O UFW é a interface de firewall interno do servidor. E "Defense in Depth" (Defesa em Profundidade) significa que, mesmo que o seu provedor de nuvem (AWS ou qualquer outro) tenha um firewall externo (Security Group), você também deve ter um firewall ativo dentro do próprio sistema operacional.

```
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw allow 80/tcp comment 'HTTP redirect'
sudo ufw enable
```

**Explicação dos comandos:**

`default deny incoming` Bloqueia todo o tráfego de internet tentando entrar no servidor por padrão.   
`default allow outgoing` Permite que o seu servidor acesse a internet livremente.   
`allow 22/tcp` Abre uma exceção para permitir tráfego na porta 22 (SSH) para que você possa administrar o servidor. Usei porta 22 como exemplo, substitua pela porta que você definiu.   
`allow 443/tcp e allow 80/tcp` Abre as portas para tráfego web seguro (HTTPS) e tráfego web normal (HTTP).   
`enable` Liga o firewall e aplica todas essas regras.

<br>

## Hardening do Kernel e SO

Este arquivo serve pra alterar parâmetros fundamentais do kernel do Linux, tem vários ataques clássicos de rede, com isso a gente deixa ele seguro.

Ao executar este comando, abrirá o terminal nano, cole o conteudo abaixo e salve.

```
# Parâmetros de rede seguros
sudo nano /etc/sysctl.d/99-hardening.conf
```

```ini
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv4.tcp_syncookies = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
```

![Exemplo Terminal nano](/img/exemplo_nano.png)

> [!NOTE]
> `rp_filter = 1` Protege contra IP Spoofing (quando um atacante falsifica o IP de origem).   
`accept_redirects = 0 / send_redirects = 0` Ignora rotas maliciosas enviadas via protocolo ICMP. Isso previne ataques de "Man-in-the-Middle" (interceptação de dados).   
`accept_source_route = 0` Impede que o remetente dite o caminho que o pacote de rede deve fazer, o que poderia ser usado para burlar filtros de segurança.   
`tcp_syncookies = 1`: Defesa essencial contra ataques de negação de serviço do tipo SYN Flood, onde o atacante tenta esgotar as conexões do servidor.   
`icmp_echo_ignore_broadcasts = 1` Ignora "Pings" enviados pra a rede inteira, prevenindo ataques do tipo Smurf (que tentam usar seu servidor como amplificador pra derrubar outras redes).   
`log_martians = 1` Faz o sistema registrar no log pacotes de rede com endereços IP "impossíveis" (como IPs que não deveriam existir na internet pública).   
`disable_ipv6 = 1` Desativa totalmente o protocolo IPv6. Mesmo que sua aplicação não use IPv6, desative pra reduzir a superfície de ataques e evitar configurações malfeitas.


Execute o próximo comando pra ler o arquivo que você acabou de criar e injetar essas regras no Kernel do Linux em tempo real, sem precisar reiniciar a máquina.

```
sudo sysctl --system
```

*Atualizações e limpezas automáticas:*

```bash
# instala um pacote que permite ao servidor baixar e instalar atualizações de segurança automaticamente
sudo apt install -y unattended-upgrades

# abre uma interface interativa pra você confirmar a ativação desse recurso. 
# Isso garante que correções de vulnerabilidades críticas sejam aplicadas mesmo que você esqueça de atualizar o servidor.
sudo dpkg-reconfigure -plow unattended-upgrades

# Remover serviços desnecessários
sudo systemctl disable --now snapd.service 2>/dev/null
sudo systemctl disable --now snapd.socket 2>/dev/null
sudo apt purge -y snapd 2>/dev/null

# Permissões restritivas
# Define a permissão 600 (apenas o dono/root pode ler e escrever) no arquivo principal de agendamento de tarefas (cron).
sudo chmod 600 /etc/crontab

# Define a permissão 700 (apenas o root pode ler, escrever e acessar a pasta) nos diretórios que guardam scripts agendados (diários, semanais, etc).
sudo chmod 700 /etc/cron.d /etc/cron.daily /etc/cron.hourly /etc/cron.weekly /etc/cron.monthly

# Restringe a pasta onde ficam os logs (registros) do sistema. O dono (root) faz tudo, o grupo apenas lê, e os "outros" usuários não têm acesso nenhum (0).
sudo chmod 750 /var/log

# Cria uma "Lista Branca" explícita. 
# Ao criar o arquivo cron.allow contendo apenas a palavra "seu_nome", o Linux bloqueia todos os outros usuários de criarem tarefas agendadas, permitindo apenas o usuário "seu_nome" (e o root).
echo "seu_nome" | sudo tee /etc/cron.allow

# protege o arquivo cron.allow para que ninguém além do root adicione novos nomes na lista.
sudo chmod 600 /etc/cron.allow

# Banner de advertência, isso vai aparecer pra pessoa antes dela digitar a senha ou enviar a chave SSH, copia tudo e cola (do `sudo` ou último `EOF`)
sudo tee /etc/issue.net << 'EOF'
*******************************************************************
ACESSO RESTRITO. Todas as atividades neste sistema sao monitoradas
e registradas. Acesso nao autorizado sera investigado e reportado.
*******************************************************************
EOF
```

![Interface do dkpg-reconfigure](/img/dpkg-reconfigure%20-plow%20unattended-upgrades.png)

> [!NOTE]
> - Desativamos o snapd, ele  é um gerenciador de pacotes da Canonical (Ubuntu). É útil em desktops mas em servidores ele consome memória, espaço em disco, aumenta o tempo de boot e cria interfaces virtuais de rede desnecessárias.   
> - Estes comandos desativam (disable --now) e removem completamente (purge) o Snapd do servidor, mantendo o sistema mais limpo, rápido e focado apenas no essencial. O trecho `2>/dev/null` faz com que eventuais mensagens de erro (caso o snapd já não exista) sejam ocultadas e não sujem a tela.   
> - Nesse servidor pequeno (t3.micro), o Snap consome RAM, espaço em disco e tempo de inicialização à toa. Se remover deixa o sistema mais leve e reduz a superfície de ataque.   
> - A permissão 600 impede que invasores que conseguiram um acesso de baixo privilégio leiam quais tarefas automatizadas o servidor executa (o que poderia revelar scripts vulneráveis).   
> - A permissão 700 tranca essas pastas completamente. Ninguém além do administrador consegue ver o que há dentro delas.   
> - A permissão 750 impede que um invasor leia seus logs pra planejar um ataque melhor.   

<br>

## Configurar Swap (Memória virtual)

O t3.micro só tem 1 GiB de RAM, se o servidor ficar sem RAM, o Linux ativa o "OOM Killer" (Out Of Memory Killer), que começa a "matar" processos aleatórios pra salvar o sistema (geralmente derrubando seu banco de dados ou servidor web).

```
# Criar arquivo de swap de 2GB pra servir como uma "memória RAM de emergência"
sudo fallocate -l 2G /swapfile

# Garante que só o root possa ler este arquivo
# Se a memória RAM estourar, senhas em texto puro, chaves SSL e dados de clientes podem ir parar dentro desse arquivo.
sudo chmod 600 /swapfile

# Formata o arquivo no padrão especial do Swap e o liga imediatamente.
# A partir disso, seu servidor passa a ter 1 GB de RAM + 2 GB de Swap.
sudo mkswap /swapfile
sudo swapon /swapfile

# Tornar permanente (sobrevive a reboot)
# O arquivo fstab controla o que é montado quando o servidor liga, isso garante que a Swap continue funcionando se a máquina for reiniciada.
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Ajustar swappiness (quanto menor, menos o sistema usa swap)
# 10 = só usa swap quando realmente precisar
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.d/99-hardening.conf
sudo sysctl -p /etc/sysctl.d/99-hardening.conf

# Verificar
free -h
# Deve mostrar ~2.0G na linha Swap
```

![Interface do dkpg-reconfigure](/img/exemplo_1.png)

> [!NOTE]
> O `swappiness` é um valor de 0 a 100 que diz ao Kernel o quão ansioso ele deve ser pra usar o disco rígido como memória. O padrão do Linux geralmente é 60. O disco rígido (mesmo SSD) é infinitamente mais lento que a memória RAM real. Ao mudar pra 10, você está dizendo ao Linux pra usar o arquivo de Swap se a memória RAM real estiver 90% cheia. Isso garante que o Swap não deixe o servidor lento no dia a dia. Queremos que o sistema use RAM ao máximo e só recorra ao swap em emergência.   
`free -h` exibe o consumo de memória de forma legível para humanos (em Megabytes/Gigabytes), permitindo que você confira se a linha do Swap realmente mostra os 2 GB ativos.

<br>

## Docker no EC2 focado nos 1 GiB RAM

### Instalar Docker

Instalação direta do repositório da Docker, nos repositórios do ubuntu geralmente estão desatualizados.

```
# Dependências
sudo apt install -y ca-certificates curl gnupg

# Chave GPG do Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Repositório
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Adicionar usuário ao grupo docker
sudo usermod -aG docker seu_nome

# Logout e login para aplicar
exit
ssh -i ~/.ssh/gafanhoto-key.pem seu_nome@IP_PUBLICO_DA_INSTANCIA

# Verificar
docker --version
docker compose version
```

<br>

## Hardening do Docker para o t3.micro

```
sudo nano /etc/docker/daemon.json
```

Conteúdo ajustado pra memória limitada:

```json
{
  "icc": false,
  "no-new-privileges": true,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "5m",
    "max-file": "2"
  },
  "live-restore": true,
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}
```

```bash
sudo systemctl restart docker
```
> [!NOTE]
> - Não foi usado o `userns-remap` porque consome memória adicional, pode causar problemas de permissão com volumes tipo EBS, por isso foi removido.   
> - Ele mapeia o usuário root dentro do container pra um usuário sem privilégio no host, é muito bom pra segurança porque reduz muito o impacto de um container escape. Se você usar uma instância com mais RAM tipo t3.small ou maior, vale muito a pena testar e adicionar `"userns-remap": "default"`.

**Observações sobre a instalação:**

*Dependências*   
- Ceritificados SSL pra conexões seguras: `ca-certificates`   

- Baixar arquivos via HTTP/HTTPS: `curl`   

- Trabalhar com chaves GPG (assinaturas digitais): `gnupg`   

*Chave GPG do Cocker*   
- Criar o diretório no padrão moderno do APT pra armazenar chaves: `/etc/apt/keyrings`   

- Baixar a chave GPG oficial da Docker e converter pra formato binário: `--dearmor`   

- Dar permissão de leitura pra todos os usuários, permite que o APT verifique a assinatura dos pacotes do Docker, isso garante que não intelemos pacotes adulterados: `a+r`   

*Repositório*   
- Adicionar o repositório oficial da Docker ao APT pra detectar automaticamente se é amd64, arm64, etc.: `arch=$(dpkg --print-architecture)`   

- Informar ao APT que os pacotes devem ser verificados com a chave que acabamos de adicionar: `signed-by=`   

- Pegar o codinome da distribuição, ex.: noble pra Ubuntu 24.04, jammy pra 22.04: `VERSION_CODENAME`   
Canal estável pra produção: `stable`   

*Instalar*   
- O deamon principal do Docker (dockerd): `docker-ce`   

- Cliente de linha de comando: `docker-ce-cli`   

- Runtime de baixo nível pra gerenciar containers: `containerd.iso`   

- Plugin pra docker compose versão V2 integrada: `docker-compose-plugin`   

*Adicionar usuário*   
Permite rodar comandos sem precisar usar `sudo` o tempo todo, o motivo de ter executado `exit` é por que só funciona depois do novo login.   

*Hardening do Docker*   
São configurações que evitam consumir muita memória extra, você cria/ edita o arquivo de configuração principal do Docker deamon.   

- Desabilitar a comunicação entre containers pela rede padrão: `"icc": false`, boa prática de segurança pra impedir que um container comprometido ataque outro diretamente via rede interna.   

- Impedir que processos dentro do container ganhem novos privilégios dirante a execução, seja via binários setuid ou setgid: `"no-new-privileges": true`, mesmo que o container rode como root, ele não consegue escalar privilégios adicionais, recomendado em praticamente todos os guias de hardening (CIS Docker Benchmark, OWASP, etc.).   

- Definir o driver de logs como `json-file`: `"log-driver": "json-file"` + `"log-opts"`, isso limita o tamanho dos logs pra evitar que encham o disco. Cada arquivo até 5 MB, mantendo no máximo 2 arquivos (rotaciona automaticamente). É útil em instâncias pequenas como essa pra economizar espaço.   

- Permitir que o deamon do Docker seja reiniciado ou atualizado sem parar os containers em execução (reduz downtime em produção): `"live-restore": true`   

- Definir limites padrão de recursos pra todos os containers: `"default-ulimits"`, aqui o `nofile` (número máximo de arquivos abertos) é aumentado pra 64.000 (soft e hard). Isso evita erros como "too many open files" em aplicações que lidem com muitas conexões.  

<br>

## Docker Compose do seu projeto

Nesta etapa você precisa clonar seu projeto no EC2. Dentro do servidor executagit clone + link do projeto, exatamente como você faz para clonar um repositório.
É importante que seu Dockerfile você crie um usuário não-root, se não tiver, ajuste e adiciona algo como `RUN groupadd -r projeto-gafanhoto && useradd -r -g projeto-gafanhoto -d /app -s /sbin/nologin projeto-gafanhoto`

Não use o usuário root. Dentro do servidor com docker deve aparecer algo como: `projeto-gafanhoto@k123456789d1:~$ `

Após isso, siga as etapas:

```
# Entrar na pasta
cd~/projeto-gafanhoto

# Criar o .env 
# Cola o conteúdo do .env que você tem localmente
nano .env

# instrução de segurança que altera as permissões do arquivo .env  para que apenas o proprietário do arquivo possa ler e escrever nele. 
chmod 600 .env

# Build e teste
docker compose build
docker compose run --rm gafanhoto gafanhoto --help
```

*Os exemplos que usei de teste presume um projeto executável por CLI, execute os testes do seu projeto dentro do servidor com docker.*

Se no seu projeto você usa PySpark, considere ajustar o tmpfs do  docker-compose.yml para:   

```
tmpfs:
      - /tmp:size=200M
      - /app/.cache:size=500M
```

E se você usa PySpark, provavelmente o diretório .ivy2_jars está no seu .gitignore, eles são  os JARs do Spark/Ivy que o seu projeto precisa, se estiver, pode copiar direto para o EC2 via SCP:

```
scp -i ~/.ssh/gafanhoto-key.pem -r ~/home/pasta-do-seu-projeto/projeto-gafanhoto/.ivy2_jars seu_nome@123.45.678.90:~/projeto-gafanhoto/
```
O comando fará o seguinte:
`-i ~/.ssh/gafanhoto-key.pem`: Usa sua chave privada pra autenticação.
`-r`: Copia de forma recursiva (necessário para pastas).
`~/home/pasta-do-seu-projeto/projeto-gafanhoto/.ivy2_jars`: A origem local.
`seu_nome@123.45.678.90:~/projeto-gafanhoto/`: O destino no servidor, dentro da estrutura que você criou anteriormente.

Depois no EC2, rebuild:

```
cd ~/projeto-gafanhoto
docker compose build
```

Agora testa:

```
docker compose run --rm projeto-gafanhoto projeto-gafanhoto --help
```

<br>

## Criar os diretórios de organização

Ainda dentro do servido na pasta do projeto:

```
# Criar pasta principal dentro da home com 4 subpastas dentro
mkdir -p ~/projeto-gafanhoto/{backups,scripts,config,logs}

# Restringir as permissões da pasta config, apenas seu usuário tem acesso
chmod 700 ~/projeto-gafanhoto/config
```

<br>

## Backup com S3

backup offsite automático usando S3 do Free Tier (5GB gratuitos).

**Criar bucket S3:**

```
1. Console → S3 → Create bucket
2. General purpose.
3. Bucket name: projeto-gafanhoto-backup-seu_nome-2026 (deve ser globalmente único)
4. Region: mesma da instância EC2
5. Block all public access: MARCADO (nunca exponha bucket de backup)
6. Bucket Versioning: Disabled (não queremos pagar por versões)
7. Encryption: SSE-S3 (criptografia padrão da Amazon, gratuita) - Server-side encryption with Amazon S3 managed keys (SSE-S3)
8. Bucket key: Enable
9. Advanced settings: não mexe
10. Create bucket
```

<br>

## Criar Credenciais de Acesso para S3

Para que o script de backup no EC2 envie arquivos ao S3, ele precisa de credenciais:
Seu usuário não vai ter permissão, então precisa logar como root para isso.

```
1. Console → IAM → Users → Create user
2. Nome: projeto-gafanhoto-backup-bot
3. NÃO marque "Console access" (este usuário é só para API)
4. Attach policies:
    - Crie uma policy customizada (IAM → Policies → Create policy):
    - No canto superior direito altere para de VISUAL para JSON e cole (edite com suas informações em "Resource"):
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::projeto-gafanhoto-backup-seu_nome-2026",
                "arn:aws:s3:::projeto-gafanhoto-backup-seu_nome-2026/*"
            ]
        }
    ]
}

5. Next
   - Nomeie a policy: projeto-gafanhoto-s3-backup-only

6. Create policy
6. Attach essa policy ao usuário projeto-gafanhoto-backup-bot (Crie o usuário projeto-gafanhoto-backup-bot e "anexe" (attach) essa policy nele), mesmo esquema.
    -  (IAM → Users → projeto-gafanhoto-backup-bot → Security credentials → Create access key)
7. Crie Access Key (IAM → Users → Create Users →  projeto-gafanhoto-backup-bot (NÃO marca "Provide user access to the AWS Management Console") → Next → Attach policies directly) → Busca "projeto-gafanhoto-s3-backup-only" → Next → Create User 
8. Depois de criar, vai em IAM → Users → projeto-gafanhoto-backup-bot → Security credentials → Create access key, seleciona Command Line Interface (CLI) e salva o Access Key ID e Secret Access Key ( são exibidos só uma vez).
9. SALVE o Access Key ID e Secret Access Key, são exibidos apenas uma vez
```

> [!NOTE] 
> Princípio do menor privilégio. Se as credenciais forem comprometidas, o atacante só consegue ler/escrever no bucket de backup, não pode criar instâncias, acessar outros buckets, ou fazer qualquer outra coisa na AWS.

<br>

## Configurar AWS CLI no EC2

execute um `cd ..` para sair da pasta do seu projeto e execute:

```
# Instalar AWS CLI
sudo apt install -y unzip curl
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verificar
aws --version

# Configurar credenciais, digite:
aws configure
# AWS Access Key ID: [colar o Access Key ID do passo anterior]
# AWS Secret Access Key: [colar o Secret Access Key]
# Default region name: us-east-1 (ou a região que escolheu)
# Default output format: json

# Proteger o arquivo de credenciais
chmod 600 ~/.aws/credentials

# Testar acesso
aws s3 ls s3://projeto-gafanhoto-backup-seu_nome-2026/
# Deve retornar vazio (bucket novo) sem erros
```

<br>

## Script de Backup com Upload para S3

```
nano ~/projeto-gafanhoto/scripts/backup_s3.sh
```

Conteúdo:

```
# backup_s3.sh ( Backup local + upload para S3)
set -euo pipefail

BACKUP_DIR="$HOME/projeto-gafanhoto/backups"
S3_BUCKET="s3://projeto-gafanhoto-backup-seu_nome-2026"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_NAME="projeto-gafanhoto_backup_${TIMESTAMP}.tar.gz"
LOG_FILE="$HOME/projeto-gafanhoto/logs/backup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "Iniciando backup..."

# Parar container para consistência
docker compose -f "$HOME/projeto-gafanhoto/docker-compose.yml" stop projeto-gafanhoto 2>/dev/null || true

# Criar backup comprimido
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}" \
    --exclude='backups' \
    --exclude='logs' \
    --exclude='src/.git' \
    -C "$HOME/projeto-gafanhoto" \
    data/ \
    .env \
    docker-compose.yml \
    config/

# Reiniciar container
docker compose -f "$HOME/projeto-gafanhoto/docker-compose.yml" start projeto-gafanhoto 2>/dev/null || true

# Verificar integridade
if ! tar -tzf "${BACKUP_DIR}/${BACKUP_NAME}" > /dev/null 2>&1; then
    log "ERRO: Backup corrompido! Abortando upload."
    exit 1
fi

SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}" | cut -f1)
log "Backup local OK: ${BACKUP_NAME} (${SIZE})"

# Upload para S3
if aws s3 cp "${BACKUP_DIR}/${BACKUP_NAME}" "${S3_BUCKET}/${BACKUP_NAME}" --quiet; then
    log "Upload S3 OK: ${BACKUP_NAME}"
else
    log "ERRO: Falha no upload para S3!"
    exit 1
fi

# Limpar backups locais antigos (manter últimos 3, disco é limitado)
find "${BACKUP_DIR}" -name "projeto-gafanhoto_backup_*.tar.gz" -mtime +3 -delete

# Limpar backups S3 antigos (manter últimos 7)
# Lista backups no S3 ordenados por data, remove os mais antigos que 7
BACKUP_COUNT=$(aws s3 ls "${S3_BUCKET}/" | grep "projeto-gafanhoto_backup_" | wc -l)
if [ "$BACKUP_COUNT" -gt 7 ]; then
    DELETE_COUNT=$((BACKUP_COUNT - 7))
    aws s3 ls "${S3_BUCKET}/" | grep "projeto-gafanhoto_backup_" | sort | head -n "$DELETE_COUNT" | \
        awk '{print $4}' | while read -r file; do
        aws s3 rm "${S3_BUCKET}/${file}" --quiet
        log "S3 cleanup: removido ${file}"
    done
fi

log "Backup completo."
```

Depois:

```
chmod +x ~/projeto-gafanhoto/scripts/backup_s3.sh
```

Se der erro: 

```
/etc/cron.allow: Permission denied
You (seu_nome) are not allowed to use this program (crontab)
See crontab(1) for more information
```

Diminui a restrição com: `sudo chmod 644 /etc/cron.allow` e executa `crontab -e`

![contrab](/img/AWS-crontab.png)

```
# Escolhe o editor:
1

# No terminal nano cola:
0 3 * * * /home/seu_nome/projeto-gafanhoto/scripts/backup_s3.sh

# Salva (Ctrl+X - Y - Enter)
```

<br>

##  Procedimento futuro de Restore do S3

Testa o backup manualmente para ver se está Ok:

```
~/projeto-gafanhoto/scripts/backup_s3.sh
```

Não vai aparecer nada (obviamente), mas se aparecer: `/home/seu_nome/projeto-gafanhoto/logs/backup.log: Permission denied` O diretório logs provavelmente pertence ao root. 

Executa se aparecer permissão negada:

`sudo chown seu_nome:seu_nome ~/projeto-gafanhoto/logs`

Verifica (Listar backups disponíveis):

```
aws s3 ls s3://projeto-gafanhoto-backup-seu_nome-2026/
```

Deve aparecer:

```
2026-04-15 22:45:59        719 projeto-gafanhoto_backup_20260415_224557.tar.gz
```

Depois:

`cat ~/projeto-gafanhoto/logs/backup.log`

Deve aparecer:

```
[2026-04-15 22:42:44] Iniciando backup...
[2026-04-15 22:44:19] Iniciando backup...
[2026-04-15 22:45:57] Iniciando backup...
[2026-04-15 22:45:57] Backup local OK: projeto-gafanhoto_backup_20260415_224557.tar.gz (4.0K)
[2026-04-15 22:45:58] Upload S3 OK: projeto-gafanhoto_backup_20260415_224557.tar.gz
[2026-04-15 22:45:59] Backup completo.

```

Comandos futuros:

```
# Baixar o backup desejado
aws s3 cp s3://projeto-gafanhoto-backup-seu_nome-2026/projeto-gafanhoto_backup_YYYYMMDD_HHMMSS.tar.gz ~/

# Extrair
mkdir -p ~/projeto-gafanhoto
tar -xzf ~/projeto-gafanhoto_backup_YYYYMMDD_HHMMSS.tar.gz -C ~/projeto-gafanhoto/

# Proteger .env
chmod 600 ~/projeto-gafanhoto/.env
chmod 700 ~/projeto-gafanhoto/config

# Rebuild e start
cd ~/projeto-gafanhoto
docker compose build
docker compose up -d
```

<br>

## Monitorar uso do S3 (Evitar Custos)

```bash
# Ver tamanho total do bucket
aws s3 ls s3://projeto-gafanhoto-backup-seu_nome-2026/ --summarize --human-readable | tail -2

# O Free Tier dá 5 GB. Se cada backup comprimido tem ~50MB,
# 7 backups = ~350MB, cabe tranquilo.
# Monitore se os dados do seu projeto crescerem significativamente.
```

<br>

## Monitoramento com CloudWatch

Vá para o Console:

```
1. Console → CloudWatch → Alarms → Create alarm → Classic → Select metric

Alarme 1 (CPU alta):
- Metric: EC2 → Per-Instance → Busca: CPUUtilization → seleciona a linha da sua instância
    - Threshold type: static
    - Whenever CPUUtilization is...: Greater
    - than…: 80
    - Next.

- Configure actions:
    - In alarm
    - Send a notification to the following SNS topic: Create new topic: projeto-gafanhoto-alerts
    - Email endpoints that will receive the notification…: Seu email
    - Clica em: Create topic
Não precisa mexer em Lambda, Auto Scaling, EC2 action, nem nas outras.
- Next 

- Add alarm details
    - Alarm name: gafanhoto-cpu-high

- Next
- Create Alarm
- Vá no seu e-mail e confirme a subscription
```
```
Alarme 2 (CPU credits esgotando), mesmo esquema:
- Metric: EC2 → Per-Instance → CPUCreditBalance
- Whenever CPUCreditBalance is...: Lower
- than…: 10
- Next
- Configure actions
    - Select an existing SNS topic

- Add alarm details
    - gafanhoto-cpu-credits-low
```
```
Alarme 3 (Status check failed):
- Metric: EC2 → Per-Instance → StatusCheckFailed
- Condition: Greater than 0 
- (Significa que a instância ou o hardware subjacente tem problemas)

- Add alarm details
    - gafanhoto-status-check-failed
```

**Explicação de CPU Credits (importante para t3.micro):**

Instâncias "burstable" (série t) funcionam com um sistema de créditos. Em uso normal, o t3.micro opera a ~10% da capacidade de CPU e acumula créditos. Quando precisa de mais (exemplo: build Docker, pipeline rodando), gasta créditos para usar mais CPU. Se os créditos acabarem, a CPU fica limitada a ~10%.

Exemplo: seu projeto roda um pipeline pesado por 30 minutos e consome créditos. Depois, enquanto está idle, reacumula. Para um pipeline batch que roda 1-2x por dia, os créditos são suficientes.

<br>

## Scripts de onitoramento Local

```
nano ~/projeto-gafanhoto/scripts/health_check.sh
```

```
LOG_FILE="$HOME/projeto-gafanhoto/logs/health.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
MEM_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100)}')
SWAP_USAGE=$(free | grep Swap | awk '{if ($2 > 0) printf("%.0f", $3/$2 * 100); else print "0"}')

echo "[$TIMESTAMP] Disco: ${DISK_USAGE}% | RAM: ${MEM_USAGE}% | Swap: ${SWAP_USAGE}%" >> "$LOG_FILE"

# Alertas (thresholds mais agressivos para t3.micro)
[ "$DISK_USAGE" -gt 75 ] && echo "[$TIMESTAMP] ALERTA: Disco em ${DISK_USAGE}%" >> "$LOG_FILE"
[ "$MEM_USAGE" -gt 80 ] && echo "[$TIMESTAMP] ALERTA: RAM em ${MEM_USAGE}%" >> "$LOG_FILE"
[ "$SWAP_USAGE" -gt 50 ] && echo "[$TIMESTAMP] ALERTA: Swap em ${SWAP_USAGE}% (performance degradada)" >> "$LOG_FILE"
```

```
# Torna o arquivo executável
chmod +x ~/projeto-gafanhoto/scripts/health_check.sh

# A cada 10 minutos (mais frequente que VPS, porque os limites são mais apertados)
crontab -e

# Cola junto:
*/10 * * * * /home/seu_nome/projeto-gafanhoto/scripts/health_check.sh
*/5 * * * * /home/seu_nome/projeto-gafanhoto/scripts/docker_check.sh
```

<br>

## Confirmar se está tudo certo

Roda no EC2:

```
# Verificar container
docker compose -f ~/projeto-gafanhoto/docker-compose.yml run --rm projeto-gafanhoto projeto-gafanhoto --help

# Verificar swap
free -h

# Verificar firewall
sudo ufw status

# Verificar fail2ban
sudo fail2ban-client status sshd

# Verificar backup no S3
aws s3 ls s3://projeto-gafanhoto-backup-seu_nome-2026/

# Verificar cron
crontab -l
