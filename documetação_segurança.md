#6 Segurança de Dados#

##6.1 Definição dos níveis de acesso (RBAC - Role-Based Access Control) e regras de validação de entrada de dados##

Foi utilizado o modleo RBAC (Role-Based Access Control) para ajudar no controle de acesso de cada usúario com cada funcionalidade. Definimos 3 "níveis": Administrados, Cliente e Cozinheiro. Cada um deles vai ter suas ações possíveis e ações bloqueadas onde: O Administrador possui permissões para gerenciar o cardápio e outras funções administrativas; o Cliente pode visualizar os pratos e realizar pedidos; e o Cozinheiro possui acesso às funções relacionadas ao acompanhamento e atualização dos pedidos na cozinha. Assim separamos somente as ações necessárias para cada usúario, assim usúarios não autorizados não vão poder alterar itens que possam comprometer o sistema.

Adicionamos mais uma camada de segurança no sistema onde ele possui regras de validação de entrada de dados. Isso significa que antes de salvar uma informação no banco de dados, é verificado se as características estão preenchidas de modo correto e no lugar correto, exemplo o formato do e-mail, tamanho, preço de um prato ser decimal, etc. Essas validações ajudam a impedir o envio de informações incorretas e contribuem para a segurança da aplicação, reduzindo riscos relacionados a entradas malformadas e consultas inadequadas ao banco de dados.
