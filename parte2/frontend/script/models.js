/* POO ES6+: encapsulamento, herança, método estático e estado do carrinho. */
export class Usuario {
  #id; #nome; #cargo;
  constructor({id,nome,cargo}) { this.#id=Number(id); this.#nome=String(nome); this.#cargo=String(cargo); }
  get id() { return this.#id; } get nome() { return this.#nome; } get cargo() { return this.#cargo; }
  static fromApi(data) { return new Usuario(data); }
}
export class Cliente extends Usuario { get inicio() {return 'index.html';} }
export class Cozinheiro extends Usuario { get inicio() {return 'cozinheiro.html';} }
export class Administrador extends Usuario { get inicio() {return 'admin-cardapio.html';} }
export class Prato {
  #id;#nome;#categoria;#preco;#desc;#img;#ativo;
  constructor(data) { this.#id=Number(data.id); this.#nome=String(data.nome); this.#categoria=String(data.categoria);
    this.#preco=Number(data.preco);this.#desc=String(data.desc??'');this.#img=String(data.img??'');this.#ativo=Boolean(data.ativo); }
  get id(){return this.#id;} get nome(){return this.#nome;} get categoria(){return this.#categoria;}
  get preco(){return this.#preco;} get desc(){return this.#desc;} get img(){return this.#img;} get ativo(){return this.#ativo;}
  toJSON(){return {id:this.#id,nome:this.#nome,categoria:this.#categoria,preco:this.#preco,desc:this.#desc,img:this.#img};}
}
export class ItemPedido {
  #prato;#quantidade;
  constructor(prato, quantidade=1){this.#prato=prato;this.quantidade=quantidade;}
  get prato(){return this.#prato;} get quantidade(){return this.#quantidade;}
  set quantidade(value){const n=Number(value);if(!Number.isInteger(n)||n<1||n>50)throw Error('Use entre 1 e 50 unidades.');this.#quantidade=n;}
  subtotal(){return this.#prato.preco*this.#quantidade;}
  toJSON(){return {prato:this.#prato.toJSON(),quantidade:this.#quantidade};}
}
export class Carrinho {
  #itens=[];
  constructor(items=[]){for(const item of items){try{this.adicionar(new Prato(item.prato),Number(item.quantidade));}catch(_){/* registro inválido descartado */}}}
  adicionar(prato,quantidade=1){if(!Number.isInteger(quantidade)||quantidade<1)throw Error('Quantidade inválida.');const item=this.#itens.find(x=>x.prato.id===prato.id);
    if(item)item.quantidade=item.quantidade+quantidade;else this.#itens.push(new ItemPedido(prato,quantidade));}
  alterar(id,delta){const item=this.#itens.find(x=>x.prato.id===Number(id));if(!item)return;const nova=item.quantidade+delta;if(nova<1){this.remover(id);return;}item.quantidade=nova;}
  remover(id){this.#itens=this.#itens.filter(x=>x.prato.id!==Number(id));}
  limpar(){this.#itens=[];} get itens(){return [...this.#itens];}
  get total(){return this.#itens.reduce((sum,x)=>sum+x.subtotal(),0);}
  get quantidade(){return this.#itens.reduce((sum,x)=>sum+x.quantidade,0);}
  toJSON(){return this.#itens.map(x=>x.toJSON());}
  toPedido(){return this.#itens.map(x=>({prato_id:x.prato.id,quantidade:x.quantidade}));}
  static carregar(userId){try{return new Carrinho(JSON.parse(sessionStorage.getItem(`saborclic_cart_${userId}`)||'[]'));}catch(_){return new Carrinho();}}
  salvar(userId){sessionStorage.setItem(`saborclic_cart_${userId}`,JSON.stringify(this.toJSON()));}
}
export class Pedido {
  #id;#status;#itens;#total;
  constructor(data){this.#id=Number(data.id);this.#status=data.status;this.#itens=[...(data.itens??[])];this.#total=Number(data.total);}
  get id(){return this.#id;} get status(){return this.#status;} get itens(){return [...this.#itens];}get total(){return this.#total;}
  static labels(){return {aguardando:'Aguardando',em_preparo:'Em preparo',pronto:'Pronto para entrega',entregue:'Entregue',cancelado:'Cancelado'};}
}
