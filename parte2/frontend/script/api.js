/* Simulação local da API: dados persistidos no navegador, sem servidor ou banco. */
const KEY='saborclic_demo_v1', SESSION='saborclic_usuario_demo';
const clone=x=>JSON.parse(JSON.stringify(x));
const now=()=>new Date().toISOString();
const seed=()=>({
 usuarios:[
  {id:1,nome:'Administrador Demo',email:'admin@saborclic.local',senha:'SenhaDemo@2026',cargo:'administrador',ativo:true},
  {id:2,nome:'Cliente Demo',email:'cliente@saborclic.local',senha:'SenhaDemo@2026',cargo:'cliente',ativo:true},
  {id:3,nome:'Cozinheiro Demo',email:'cozinheiro@saborclic.local',senha:'SenhaDemo@2026',cargo:'cozinheiro',ativo:true}],
 pratos:[
  {id:1,nome:'X-Burguer Artesanal',categoria:'Lanches',desc:'Hambúrguer suculento, cheddar derretido e pão brioche macio.',preco:32.9,img:'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=700&q=80',tempo_preparo:20,ativo:true},
  {id:2,nome:'Pizza Margherita',categoria:'Pizzas',desc:'Molho de tomate, muçarela e manjericão fresquinho.',preco:54,img:'https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?w=700&q=80',tempo_preparo:30,ativo:true},
  {id:3,nome:'Açaí Especial 500ml',categoria:'Sobremesas',desc:'Açaí cremoso com banana e complementos especiais.',preco:24.5,img:'https://images.unsplash.com/photo-1590301157890-4810ed352733?w=700&q=80',tempo_preparo:8,ativo:true},
  {id:4,nome:'Batata Rústica',categoria:'Acompanhamentos',desc:'Batatas crocantes por fora e macias por dentro.',preco:18.9,img:'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=700&q=80',tempo_preparo:15,ativo:true},
  {id:5,nome:'Cappuccino Cremoso',categoria:'Bebidas',desc:'Espresso encorpado com leite vaporizado.',preco:15.9,img:'https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?w=700&q=80',tempo_preparo:6,ativo:true},
  {id:6,nome:'Pizza de Queijo',categoria:'Pizzas',desc:'Uma combinação clássica de queijo e massa leve.',preco:49.9,img:'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=700&q=80',tempo_preparo:25,ativo:true}],
 ingredientes:[
  ['Hambúrguer bovino','Carnes','un',80,12],['Pão brioche','Panificação','un',100,15],['Queijo cheddar','Laticínios','fatia',130,20],['Massa de pizza','Massas','un',45,8],['Muçarela','Laticínios','g',15000,2000],['Tomate','Hortifruti','g',12000,1800],['Açaí','Congelados','ml',18000,3000],['Banana','Hortifruti','un',75,12],['Batata','Hortifruti','g',14000,2000],['Óleo de cozinha','Mercearia','ml',7500,1200],['Café em grãos','Bebidas','g',4800,650],['Leite','Laticínios','ml',16000,2500]].map(([nome,categoria,unidade,quantidade,estoque_minimo],i)=>({id:i+1,nome,categoria,unidade,quantidade,estoque_minimo})),
 fichas:{1:[{ingrediente_id:1,quantidade:1},{ingrediente_id:2,quantidade:1},{ingrediente_id:3,quantidade:2}],2:[{ingrediente_id:4,quantidade:1},{ingrediente_id:5,quantidade:200},{ingrediente_id:6,quantidade:130}],3:[{ingrediente_id:7,quantidade:500},{ingrediente_id:8,quantidade:1}],4:[{ingrediente_id:9,quantidade:250},{ingrediente_id:10,quantidade:30}],5:[{ingrediente_id:11,quantidade:15},{ingrediente_id:12,quantidade:200}],6:[{ingrediente_id:4,quantidade:1},{ingrediente_id:5,quantidade:260}]},
 bancadas:[{id:1,nome:'Bancada 01',tipo:'Fornos e pizzas',capacidade:4,ativa:true},{id:2,nome:'Bancada 02',tipo:'Chapas e fritadeiras',capacidade:3,ativa:true},{id:3,nome:'Bancada 03',tipo:'Confeitaria',capacidade:2,ativa:false},{id:4,nome:'Bancada 04',tipo:'Preparação geral',capacidade:5,ativa:true}],
 pedidos:[],agendamentos:[]
});
function read(){try{const x=JSON.parse(localStorage.getItem(KEY));if(x&&Array.isArray(x.usuarios)&&Array.isArray(x.pratos))return x;}catch(_){}const x=seed();write(x);return x;}
function write(x){try{localStorage.setItem(KEY,JSON.stringify(x));}catch(_){throw Error('O navegador bloqueou o armazenamento local. Use o Live Server e permita dados do site.');}}
const nextId=arr=>Math.max(0,...arr.map(x=>Number(x.id)||0))+1;
const currentId=()=>Number(sessionStorage.getItem(SESSION)||0);
function requireUser(db){const u=db.usuarios.find(x=>x.id===currentId()&&x.ativo);if(!u)throw Error('Faça login para continuar.');return u;}
function requireRole(u,...roles){if(!roles.includes(u.cargo))throw Error('Esta ação não está disponível para este perfil.');}
function publicUser(u){const {senha,...safe}=u;return safe;}
const nonempty=(v,label)=>{if(!String(v??'').trim())throw Error(`Informe ${label}.`);return String(v).trim();};
const positive=(v,label)=>{const n=Number(v);if(!Number.isFinite(n)||n<=0)throw Error(`${label} deve ser maior que zero.`);return n;};
const nonnegative=(v,label)=>{const n=Number(v);if(!Number.isFinite(n)||n<0)throw Error(`${label} não pode ser negativo.`);return n;};
const commit=(db,value)=>{write(db);return clone(value);};
const pause=()=>new Promise(resolve=>setTimeout(resolve,30));
export const setCsrf=()=>{};
export async function requestApi(path,{method='GET',body={}}={}){
 await pause();const db=read();const parts=path.split('/').filter(Boolean),resource=parts[0],id=Number(parts[1]);
 if(resource==='auth'){
  if(parts[1]==='me'){const u=db.usuarios.find(x=>x.id===currentId()&&x.ativo);return {csrf:'demo',usuario:u?publicUser(u):null,mensagens:[]};}
  if(parts[1]==='logout'){sessionStorage.removeItem(SESSION);return {ok:true};}
  if(parts[1]==='login'){
   const u=db.usuarios.find(x=>x.email.toLowerCase()===String(body.email||'').trim().toLowerCase()&&x.senha===body.senha);
   if(!u||!u.ativo)throw Error('E-mail ou senha inválidos, ou conta desativada.');sessionStorage.setItem(SESSION,String(u.id));return {csrf:'demo',usuario:publicUser(u)};
  }
  if(parts[1]==='registro'){
   const email=nonempty(body.email,'o e-mail').toLowerCase();if(db.usuarios.some(x=>x.email.toLowerCase()===email))throw Error('Este e-mail já está cadastrado.');
   const senha=nonempty(body.senha,'a senha');if(senha.length<6)throw Error('A senha deve ter pelo menos 6 caracteres.');
   const u={id:nextId(db.usuarios),nome:nonempty(body.nome,'o nome'),email,senha,cargo:'cliente',endereco:body.endereco||'',ativo:true};db.usuarios.push(u);return commit(db,{usuario:publicUser(u)});
  }
 }
 const u=requireUser(db),admin=u.cargo==='administrador',staff=admin||u.cargo==='cozinheiro';
 if(resource==='pratos'){
  if(method==='GET'&&parts[2]==='ficha'){requireRole(u,'administrador');return clone(db.fichas[id]||[]);}
  if(method==='PUT'&&parts[2]==='ficha'){requireRole(u,'administrador');if(!db.pratos.some(p=>p.id===id))throw Error('Prato não encontrado.');
   const rows=body.ingredientes||[];if(rows.some(r=>!db.ingredientes.some(i=>i.id===Number(r.ingrediente_id))||Number(r.quantidade)<=0))throw Error('Selecione ingredientes válidos e quantidades positivas.');
   if(new Set(rows.map(r=>Number(r.ingrediente_id))).size!==rows.length)throw Error('Não repita o mesmo ingrediente na ficha.');db.fichas[id]=rows.map(r=>({ingrediente_id:Number(r.ingrediente_id),quantidade:Number(r.quantidade)}));return commit(db,{ok:true});}
  if(method==='GET')return clone(admin?db.pratos:db.pratos.filter(p=>p.ativo));
  requireRole(u,'administrador');
  if(method==='DELETE'){const p=db.pratos.find(p=>p.id===id);if(!p)throw Error('Prato não encontrado.');p.ativo=false;return commit(db,{ok:true});}
  const data={nome:nonempty(body.nome,'o nome do prato'),categoria:nonempty(body.categoria,'a categoria'),preco:positive(body.preco,'O preço'),desc:String(body.desc||''),img:String(body.img||''),tempo_preparo:positive(body.tempo_preparo,'O tempo de preparo'),ativo:Boolean(body.ativo)};
  if(method==='POST'){const p={id:nextId(db.pratos),...data};db.pratos.push(p);return commit(db,p);}
  const p=db.pratos.find(p=>p.id===id);if(!p)throw Error('Prato não encontrado.');Object.assign(p,data);return commit(db,p);
 }
 if(resource==='pedidos'){
  if(method==='GET')return clone(staff?db.pedidos:db.pedidos.filter(p=>p.cliente_id===u.id));
  if(method==='POST'){
   requireRole(u,'cliente');if(!Array.isArray(body.itens)||!body.itens.length)throw Error('O carrinho está vazio.');
   const itens=body.itens.map(item=>{const p=db.pratos.find(x=>x.id===Number(item.prato_id)&&x.ativo);if(!p)throw Error('Um prato do carrinho não está mais disponível.');const quantidade=Number(item.quantidade);if(!Number.isInteger(quantidade)||quantidade<1||quantidade>50)throw Error('Quantidade inválida.');return {prato_id:p.id,nome:p.nome,quantidade,preco_unitario:p.preco};});
   const required=new Map();for(const item of itens)for(const r of db.fichas[item.prato_id]||[])required.set(r.ingrediente_id,(required.get(r.ingrediente_id)||0)+r.quantidade*item.quantidade);
   for(const [ingredientId,quantity] of required){const ing=db.ingredientes.find(x=>x.id===ingredientId);if(!ing||ing.quantidade<quantity)throw Error(`Estoque insuficiente para ${ing?.nome||'um ingrediente'}.`);}
   for(const [ingredientId,quantity] of required)db.ingredientes.find(x=>x.id===ingredientId).quantidade-=quantity;
   const p={id:nextId(db.pedidos),cliente_id:u.id,cliente:u.nome,itens,total:Number(itens.reduce((s,x)=>s+x.quantidade*x.preco_unitario,0).toFixed(2)),status:'aguardando',tempo_estimado:Math.max(...itens.map(x=>db.pratos.find(p=>p.id===x.prato_id).tempo_preparo)),forma_pagamento:nonempty(body.forma_pagamento,'a forma de pagamento'),endereco_entrega:String(body.endereco_entrega||''),criado_em:now()};db.pedidos.unshift(p);return commit(db,p);
  }
  const p=db.pedidos.find(p=>p.id===id);if(!p)throw Error('Pedido não encontrado.');requireRole(u,'administrador','cozinheiro');
  if(parts[2]==='status'){const transitions={aguardando:['em_preparo'],em_preparo:['pronto'],pronto:['entregue'],entregue:[],cancelado:[]};if(!transitions[p.status].includes(body.status))throw Error('Transição de status inválida.');if(body.status==='entregue'&&!admin)throw Error('Apenas o administrador confirma a entrega.');p.status=body.status;}
  else if(parts[2]==='tempo'){if(!['aguardando','em_preparo'].includes(p.status))throw Error('Pedido já finalizado.');p.tempo_estimado=positive(body.tempo_estimado,'A estimativa');if(p.tempo_estimado>240)throw Error('Limite de 240 minutos.');}
  return commit(db,p);
 }
 if(resource==='ingredientes'){
  requireRole(u,'administrador');if(method==='GET')return clone(db.ingredientes);
  if(method==='POST'){const ing={id:nextId(db.ingredientes),nome:nonempty(body.nome,'o ingrediente'),categoria:nonempty(body.categoria,'a categoria'),unidade:nonempty(body.unidade,'a unidade'),quantidade:nonnegative(body.quantidade,'A quantidade'),estoque_minimo:nonnegative(body.estoque_minimo,'O estoque mínimo')};db.ingredientes.push(ing);return commit(db,ing);}
  const ing=db.ingredientes.find(x=>x.id===id);if(!ing)throw Error('Ingrediente não encontrado.');if(body.repor!==undefined)ing.quantidade+=positive(body.repor,'A reposição');if(body.estoque_minimo!==undefined)ing.estoque_minimo=nonnegative(body.estoque_minimo,'O estoque mínimo');return commit(db,ing);
 }
 if(resource==='usuarios'){
  requireRole(u,'administrador');if(method==='GET')return clone(db.usuarios.map(publicUser));
  if(method==='POST'){const email=nonempty(body.email,'o e-mail').toLowerCase();if(db.usuarios.some(x=>x.email===email))throw Error('E-mail já cadastrado.');if(!['cliente','cozinheiro','administrador'].includes(body.cargo))throw Error('Perfil inválido.');const novo={...body,id:nextId(db.usuarios),nome:nonempty(body.nome,'o nome'),email,senha:nonempty(body.senha,'a senha'),ativo:true};db.usuarios.push(novo);return commit(db,publicUser(novo));}
  const target=db.usuarios.find(x=>x.id===id);if(!target)throw Error('Usuário não encontrado.');if(target.id===u.id&&!body.ativo)throw Error('Não é possível desativar sua conta.');target.ativo=Boolean(body.ativo);return commit(db,publicUser(target));
 }
 if(resource==='bancadas'){
  if(method==='GET')return clone(admin?db.bancadas:db.bancadas.filter(b=>b.ativa));requireRole(u,'administrador');
  if(method==='POST'){const b={id:nextId(db.bancadas),nome:nonempty(body.nome,'o nome'),tipo:nonempty(body.tipo,'o tipo'),capacidade:positive(body.capacidade,'A capacidade'),ativa:true};db.bancadas.push(b);return commit(db,b);}
  const b=db.bancadas.find(x=>x.id===id);if(!b)throw Error('Bancada não encontrada.');b.ativa=Boolean(body.ativa);return commit(db,b);
 }
 if(resource==='agendamentos'){
  if(method==='GET')return clone(admin?db.agendamentos:db.agendamentos.filter(a=>a.cliente_id===u.id));
  if(method==='POST'){
   requireRole(u,'cliente');const b=db.bancadas.find(x=>x.id===Number(body.bancada_id)&&x.ativa);if(!b)throw Error('Selecione uma bancada disponível.');
   const start=new Date(body.inicio).getTime(),end=new Date(body.fim).getTime();if(!Number.isFinite(start)||!Number.isFinite(end)||start>=end||start<Date.now())throw Error('Escolha um período futuro válido.');
   if(db.agendamentos.some(a=>a.bancada_id===b.id&&a.status==='confirmado'&&start<new Date(a.fim).getTime()&&end>new Date(a.inicio).getTime()))throw Error('Esta bancada já está reservada nesse horário.');
   const a={id:nextId(db.agendamentos),bancada_id:b.id,bancada_nome:b.nome,cliente_id:u.id,cliente_nome:u.nome,inicio:new Date(start).toISOString(),fim:new Date(end).toISOString(),observacao:String(body.observacao||''),status:'confirmado'};db.agendamentos.unshift(a);return commit(db,a);
  }
  const a=db.agendamentos.find(x=>x.id===id);if(!a)throw Error('Reserva não encontrada.');if(!admin&&a.cliente_id!==u.id)throw Error('Você não pode cancelar esta reserva.');a.status='cancelado';return commit(db,a);
 }
 if(resource==='relatorios'){
  requireRole(u,'administrador');const month=now().slice(0,7),orders=db.pedidos.filter(p=>p.criado_em.slice(0,7)===month),sold=new Map(),statuses=new Map();
  for(const p of db.pedidos){statuses.set(p.status,(statuses.get(p.status)||0)+1);if(p.status!=='cancelado')for(const item of p.itens)sold.set(item.nome,(sold.get(item.nome)||0)+item.quantidade);}
  return {receita_mes:Number(orders.filter(p=>p.status!=='cancelado').reduce((s,p)=>s+p.total,0).toFixed(2)),pedidos_mes:orders.length,reservas_mes:db.agendamentos.filter(a=>a.status==='confirmado'&&a.inicio.slice(0,7)===month).length,estoque_baixo:clone(db.ingredientes.filter(i=>i.quantidade<=i.estoque_minimo)),mais_vendidos:[...sold].map(([nome,quantidade])=>({nome,quantidade})).sort((a,b)=>b.quantidade-a.quantidade).slice(0,5),por_status:[...statuses].map(([status,quantidade])=>({status,quantidade}))};
 }
 throw Error('Operação não disponível nesta demonstração.');
}
export const api={
 me:()=>requestApi('/auth/me'),login:data=>requestApi('/auth/login',{method:'POST',body:data}),register:data=>requestApi('/auth/registro',{method:'POST',body:data}),logout:()=>requestApi('/auth/logout',{method:'POST'}),
 pratos:()=>requestApi('/pratos'),createPrato:data=>requestApi('/pratos',{method:'POST',body:data}),updatePrato:(id,data)=>requestApi(`/pratos/${id}`,{method:'PUT',body:data}),deletePrato:id=>requestApi(`/pratos/${id}`,{method:'DELETE'}),ficha:id=>requestApi(`/pratos/${id}/ficha`),saveFicha:(id,ingredientes)=>requestApi(`/pratos/${id}/ficha`,{method:'PUT',body:{ingredientes}}),
 pedidos:()=>requestApi('/pedidos'),createPedido:data=>requestApi('/pedidos',{method:'POST',body:data}),changeStatus:(id,status)=>requestApi(`/pedidos/${id}/status`,{method:'PATCH',body:{status}}),changeTempo:(id,tempo_estimado)=>requestApi(`/pedidos/${id}/tempo`,{method:'PATCH',body:{tempo_estimado}}),
 ingredientes:()=>requestApi('/ingredientes'),createIngrediente:data=>requestApi('/ingredientes',{method:'POST',body:data}),updateIngrediente:(id,data)=>requestApi(`/ingredientes/${id}`,{method:'PATCH',body:data}),
 usuarios:()=>requestApi('/usuarios'),createUsuario:data=>requestApi('/usuarios',{method:'POST',body:data}),changeUsuario:(id,ativo)=>requestApi(`/usuarios/${id}`,{method:'PATCH',body:{ativo}}),
 bancadas:()=>requestApi('/bancadas'),createBancada:data=>requestApi('/bancadas',{method:'POST',body:data}),changeBancada:(id,ativa)=>requestApi(`/bancadas/${id}`,{method:'PATCH',body:{ativa}}),
 agendamentos:()=>requestApi('/agendamentos'),createAgendamento:data=>requestApi('/agendamentos',{method:'POST',body:data}),cancelAgendamento:id=>requestApi(`/agendamentos/${id}/cancelar`,{method:'PATCH',body:{}}),relatorios:()=>requestApi('/relatorios')
};
