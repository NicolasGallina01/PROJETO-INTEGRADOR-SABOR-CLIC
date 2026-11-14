let csrfToken='';
export const setCsrf=token=>{csrfToken=token||'';};
async function remote(path,method,body){
 const response=await fetch('/api'+path,{method,credentials:'same-origin',headers:{'Content-Type':'application/json','X-CSRF-Token':csrfToken},...(method==='GET'?{}:{body:JSON.stringify(body)})});
 const data=await response.json();
 if(!response.ok)throw Error(data.erro?.mensagem||'Falha na API.');
 if(data.csrf)csrfToken=data.csrf;
 return data;
}
export async function requestApi(path,{method='GET',body={}}={}){
 return remote(path,method,body);
}
export const api={
 pagamentos:()=>requestApi('/pagamentos'),confirmarPagamento:(id,forma_pagamento)=>requestApi(`/pagamentos/${id}/confirmar`,{method:'PATCH',body:{forma_pagamento}}),
 me:()=>requestApi('/auth/me'),login:data=>requestApi('/auth/login',{method:'POST',body:data}),register:data=>requestApi('/auth/registro',{method:'POST',body:data}),logout:()=>requestApi('/auth/logout',{method:'POST'}),
 pratos:()=>requestApi('/pratos'),createPrato:data=>requestApi('/pratos',{method:'POST',body:data}),updatePrato:(id,data)=>requestApi(`/pratos/${id}`,{method:'PUT',body:data}),deletePrato:id=>requestApi(`/pratos/${id}`,{method:'DELETE'}),ficha:id=>requestApi(`/pratos/${id}/ficha`),saveFicha:(id,ingredientes)=>requestApi(`/pratos/${id}/ficha`,{method:'PUT',body:{ingredientes}}),
 pedidos:()=>requestApi('/pedidos'),createPedido:data=>requestApi('/pedidos',{method:'POST',body:data}),changeStatus:(id,status)=>requestApi(`/pedidos/${id}/status`,{method:'PATCH',body:{status}}),changeTempo:(id,tempo_estimado)=>requestApi(`/pedidos/${id}/tempo`,{method:'PATCH',body:{tempo_estimado}}),
 ingredientes:()=>requestApi('/ingredientes'),createIngrediente:data=>requestApi('/ingredientes',{method:'POST',body:data}),updateIngrediente:(id,data)=>requestApi(`/ingredientes/${id}`,{method:'PATCH',body:data}),
 usuarios:()=>requestApi('/usuarios'),createUsuario:data=>requestApi('/usuarios',{method:'POST',body:data}),changeUsuario:(id,ativo)=>requestApi(`/usuarios/${id}`,{method:'PATCH',body:{ativo}}),
 bancadas:()=>requestApi('/bancadas'),createBancada:data=>requestApi('/bancadas',{method:'POST',body:data}),changeBancada:(id,ativa)=>requestApi(`/bancadas/${id}`,{method:'PATCH',body:{ativa}}),
 agendamentos:()=>requestApi('/agendamentos'),createAgendamento:data=>requestApi('/agendamentos',{method:'POST',body:data}),cancelAgendamento:id=>requestApi(`/agendamentos/${id}/cancelar`,{method:'PATCH',body:{}}),relatorios:()=>requestApi('/relatorios')
};
