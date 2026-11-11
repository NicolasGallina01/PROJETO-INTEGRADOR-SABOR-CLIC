# Sabor & Clic — Front-end demonstrativo

Projeto **somente front-end**: HTML, CSS e JavaScript. Não é necessário instalar Python, Flask, Node.js nem banco de dados.

## Como abrir

1. Extraia o ZIP para uma pasta.
2. Abra a pasta no VS Code.
3. Abra `login.html` com a extensão **Live Server** (clique direito > Open with Live Server).
4. Navegue entre as páginas normalmente.

> O Live Server apenas disponibiliza os arquivos estáticos; ele não é um backend. A extensão é recomendada porque os scripts usam módulos ES6. Abrir os arquivos com duplo clique (`file://`) pode bloquear módulos no navegador.

## Acessos de demonstração

- Cliente: `cliente@saborclic.local`
- Cozinheiro: `cozinheiro@saborclic.local`
- Administrador: `admin@saborclic.local`
- Senha para todos: `SenhaDemo@2026`

Também é possível criar uma conta de cliente na tela de login.

## O que funciona

- Cardápio, pesquisa e filtros; carrinho e finalização de pedidos simulados.
- Acompanhamento de pedidos, atualização de status na cozinha e confirmação de entrega pelo administrador.
- Gestão de pratos, fichas técnicas, ingredientes, usuários e bancadas.
- Agendamentos com verificação de conflito de horários; relatórios calculados dos dados locais.
- Alto contraste e layout responsivo.

## Importante

Os dados ficam no **localStorage do navegador** e o usuário logado no **sessionStorage**. Eles não são compartilhados entre navegadores, dispositivos ou origens diferentes (ex.: portas diferentes do Live Server). Os perfis e senhas são **apenas uma simulação**, sem segurança de autenticação real. Não use dados pessoais ou senhas verdadeiras.

Para reiniciar a demonstração, abra o DevTools do navegador > Aplicativo/Armazenamento > Armazenamento local e remova a chave `saborclic_demo_v1`. Isso apaga os dados simulados, inclusive pedidos e contas criadas.

As fotos do cardápio usam URLs externas e dependem de internet para aparecer.

## Perfis e páginas compartilhadas (versão revisada)

- Cliente: cardápio, carrinho, acompanhamento e agendamento.
- Cozinheiro: fila KDS e cardápio em modo consulta.
- Administrador: cardápio em modo consulta, gerenciamento de cardápio, pedidos gerais, usuários, cozinhas, estoque, relatórios e fila KDS.

O perfil é obtido da sessão em cada página, não do nome da página. A navegação se adapta ao usuário autenticado; consultar o cardápio não transforma o administrador ou cozinheiro em cliente. A API simulada também verifica as permissões de cada ação. Como é uma demonstração sem servidor, esses controles não substituem segurança real.
