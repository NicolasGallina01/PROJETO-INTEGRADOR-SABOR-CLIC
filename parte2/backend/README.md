# Backend definitivo - sessoes 1 a 5

Ingredientes e substituicoes, pedidos e fila da cozinha agora usam MySQL.
A baixa e o estorno de ingredientes ocorrem no servico Python, em transacao.
Pedido_Consumo registra a quantidade retirada no momento da compra para
permitir estorno correto mesmo se a ficha tecnica mudar depois.
Para bancos criados antes da sessao 5, execute database/03_pedido_consumo.sql.
Em uma instalacao nova, a tabela ja esta em 01_modelo_fisico.sql.

Autenticacao por sessao, usuarios, pratos e fichas tecnicas usam MySQL.
Abra a interface pelo Flask em http://127.0.0.1:5000/ (nao pelo Live Server).
GET /api/auth/me fornece o token CSRF; escritas exigem X-CSRF-Token.
Crie o primeiro administrador com:

~~~powershell
.\.venv\Scripts\python.exe -m flask --app app:create_app create-admin
~~~

O comando solicita nome, email e senha sem exibir a senha no terminal.
Nao existem contas demo no banco. Cadastros publicos sempre criam clientes.
Pratos novos devem ser criados inativos; salve a ficha antes de ativa-los.
O projeto nao usa triggers; o arquivo anterior foi removido.
Reservas, vendas e relatorios aguardam as proximas sessoes:
a interface informa essa pendencia ao tentar acessar essas operacoes.

Este e o backend da parte 2. O codigo de parte1 permanece como historico.
As funcionalidades de usuarios, catalogo, pedidos e reservas serao implementadas
nas sessoes seguintes. A interface ainda usa a API demonstrativa.

## Preparacao

Requer Python 3.10+ e MySQL 8.0.16+.
Na pasta deste README, execute:

~~~powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
~~~

Configure as credenciais no .env. Use uma chave aleatoria em SECRET_KEY.
O usuario configurado precisa acessar o banco sabor_clic.
Para criar um banco novo, abra no Workbench e execute nesta ordem:

1. database/01_modelo_fisico.sql
2. database/02_insercoes_basicas.sql

Os scripts nao apagam tabelas nem migram bancos existentes.
O usuario de execucao da aplicacao precisa de SELECT, INSERT, UPDATE e DELETE;
a criacao de tabelas deve ser feita por um usuario de instalacao.

~~~powershell
.\.venv\Scripts\python.exe -m flask --app app:create_app check-db
.\.venv\Scripts\python.exe -m flask --app app:create_app run
~~~

GET /api/health verifica o Flask.
GET /api/ready verifica uma consulta ao MySQL e retorna 503 quando indisponivel.
check-db informa a versao e o banco conectado.
Readiness verifica conectividade; a validacao do esquema exige executar os SQL.

Nesta maquina, a instancia local usa mysql-local.ini e o diretorio de dados
C:\ProgramData\MySQL\MySQL Server 8.0\Data. O Windows recusou o registro do
servico MySQL80 por falta de privilegio administrativo. start-mysql.ps1 inicia
o servidor de forma oculta quando necessario. Nesta maquina,
SaborClicMySQL.cmd foi copiado para a pasta de Inicializacao do usuario para
executar esse script ao entrar no Windows. As credenciais locais ficam em
.env e .mysql-admin.env; ambos estao ignorados pelo Git.

## Organizacao

- routes: caminhos HTTP e blueprints.
- controllers: entrada e resposta HTTP.
- services: regras de negocio e transacoes.
- models: consultas e persistencia com parametros.
- database: conexao por contexto, cursores, transacoes e scripts.
- utils: tratamento central de erros.

Os modelos de dominio serao adicionados junto de suas funcionalidades.
Nao ha endpoints de negocio simulados neste backend.

Use database.transaction() para coordenar escrita entre models.
models.base.execute exige transacao explicita e nao faz commit sozinho.
Cursores fecham ao sair do bloco; a conexao fecha ao encerrar o contexto.
Falhas na transacao provocam rollback. Transacoes aninhadas sao rejeitadas.
Nao concatene entrada do usuario ao SQL; use placeholders %s e parametros.

## Contrato inicial

Sucesso: JSON com os dados da operacao.
Erro: {"erro": {"codigo": 400, "mensagem": "Descricao"}}.
Codigos: 400 validacao, 401 login necessario, 403 acesso negado,
404 inexistente, 409 conflito, 500 falha interna, 503 banco indisponivel.

O contrato das telas sera traduzido nos controllers: id_prato -> id,
preco_unitario -> preco, estoque_atual -> quantidade e ativo -> ativa
para bancadas. Prazo estimado e persistido como data/hora; a API de pedidos
devera fornecer os minutos esperados pela tela.

Custo do ingrediente e valor/hora possuem zero como padrao, pois os formularios
atuais nao enviam esses campos. A interface devera permitir informar os valores
antes de usar precificacao/cobranca. Observacoes da reserva sao persistiveis.
O carrinho pode permanecer local; precos e disponibilidade devem ser
revalidados pelo servidor ao fechar o pedido.

## Verificacao

~~~powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
~~~

Os testes de infraestrutura usam conexoes simuladas. Eles nao substituem
a validacao dos scripts e das regras de negocio em um servidor MySQL.
