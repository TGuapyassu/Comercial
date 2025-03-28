document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('cadastroForm');
    const cepInput = document.getElementById('cep');

    // Função para gerar número aleatório de 7 dígitos
    function gerarNumeroAleatorio() {
        return Math.floor(Math.random() * 9000000 + 1000000).toString();
    }

    // Função para buscar CEP
    async function buscarCEP(cep) {
        try {
            const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
            const data = await response.json();
            
            if (data.erro) {
                throw new Error('CEP não encontrado');
            }

            document.getElementById('logradouro').value = data.logradouro;
            document.getElementById('endereco').value = data.logradouro;
            document.getElementById('bairro').value = data.bairro;
            document.getElementById('cidade').value = data.localidade;
            document.getElementById('estado').value = data.uf;
        } catch (error) {
            alert('Erro ao buscar CEP: ' + error.message);
        }
    }

    // Evento para buscar CEP quando o campo perder o foco
    cepInput.addEventListener('blur', function() {
        const cep = this.value.replace(/\D/g, '');
        if (cep.length === 8) {
            buscarCEP(cep);
        }
    });

    // Evento de submit do formulário
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Gera o código com base nas regras
        const numeroAleatorio = gerarNumeroAleatorio();
        const letraCategoria = document.getElementById('categoria').value;
        const codigoRegra = document.getElementById('regra_comissao').value;
        
        data.codigo = `${numeroAleatorio}${letraCategoria}${codigoRegra}`;

        try {
            const response = await fetch('/api/cadastro', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                alert(`Cadastro realizado com sucesso!\nCódigo gerado: ${data.codigo}`);
                form.reset();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            alert('Erro ao salvar: ' + error.message);
        }
    });
}); 