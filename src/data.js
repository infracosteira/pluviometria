const STATUS_ON_DECK = { id: 1, name: "On Deck", color: "blue.300" };
const STATUS_IN_PROGRESS = { id: 2, name: "In Progress", color: "yellow.400" };
const STATUS_TESTING = { id: 3, name: "Testing", color: "pink.300" };
const STATUS_DEPLOYED = { id: 4, name: "Deployed", color: "green.300" };

export const STATUSES = [
  STATUS_ON_DECK,
  STATUS_IN_PROGRESS,
  STATUS_TESTING,
  STATUS_DEPLOYED,
];

// Função para buscar e processar dados do arquivo JS no GitHub
async function fetchDataFromGitHub() {
  try {
    const response = await fetch('https://raw.githubusercontent.com/infracosteira/pluviometria/refs/heads/main/data/data.js');
    
    if (!response.ok) {
      throw new Error(`Erro ao buscar dados: ${response.statusText}`);
    }

    const scriptText = await response.text();
    
    // Criar um elemento <script> para avaliar o código JS e obter os dados
    const scriptElement = document.createElement('script');
    scriptElement.textContent = scriptText;
    document.body.appendChild(scriptElement);

    // A variável DATA deve estar disponível globalmente no arquivo .data.js
    if (typeof DATA !== 'undefined') {
      console.log(DATA);
      preencherTabela(DATA);
    } else {
      console.error('A variável DATA não foi encontrada no arquivo.');
    }
  } catch (error) {
    console.error('Erro ao carregar os dados:', error);
  }
}

// Função para preencher a tabela com os dados
function preencherTabela(data) {
  data.forEach((item) => {
    console.log(`Nome Município: ${item.Nome_Municipio}, Precipitação Média Anual: ${item.Precipitacao_media_anual}`);
    // Adicione o código para preencher sua tabela HTML com os dados recebidos
  });
}

// Chamar a função para buscar os dados quando a página for carregada
fetchDataFromGitHub();
