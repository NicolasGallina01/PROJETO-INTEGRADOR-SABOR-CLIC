const cardapio = [
    {
        id: 1,
        nome: "Hambúrguer",
        preco: 25.00,
        descricao: "Hambúrguer artesanal com queijo e salada."
    },
    {
        id: 2,
        nome: "Pizza",
        preco: 40.00,
        descricao: "Pizza de queijo com molho de tomate."
    },
    {
        id: 3,
        nome: "Batata Frita",
        preco: 15.00,
        descricao: "Porção de batatas fritas crocantes."
    },
    {
        id: 4,
        nome: "Refrigerante",
        preco: 8.00,
        descricao: "Refrigerante gelado de 350ml."
    }
];

let carrinho = [];

const Cardapio = document.getElementById("cardapio");
const totalCarrinho = document.getElementById("total");
const listaCarrinho = document.getElementById("carrinho");

function mostrarCardapio() {

    Cardapio.innerHTML = "";

    cardapio.forEach(function(produto) {

        const card = document.createElement("div");

        card.innerHTML = `
            <h3>${produto.nome}</h3>
            <p>${produto.descricao}</p>
            <p>Preço: R$ ${produto.preco.toFixed(2)}</p>

            <button onclick="adicionarCarrinho(${produto.id})">
                Adicionar ao Carrinho
            </button>
        `;

        Cardapio.appendChild(card);
    });
}

function adicionarCarrinho(id){
    const produto = cardapio.find(function(item){return item.id === id;})
    if (produto){
        carrinho.push(produto);
        atualizarCarrinhoHTML();
    }
}

function removerCarrinho(id){
    carrinho.splice(id, 1);
    atualizarCarrinhoHTML();
}

function calcularTotal(){
    let total = 0.00;

    carrinho.forEach(function(produto){
        total += produto.preco;
    });

    totalCarrinho.textContent = `Total: R$ ${total.toFixed(2)}`;
}

function atualizarCarrinhoHTML(){
    listaCarrinho.innerHTML = "";
    
    carrinho.forEach(function(produto, indice){
        const item = document.createElement("div");

        item.innerHTML = `
            <span>${produto.nome} - R$ ${produto.preco.toFixed(2)}</span>

            <button onclick="removerCarrinho(${indice})">
                Remover
            </button>
        `;

        listaCarrinho.appendChild(item);
    });
    calcularTotal();
}

mostrarCardapio();
atualizarCarrinhoHTML();