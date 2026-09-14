const formulario = document.getElementById("formulario");

function checarRequisitosSenha(senha) {
  const erros = [];

  if (!/[A-Z]/.test(senha)) erros.push("Falta uma letra maiúscula");
  if (!/[0-9]/.test(senha)) erros.push("Falta um número");
  if (!/[^a-zA-Z0-9]/.test(senha)) erros.push("Falta um caractere especial");

  return {erros: erros};
}

formulario.addEventListener("submit", function(event) {
    event.preventDefault();

    const nome = document.getElementById("nome").value.trim();
    const email = document.getElementById("email").value.trim();
    const senha = document.getElementById("senha").value.trim();

    let erros = [];

    if (nome === "" || email === "" || senha === "") {
        erros.push("Preencha todos os campos!");
    } else {
        if (nome.length < 4) {
            erros.push("Nome muito curto!");
        }
        if (!email.includes("@")) {
            erros.push("Digite um e-mail válido!");
        }
        if (senha.length < 8) {
            erros.push("Senha muito pequena (mínimo 8 caracteres)!");
        }

        const requisitosSenha = checarRequisitosSenha(senha);
        erros = erros.concat(requisitosSenha.erros);
    }

    if (erros.length > 0) {
        alert(erros.join("\n"));
        return;
    } else{
        alert("Formulário enviado com sucesso!");
        formulario.reset();
    }

});