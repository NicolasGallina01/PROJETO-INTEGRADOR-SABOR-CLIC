import {api,setCsrf} from './api.js';
import {Usuario,Cliente,Cozinheiro,Administrador,Prato,Carrinho,Pedido} from './models.js';

const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const money = value => Number(value||0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
const esc = value => String(value??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
const friendlyDate = raw => { if (!raw) return '—';const date=new Date(raw.includes('T') ? raw : raw.replace(' ','T')+'Z');return Number.isNaN(date.valueOf()) ? esc(raw) : date.toLocaleString('pt-BR',{dateStyle:'short',timeStyle:'short'}); };
const image = src => /^https:\/\/[^\s<>'\"`]+$/i.test(src||'') ? `<img src="${esc(src)}" alt="" loading="lazy">` : '<span aria-hidden="true">🍽️</span>';
const badge = (value,label) => `<span class="status status-${esc(value)}">${esc(label??{aguardando:'Aguardando',em_preparo:'Em preparo',pronto:'Pronto',entregue:'Entregue',cancelado:'Cancelado'}[value]??value)}</span>`;
const empty = (title,detail='') => `<div class="empty-state"><strong>${esc(title)}</strong>${esc(detail)}</div>`;
const metric = (label,value,foot='') => `<div class="metric"><div class="metric-label">${esc(label)}</div><div class="metric-number">${esc(value)}</div><div class="metric-foot">${esc(foot)}</div></div>`;
const rowEmpty = (count,label) => `<tr><td colspan="${count}">${empty(label)}</td></tr>`;
const redirectByRole = {administrador:'admin-cardapio.html',cozinheiro:'cozinheiro.html',cliente:'index.html'};
const page = document.body.dataset.page;
const pageAccess={
 index:['cliente','cozinheiro','administrador'],cliente:['cliente','cozinheiro','administrador'],
 carrinho:['cliente'],rastreamento:['cliente'],agendamentos:['cliente'],
 cozinheiro:['cozinheiro','administrador'],
 'admin-cardapio':['administrador'],'admin-pedidos':['administrador'],
 'admin-estoque':['administrador'],'admin-cozinhas':['administrador'],
 'admin-usuarios':['administrador'],'admin-relatorios':['administrador']
};
const navigation={
 cliente:[['index.html','Cardápio'],['carrinho.html','Carrinho'],['rastreamento.html','Meus pedidos'],['agendamentos.html','Reservar bancada']],
 cozinheiro:[['cozinheiro.html','Fila KDS (Cozinha)'],['index.html','Ver Cardápio']],
 administrador:[['index.html','Cardápio do cliente'],['admin-cardapio.html','Gerenciar Cardápio'],['admin-pedidos.html','Pedidos Gerais'],['admin-usuarios.html','Gerenciar Usuários'],['admin-cozinhas.html','Gestão de Cozinhas'],['admin-estoque.html','Estoque de Alimentos'],['admin-relatorios.html','Relatório de Desempenho'],['cozinheiro.html','Painel da Cozinha (KDS)']]
};
function renderRoleNavigation(){
 const nav=$('.sidebar-nav');
 if(nav){
  nav.setAttribute('aria-label','Navegação do '+user.cargo);
  nav.innerHTML=navigation[user.cargo].map(([url,label],i)=>`<a class="nav-link ${url===location.pathname.split('/').pop()?'active':''}" href="${url}"><span aria-hidden="true" class="nav-symbol">${i===0?'◈':'•'}</span><span>${esc(label)}</span>${user.cargo==='cliente'&&url==='carrinho.html'?'<span class="nav-count" id="cart-count">0</span>':''}</a>`).join('');
 }
 const role=$('#user-role');if(role)role.textContent={cliente:'Cliente',cozinheiro:'Cozinheiro',administrador:'Administrador'}[user.cargo];
 const label=$('.page-head .eyebrow');if(label&&['index','cliente'].includes(page))label.textContent=user.cargo==='cliente'?'ÁREA DO CLIENTE':'VISUALIZAÇÃO DO CARDÁPIO';
 const hero=$('#menu-welcome');if(hero)hero.hidden=user.cargo!=='cliente';
 const note=$('#staff-menu-note');if(note)note.hidden=user.cargo==='cliente';
}

let user=null;let cart=new Carrinho();let state={pratos:[],pedidos:[],ingredientes:[],usuarios:[],bancadas:[],agendamentos:[],recipeDish:null,recipeRows:[],category:'Todos',kdsFilter:'ativos'};
let toastTimeout;
function toast(message,isError=false){const box=$('#toast');if(!box)return;box.textContent=message;box.hidden=false;box.classList.toggle('error',isError);clearTimeout(toastTimeout);toastTimeout=setTimeout(()=>box.hidden=true,5200);}
async function operate(callback,success){try{await callback();if(success)toast(success);}catch(error){toast(error.message||'Não foi possível completar a operação.',true);}}
function persistCart(){cart.salvar(user.id);$$('#cart-count, #hero-cart-count').forEach(el=>el.textContent=el.id==='hero-cart-count'?`(${cart.quantidade})`:cart.quantidade);}
function fillIdentity(){if(!user)return;const initial=user.nome.split(/\s+/).slice(0,2).map(x=>x[0]).join('').toUpperCase();if($('#user-name'))$('#user-name').textContent=user.nome;if($('#user-avatar'))$('#user-avatar').textContent=initial;}
function setBusy(form,busy){form.querySelectorAll('button[type="submit"]').forEach(button=>{button.disabled=busy;button.dataset.original??=button.textContent;if(busy)button.textContent='Salvando...';else button.textContent=button.dataset.original;});}
function onForm(id,handler){const el=$(id);if(!el)return;el.addEventListener('submit',async event=>{event.preventDefault();if(!el.reportValidity())return;setBusy(el,true);try{await handler();}catch(e){toast(e.message,true);}finally{setBusy(el,false);}});}
const field = id => $(id)?.value?.trim()??'';
const roles={administrador:Administrador,cliente:Cliente,cozinheiro:Cozinheiro};

async function bootstrap(){
  try{
    const auth=await api.me();setCsrf(auth.csrf);
    if(page==='login'){
      if(auth.usuario){location.replace(redirectByRole[auth.usuario.cargo]);return;}
      initializeLogin();return;
    }
    if(!auth.usuario){location.replace('login.html');return;}
    user=new (roles[auth.usuario.cargo]||Usuario)(auth.usuario);
    if(!pageAccess[page]?.includes(user.cargo)){location.replace(redirectByRole[user.cargo]);return;}
    renderRoleNavigation();
    fillIdentity();cart=Carrinho.carregar(user.id);persistCart();
    for(const [,message] of auth.mensagens??[]){if(message)toast(message);}
    switch(page){
      case 'index':case 'cliente':await initMenu();break;
      case 'carrinho':initCart();break;
      case 'rastreamento':await initTracking();break;
      case 'agendamentos':await initClientBookings();break;
      case 'cozinheiro':await initKitchen();break;
      case 'admin-cardapio':await initAdminMenu();break;
      case 'admin-pedidos':await initAdminOrders();break;
      case 'admin-estoque':await initStock();break;
      case 'admin-cozinhas':await initBenches();break;
      case 'admin-usuarios':await initUsers();break;
      case 'admin-relatorios':await initReports();break;
    }
  }catch(e){
    toast(e.message,true);
    if(page==='login') initializeLogin();
    else document.querySelectorAll('.empty-state[role="status"]').forEach(node=>{node.textContent='Não foi possível carregar os dados. Verifique a conexão com o servidor e recarregue a página.';});
  }
}
function initializeLogin(){
  const showMode=(mode)=>{
    const register=mode==='register';$('#login-form').hidden=register;$('#register-form').hidden=!register;
    $('#auth-title').textContent=register?'Crie sua conta':'Entre na sua conta';
    $('#show-login').classList.toggle('active',!register);$('#show-register').classList.toggle('active',register);
    $('#show-login').setAttribute('aria-pressed',String(!register));$('#show-register').setAttribute('aria-pressed',String(register));
  };
  $('#show-login')?.addEventListener('click',()=>showMode('login'));
  $('#show-register')?.addEventListener('click',()=>showMode('register'));
  onForm('#login-form',async()=>{
    const auth=await api.login({email:field('#login-email'),senha:field('#login-password')});
    setCsrf(auth.csrf);location.assign(redirectByRole[auth.usuario.cargo]);
  });
  onForm('#register-form',async()=>{
    const data={nome:field('#register-name'),email:field('#register-email'),endereco:field('#register-address'),senha:field('#register-password')};
    await api.register(data);toast('Conta criada! Entre com suas credenciais.');$('#login-email').value=data.email;$('#register-form').reset();showMode('login');
  });
}

// CLIENTE — CARDÁPIO
async function initMenu(){state.pratos=(await api.pratos()).map(p=>new Prato(p));
  $('#menu-search')?.addEventListener('input',renderMenu);
  $('#menu-categories')?.addEventListener('click',e=>{const btn=e.target.closest('button[data-category]');if(!btn)return;state.category=btn.dataset.category;renderMenu();});
  renderMenu();
}
function renderMenu(){
  const categories=['Todos',...new Set(state.pratos.map(p=>p.categoria))];
  const tabs=$('#menu-categories');if(tabs)tabs.innerHTML=categories.map(category=>`<button type="button" class="filter-tab ${state.category===category?'active':''}" data-category="${esc(category)}">${esc(category)}</button>`).join('');
  const search=field('#menu-search').toLocaleLowerCase('pt-BR');
  const displayed=state.pratos.filter(p=>(state.category==='Todos'||p.categoria===state.category)&&(`${p.nome} ${p.desc}`).toLocaleLowerCase('pt-BR').includes(search));
  $('#menu-grid').innerHTML=displayed.length?displayed.map(p=>`<article class="dish-card"><div class="dish-image">${image(p.img)}<span class="dish-category">${esc(p.categoria)}</span></div><div class="dish-content"><h3>${esc(p.nome)}</h3><p>${esc(p.desc)}</p><div class="dish-bottom"><span class="price">${money(p.preco)}</span>${user.cargo==='cliente'?`<button class="btn btn-outline btn-sm" type="button" data-action="add-cart" data-id="${p.id}">+ Adicionar</button>`:'<span class="muted">Somente consulta</span>'}</div></div></article>`).join(''):empty('Nenhum prato encontrado','Experimente buscar outra categoria.');
}

// CLIENTE — CARRINHO
function initCart(){renderCart();const form=$('#checkout-form');onForm('#checkout-form',async()=>{
  if(!cart.quantidade)throw Error('Adicione ao menos um prato antes de finalizar.');
  const data={itens:cart.toPedido(),forma_pagamento:field('#checkout-pagamento'),endereco_entrega:field('#checkout-endereco')};
  const order=await api.createPedido(data);cart.limpar();persistCart();toast(`Pedido #${order.id} recebido!`);location.assign('rastreamento.html');
});}
function renderCart(){const container=$('#cart-items-page');if(!container)return;
  container.innerHTML=cart.quantidade?cart.itens.map(({prato,quantidade})=>`<div class="cart-row"><div class="cart-picture">${image(prato.img)}</div><div class="cart-row-details"><h3>${esc(prato.nome)}</h3><p>${money(prato.preco)} / unidade</p><div class="cart-row-control"><button type="button" class="qty-btn" aria-label="Diminuir quantidade de ${esc(prato.nome)}" data-action="cart-minus" data-id="${prato.id}">−</button><strong>${quantidade}</strong><button type="button" class="qty-btn" aria-label="Aumentar quantidade de ${esc(prato.nome)}" data-action="cart-plus" data-id="${prato.id}">+</button><button type="button" class="link-inline" data-action="cart-remove" data-id="${prato.id}">Remover</button></div></div><strong>${money(prato.preco*quantidade)}</strong></div>`).join(''):empty('Seu carrinho está vazio','Adicione pratos no cardápio para começar.');
  $('#cart-subtotal').textContent=money(cart.total);$('#cart-total-price').textContent=money(cart.total);
  $('#checkout-submit').disabled=!cart.quantidade;
}

// PEDIDOS
async function fetchOrders(){state.pedidos=await api.pedidos();}
const statusOrder=['aguardando','em_preparo','pronto','entregue'];
const contents=p=>(p.itens??[]).map(i=>`${i.quantidade}× ${esc(i.nome)}`).join(' · ')||'Nenhum item';
async function initTracking(){await fetchOrders();renderTracking();}
function renderTracking(){const el=$('#tracking-orders');if(!el)return;
  el.innerHTML=state.pedidos.length?state.pedidos.map(p=>{const idx=Math.max(0,statusOrder.indexOf(p.status));return `<article class="order-card"><div class="order-top"><div><span class="eyebrow">PEDIDO Nº ${p.id}</span><h3>${money(p.total)} · ${esc(p.cliente)}</h3></div>${badge(p.status)}</div><p>${contents(p)}</p><p>Recebido em ${friendlyDate(p.criado_em)} · Previsão de preparo: ${p.tempo_estimado} min</p><div class="order-progress" aria-label="Progresso do pedido">${statusOrder.map((_,i)=>`<div class="progress-step ${i<=idx&&p.status!=='cancelado'?'done':''}"></div>`).join('')}</div></article>`}).join(''):empty('Nenhum pedido por enquanto','Quando você finalizar uma compra, ela aparecerá aqui.');
}
async function initAdminOrders(){await fetchOrders();renderAdminOrders();}
function renderAdminOrders(){const el=$('#admin-orders');if(!el)return;
  $('#admin-orders-metrics').innerHTML=metric('Pedidos',state.pedidos.length,'Total registrado')+metric('Em preparo',state.pedidos.filter(p=>p.status==='em_preparo').length,'Produção em andamento')+metric('Prontos',state.pedidos.filter(p=>p.status==='pronto').length,'Aguardando entrega')+metric('Valor dos pedidos',money(state.pedidos.filter(p=>p.status!=='cancelado').reduce((s,p)=>s+p.total,0)),'Acumulado');
  el.innerHTML=state.pedidos.length?state.pedidos.map(p=>`<tr><td><strong>#${p.id}</strong><div class="cell-sub">${friendlyDate(p.criado_em)}</div></td><td>${esc(p.cliente)}</td><td>${contents(p)}</td><td>${money(p.total)}</td><td>${badge(p.status)}</td><td>${p.status==='pronto'?`<button class="btn btn-primary btn-sm" data-action="deliver" data-id="${p.id}">Confirmar entrega</button>`:'—'}</td></tr>`).join(''):rowEmpty(6,'Nenhum pedido registrado.');
}
async function initKitchen(){await fetchOrders();renderKitchen();$('#kds-tabs')?.addEventListener('click',e=>{const b=e.target.closest('[data-filter]');if(!b)return;state.kdsFilter=b.dataset.filter;$$('#kds-tabs .filter-tab').forEach(x=>x.classList.toggle('active',x===b));renderKitchen();});setInterval(async()=>{if(document.hidden)return;try{await fetchOrders();renderKitchen();}catch(_){/* Ações manuais mostram erros. */}},20000);}
function renderKitchen(){if(!$('#kds-orders'))return;
  const pending=state.pedidos.filter(p=>p.status==='aguardando');const cooking=state.pedidos.filter(p=>p.status==='em_preparo');const ready=state.pedidos.filter(p=>p.status==='pronto');
  $('#kds-metrics').innerHTML=metric('Aguardando',pending.length,'Na fila')+metric('Em preparo',cooking.length,'Na cozinha')+metric('Prontos',ready.length,'Para entrega');
  const shown=state.kdsFilter==='ativos'?state.pedidos.filter(p=>['aguardando','em_preparo'].includes(p.status)):state.pedidos;
  $('#kds-orders').innerHTML=shown.length?shown.map(p=>`<article class="kds-ticket"><div class="ticket-head"><div><p class="eyebrow">PEDIDO Nº ${p.id}</p><h3>${esc(p.cliente)}</h3></div>${badge(p.status)}</div><div class="ticket-items">${(p.itens??[]).map(i=>`<p><strong>${i.quantidade}×</strong> ${esc(i.nome)}</p>`).join('')}</div><p class="ticket-date">${friendlyDate(p.criado_em)}</p><div class="ticket-actions"><span class="muted">Estimativa:</span><input type="number" min="1" max="240" value="${p.tempo_estimado}" id="time-${p.id}" aria-label="Tempo em minutos para pedido ${p.id}" ${['pronto','entregue','cancelado'].includes(p.status)?'disabled':''}><button class="btn btn-soft btn-sm" data-action="set-time" data-id="${p.id}" ${['pronto','entregue','cancelado'].includes(p.status)?'disabled':''}>Salvar</button></div><div class="ticket-actions">${p.status==='aguardando'?`<button class="btn btn-primary" data-action="status" data-id="${p.id}" data-status="em_preparo">Iniciar preparo →</button>`:p.status==='em_preparo'?`<button class="btn btn-primary" data-action="status" data-id="${p.id}" data-status="pronto">Marcar como pronto ✓</button>`:''}</div></article>`).join(''):empty('Nenhum pedido nessa visualização','Novos pedidos aparecerão automaticamente.');
}

// RESERVAS
const whenISO = value => new Date(value).toISOString();
function bookingHtml(p,canCancel=true){return `<article class="booking-card"><div class="order-top"><strong>#${p.id} · ${esc(p.bancada_nome)}</strong>${badge(p.status,p.status==='confirmado'?'Confirmado':'Cancelado')}</div><h3>${friendlyDate(p.inicio)} até ${friendlyDate(p.fim)}</h3><p>${esc(p.cliente_nome)} ${p.observacao?'· '+esc(p.observacao):''}</p>${p.status==='confirmado'&&canCancel?`<button type="button" class="link-inline" data-action="cancel-booking" data-id="${p.id}">Cancelar reserva</button>`:''}</article>`;}
async function initClientBookings(){[state.bancadas,state.agendamentos]=await Promise.all([api.bancadas(),api.agendamentos()]);
  $('#booking-bench').innerHTML='<option value="">Selecione uma bancada</option>'+state.bancadas.map(b=>`<option value="${b.id}">${esc(b.nome)} · ${esc(b.tipo)} (${b.capacidade} pessoas) · ${money(b.valor_hora)}/hora</option>`).join('');
  onForm('#booking-form',async()=>{
    const start=field('#booking-start'),end=field('#booking-end');if(!start||!end)throw Error('Escolha o início e o fim da reserva.');
    const data={bancada_id:Number(field('#booking-bench')),inicio:whenISO(start),fim:whenISO(end),observacao:field('#booking-note')};
    await api.createAgendamento(data);toast('Reserva realizada!');$('#booking-form').reset();state.agendamentos=await api.agendamentos();renderBookings();
  });renderBookings();
}
function renderBookings(){const el=$('#booking-list');if(el)el.innerHTML=state.agendamentos.length?state.agendamentos.map(x=>bookingHtml(x)).join(''):empty('Ainda não existem reservas.');}

// ADMIN — CARDÁPIO
async function initAdminMenu(){[state.pratos,state.ingredientes]=await Promise.all([api.pratos(),api.ingredientes()]);renderAdminDishes();
  onForm('#dish-form',async()=>{
    const id=Number(field('#dish-id'));
    const data={nome:field('#dish-name'),categoria:field('#dish-category'),preco:Number(field('#dish-price')),desc:field('#dish-desc'),img:field('#dish-img'),tempo_preparo:Number(field('#dish-time')),ativo:$('#dish-active').checked};
    if(id)await api.updatePrato(id,data);else await api.createPrato(data);
    toast(id?'Prato atualizado.':'Prato criado. Cadastre a ficha técnica para poder ativá-lo.');clearDish();state.pratos=await api.pratos();renderAdminDishes();
  });
}
function renderAdminDishes(){const el=$('#admin-dishes');if(!el)return;$('#dishes-total').textContent=`${state.pratos.length} itens`;
  el.innerHTML=state.pratos.length?state.pratos.map(p=>`<tr><td><strong>${esc(p.nome)}</strong><div class="cell-sub">${esc(p.desc.slice(0,75))}</div></td><td>${esc(p.categoria)}</td><td>${money(p.preco)}</td><td>${badge(p.ativo?'ok':'off',p.ativo?'Disponível':'Inativo')}</td><td><div class="cell-actions"><button class="btn btn-soft btn-sm" data-action="edit-dish" data-id="${p.id}">Editar</button><button class="btn btn-soft btn-sm" data-action="recipe" data-id="${p.id}">Ficha</button><button class="btn btn-outline btn-sm" data-action="delete-dish" data-id="${p.id}">Excluir</button></div></td></tr>`).join(''):rowEmpty(5,'Cadastre seu primeiro prato.');
}
function clearDish(){$('#dish-form')?.reset();$('#dish-id').value='';$('#dish-form-title').textContent='Cadastrar novo prato';}
async function openRecipe(id){const prato=state.pratos.find(p=>p.id===id);if(!prato)return;
  state.recipeDish=id;state.recipeRows=await api.ficha(id);renderRecipe();$('#recipe-editor')?.scrollIntoView({block:'nearest',behavior:'smooth'});
}
function renderRecipe(){const el=$('#recipe-editor');if(!el||!state.recipeDish)return;
  const dish=state.pratos.find(p=>p.id===state.recipeDish);
  const selectOptions=(selected)=>'<option value="">Ingrediente...</option>'+state.ingredientes.map(i=>`<option value="${i.id}" ${Number(selected)===i.id?'selected':''}>${esc(i.nome)} (${esc(i.unidade)})</option>`).join('');
  el.innerHTML=`<div class="surface-heading"><strong>${esc(dish?.nome??'Prato')}</strong><span class="count-pill">${state.recipeRows.length} ingrediente(s)</span></div><p class="form-hint">Informe a quantidade consumida para preparar uma unidade do prato.</p><div id="recipe-rows">${state.recipeRows.map((r,index)=>`<div class="recipe-row"><select aria-label="Ingrediente ${index+1}" data-recipe-index="${index}" data-recipe-key="ingrediente_id">${selectOptions(r.ingrediente_id)}</select><input aria-label="Quantidade do ingrediente ${index+1}" type="number" min="0.001" step="0.001" value="${r.quantidade}" data-recipe-index="${index}" data-recipe-key="quantidade"><button type="button" aria-label="Remover ingrediente ${index+1}" data-action="remove-recipe" data-index="${index}">×</button></div>`).join('')}</div><div class="button-row"><button type="button" class="btn btn-soft" data-action="add-recipe">+ Ingrediente</button><button type="button" class="btn btn-primary" data-action="save-recipe">Salvar ficha</button></div>`;
  el.querySelectorAll('[data-recipe-index]').forEach(input=>input.addEventListener('input',()=>{const idx=Number(input.dataset.recipeIndex);state.recipeRows[idx][input.dataset.recipeKey]=input.dataset.recipeKey==='quantidade'?Number(input.value):Number(input.value);}));
}

// ADMIN — INGREDIENTES
async function initStock(){state.ingredientes=await api.ingredientes();renderStock();
  onForm('#ingredient-form',async()=>{await api.createIngrediente({nome:field('#ingredient-name'),categoria:field('#ingredient-category'),unidade:field('#ingredient-unit'),quantidade:Number(field('#ingredient-amount')),estoque_minimo:Number(field('#ingredient-min'))});$('#ingredient-form').reset();state.ingredientes=await api.ingredientes();renderStock();toast('Ingrediente cadastrado.');});
}
function renderStock(){const list=state.ingredientes;$('#ingredients-total').textContent=`${list.length} ingredientes`;
  $('#stock-metrics').innerHTML=metric('Ingredientes',list.length,'No inventário')+metric('Estoque baixo',list.filter(i=>i.quantidade<=i.estoque_minimo).length,'Requer atenção')+metric('Dentro do mínimo',list.filter(i=>i.quantidade>i.estoque_minimo).length,'Sem alertas');
  $('#admin-ingredients').innerHTML=list.length?list.map(i=>`<tr><td><strong>${esc(i.nome)}</strong></td><td>${esc(i.categoria)}</td><td><strong>${i.quantidade.toLocaleString('pt-BR')}</strong> ${esc(i.unidade)}</td><td>${i.estoque_minimo.toLocaleString('pt-BR')} ${esc(i.unidade)}</td><td>${badge(i.quantidade<=i.estoque_minimo?'low':'ok',i.quantidade<=i.estoque_minimo?'Abaixo do mínimo':'Adequado')}</td><td><div class="cell-actions"><button class="btn btn-soft btn-sm" data-action="restock" data-id="${i.id}">Repor</button><button class="btn btn-soft btn-sm" data-action="min-stock" data-id="${i.id}">Mínimo</button></div></td></tr>`).join(''):rowEmpty(6,'Sem ingredientes cadastrados.');
}

// ADMIN — USUÁRIOS
async function initUsers(){state.usuarios=await api.usuarios();renderUsers();onForm('#user-form',async()=>{
  await api.createUsuario({nome:field('#new-user-name'),email:field('#new-user-email'),senha:field('#new-user-password'),cargo:field('#new-user-role'),endereco:field('#new-user-address'),turno:field('#new-user-shift'),especialidade:field('#new-user-specialty')});$('#user-form').reset();state.usuarios=await api.usuarios();renderUsers();toast('Usuário cadastrado com sucesso.');
});}
function renderUsers(){const list=state.usuarios;$('#users-total').textContent=`${list.length} usuários`;
  $('#admin-users').innerHTML=list.length?list.map(u=>`<tr><td><strong>${esc(u.nome)}</strong></td><td>${esc(u.email)}</td><td>${esc({administrador:'Administrador',cozinheiro:'Cozinheiro',cliente:'Cliente'}[u.cargo]??u.cargo)}</td><td>${badge(u.ativo?'ok':'off',u.ativo?'Ativo':'Desativado')}</td><td><button type="button" class="btn btn-soft btn-sm" data-action="toggle-user" data-id="${u.id}" ${u.id===user.id?'disabled title="Não é possível desativar sua própria conta"':''}>${u.ativo?'Desativar':'Reativar'}</button></td></tr>`).join(''):rowEmpty(5,'Nenhuma conta cadastrada.');
}

// ADMIN — BANCADAS E RESERVAS
async function initBenches(){[state.bancadas,state.agendamentos]=await Promise.all([api.bancadas(),api.agendamentos()]);renderBenches();
  onForm('#bench-form',async()=>{await api.createBancada({nome:field('#bench-name'),tipo:field('#bench-type'),capacidade:Number(field('#bench-capacity')),valor_hora:Number(field('#bench-rate'))});$('#bench-form').reset();state.bancadas=await api.bancadas();renderBenches();toast('Bancada cadastrada.');});
}
function renderBenches(){const el=$('#admin-benches');if(!el)return;
  $('#benches-total').textContent=`${state.bancadas.length} bancadas`;
  el.innerHTML=state.bancadas.length?state.bancadas.map(b=>`<article class="bench-card"><span class="eyebrow">ESPAÇO ${b.id}</span><h3>${esc(b.nome)}</h3><p>${esc(b.tipo)} · Capacidade: ${b.capacidade} pessoa(s)</p><div class="order-top">${badge(b.ativa?'ok':'off',b.ativa?'Disponível':'Em manutenção')}<button type="button" class="btn btn-soft btn-sm" data-action="toggle-bench" data-id="${b.id}">${b.ativa?'Desativar':'Ativar'}</button></div></article>`).join(''):empty('Cadastre uma bancada.');
  $('#admin-bookings').innerHTML=state.agendamentos.length?state.agendamentos.slice(0,12).map(b=>bookingHtml(b)).join(''):empty('Ainda não há reservas.');
}

// ADMIN — RELATÓRIOS
async function initReports(){const r=await api.relatorios();$('#report-metrics').innerHTML=metric('Receita do mês',money(r.receita_mes),'Pedidos não cancelados')+metric('Pedidos no mês',r.pedidos_mes,'Total do período')+metric('Reservas do mês',r.reservas_mes,'Agendamentos confirmados')+metric('Alertas no estoque',r.estoque_baixo.length,'Ingredientes abaixo do mínimo');
  await renderPayments();
  $('#refresh-payments').onclick=()=>operate(renderPayments);
  const top=r.mais_vendidos??[];const topMax=Math.max(1,...top.map(i=>i.quantidade));
  $('#report-top-products').innerHTML=top.length?top.map(i=>bar(i.nome,i.quantidade,topMax)).join(''):empty('Ainda não há vendas.');
  const status=r.por_status??[];const statMax=Math.max(1,...status.map(i=>i.quantidade));
  $('#report-status').innerHTML=status.length?status.map(i=>bar(Pedido.labels()[i.status]??i.status,i.quantidade,statMax)).join(''):empty('Sem pedidos registrados.');
  $('#report-low-stock').innerHTML=r.estoque_baixo.length?r.estoque_baixo.map(i=>`<article class="booking-card"><div class="order-top"><strong>${esc(i.nome)}</strong>${badge('low','Abaixo do mínimo')}</div><p>${i.quantidade} ${esc(i.unidade)} restantes · Mínimo: ${i.estoque_minimo} ${esc(i.unidade)}</p></article>`).join(''):empty('Tudo em dia!','Nenhum ingrediente está abaixo do estoque mínimo.');
}
function bar(label,value,max){return `<div class="bar-row"><div class="bar-label"><strong>${esc(label)}</strong><span>${value}</span></div><progress class="bar-progress" value="${Math.max(0,value)}" max="${Math.max(1,max)}" aria-label="${esc(label)}: ${value}"></progress></div>`;}

async function renderPayments(){
  const rows=await api.pagamentos();
  $('#payments-list').innerHTML=rows.length?rows.map(p=>`<article class="booking-card"><strong>Pagamento #${p.id_venda} · ${money(p.valor_pagamento)}</strong><p>${p.id_agendamento?'Reserva #'+p.id_agendamento:'Pedido'} · ${esc(p.status_pagamento)}</p>${p.status_pagamento==='pendente'?`<select id="payment-method-${p.id_venda}" aria-label="Forma de pagamento"><option value="PIX">PIX</option><option value="DINHEIRO">Dinheiro</option><option value="DEBITO">Débito</option><option value="CREDITO">Crédito</option></select><button class="btn btn-primary" data-action="confirm-payment" data-id="${p.id_venda}">Confirmar recebimento</button>`:''}</article>`).join(''):empty('Nenhum pagamento registrado.');
}

// EVENTOS GERAIS (sem atributos onclick)
document.addEventListener('click',async e=>{
  const button=e.target.closest('button[data-action]');if(!button)return;
  const action=button.dataset.action,id=Number(button.dataset.id);
  if(action==='contrast')return; // theme.js administra o contraste
  if(action==='logout'){await operate(async()=>{await api.logout();location.replace('login.html');});return;}
  if(!user)return;
  if(action==='confirm-payment'){if(!confirm('Confirmar que o valor foi recebido?'))return;await operate(async()=>{await api.confirmarPagamento(id,$(`#payment-method-${id}`).value);await renderPayments();},'Recebimento registrado.');return;}
  if(action==='add-cart'){
    if(user.cargo!=='cliente'){toast('Somente clientes podem adicionar itens ao carrinho.',true);return;}
    const dish=state.pratos.find(p=>p.id===id);if(!dish)return;
    try{cart.adicionar(dish);persistCart();toast(`${dish.nome} adicionado ao carrinho.`);}catch(error){toast(error.message,true);}return;
  }
  if(action.startsWith('cart-')){
    try{if(action==='cart-plus')cart.alterar(id,1);else if(action==='cart-minus')cart.alterar(id,-1);else if(action==='cart-remove')cart.remover(id);persistCart();renderCart();}catch(error){toast(error.message,true);}return;
  }
  if(action==='refresh-orders'){await operate(async()=>{await fetchOrders();if(page==='cozinheiro')renderKitchen();else if(page==='admin-pedidos')renderAdminOrders();else renderTracking();},'Pedidos atualizados.');return;}
  if(action==='status'||action==='deliver'){await operate(async()=>{await api.changeStatus(id,action==='deliver'?'entregue':button.dataset.status);await fetchOrders();page==='cozinheiro'?renderKitchen():renderAdminOrders();},'Status atualizado.');return;}
  if(action==='set-time'){await operate(async()=>{const input=$(`#time-${id}`);await api.changeTempo(id,Number(input.value));await fetchOrders();renderKitchen();},'Estimativa atualizada.');return;}
  if(action==='cancel-booking'){if(!confirm('Cancelar esta reserva?'))return;await operate(async()=>{await api.cancelAgendamento(id);state.agendamentos=await api.agendamentos();page==='agendamentos'?renderBookings():renderBenches();},'Reserva cancelada.');return;}
  if(action==='edit-dish'){const p=state.pratos.find(x=>x.id===id);if(!p)return;$('#dish-id').value=p.id;$('#dish-name').value=p.nome;$('#dish-category').value=p.categoria;$('#dish-price').value=p.preco;$('#dish-desc').value=p.desc;$('#dish-time').value=p.tempo_preparo;$('#dish-img').value=p.img;$('#dish-active').checked=p.ativo;$('#dish-form-title').textContent='Editar prato';$('#dish-form').scrollIntoView({behavior:'smooth'});return;}
  if(action==='clear-dish'){clearDish();return;}
  if(action==='delete-dish'){if(!confirm('Remover este prato do catálogo? O histórico de pedidos será mantido.'))return;await operate(async()=>{await api.deletePrato(id);state.pratos=await api.pratos();renderAdminDishes();},'Prato removido.');return;}
  if(action==='recipe'){await operate(()=>openRecipe(id));return;}
  if(action==='add-recipe'){state.recipeRows.push({ingrediente_id:0,quantidade:1});renderRecipe();return;}
  if(action==='remove-recipe'){state.recipeRows.splice(Number(button.dataset.index),1);renderRecipe();return;}
  if(action==='save-recipe'){await operate(async()=>{const items=state.recipeRows.map(x=>({ingrediente_id:Number(x.ingrediente_id),quantidade:Number(x.quantidade)}));await api.saveFicha(state.recipeDish,items);},'Ficha técnica salva.');return;}
  if(action==='restock'){const q=prompt('Quantidade a acrescentar ao estoque:','10');if(q===null)return;await operate(async()=>{await api.updateIngrediente(id,{repor:Number(q)});state.ingredientes=await api.ingredientes();renderStock();},'Estoque reposto.');return;}
  if(action==='min-stock'){const item=state.ingredientes.find(x=>x.id===id);const q=prompt('Novo estoque mínimo:',String(item.estoque_minimo));if(q===null)return;await operate(async()=>{await api.updateIngrediente(id,{estoque_minimo:Number(q)});state.ingredientes=await api.ingredientes();renderStock();},'Mínimo atualizado.');return;}
  if(action==='toggle-user'){const item=state.usuarios.find(x=>x.id===id);if(!item)return;await operate(async()=>{await api.changeUsuario(id,!item.ativo);state.usuarios=await api.usuarios();renderUsers();},'Permissão atualizada.');return;}
  if(action==='toggle-bench'){const item=state.bancadas.find(x=>x.id===id);if(!item)return;await operate(async()=>{await api.changeBancada(id,!item.ativa);state.bancadas=await api.bancadas();renderBenches();},'Bancada atualizada.');}
});

document.addEventListener('DOMContentLoaded',bootstrap);
