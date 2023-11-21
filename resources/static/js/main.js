const inputs = document.querySelectorAll('.barra-pesquisa');
const suggestionsTable = document.querySelector('tbody');
let pokemonList = [];
let sprites = []
let teamWeaknesses = []
document.addEventListener('DOMContentLoaded', function () {
    const inputs = document.querySelectorAll('.barra-pesquisa');

    inputs.forEach(function (input) {
        $(input).autoComplete({
            minChars: 1,
            source: function (term, suggest) {
                term = term.toLowerCase();
                var matches = [];
                for (var i = 0; i < sprites.length; i++) {
                    var pokemon = sprites[i]['Pokémon'];
                    if (pokemon.toLowerCase().indexOf(term) !== -1) {
                        matches.push(pokemon);
                    }
                }
                suggest(matches);
            },
            renderItem: function (item, search) {
                search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                var re = new RegExp('(' + search.split(' ').join('|') + ')', 'gi');
                return '<div class="autocomplete-suggestion" data-val="' + item + '">' + item.replace(re, '<strong>$1</strong>') + '</div>';
            },
            onSelect: function (event, term, item) {
                var nextElement = item.closest('.conjunto-slots').nextElementSibling;
                if (nextElement) {
                    var barraPesquisa = nextElement.querySelector('.barra-pesquisa');
                    if (barraPesquisa && pokemonList.length !== 6) {
                        enableNextInput(barraPesquisa);
                    }
                }
                $(this).autoComplete('hide');
            },
            onRender: function (container) {
                var input = this.element;
                var inputPosition = input.getBoundingClientRect();
                container.style.width = inputPosition.width + 'px';
                container.style.left = inputPosition.left + 'px';
                container.style.top = (inputPosition.top + inputPosition.height) + 'px';
                container.style.display = input.value.trim() !== '' ? 'block' : 'none';
                container.parentElement.style.position = 'relative'; // Define o posicionamento relativo para o elemento pai
                container.parentElement.style.zIndex = 9999; // Define um índice z para sobrepor outros elementos
                container.parentElement.appendChild(container);
            },
        });
    });

});

inputs.forEach((input, index) => {
    if (index > 0) {
        input.setAttribute('readonly', 'readonly');
    }
    if (index === inputs.length - 1) {
        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === 'Tab') {
                handleInputChange(event);
            }
        });
    } else {
        input.addEventListener('change', handleInputChange);
    }
});

// Carregar os resultados armazenados no sessionStorage ao recarregar a página
window.addEventListener('DOMContentLoaded', loadResultsFromSessionStorage);
window.addEventListener('DOMContentLoaded', fetchSprites());
document.addEventListener("touchstart", function() {}, true);
document.querySelector('#clear-button').addEventListener('click', function () {
    // Limpar o sessionStorage
    sessionStorage.clear();
    // Remover o #container-sugestoes da página
    hiddenSuggestions();
    resetInputs();
    resetSlots();
    pokemonList = [];
});

async function fetchSprites() {
    const response = await fetch('https://gilliardrodrigues.pythonanywhere.com/sprites', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json, charset=utf-8',
        },
    });

    sprites = await response.json();
}

function enableNextInput(currentInput) {
    const currentInputIndex = Array.from(inputs).indexOf(currentInput);
    const nextInput = inputs[currentInputIndex + 1];
    nextInput.removeAttribute('readonly');
    nextInput.placeholder = 'Insira sua escolha.';
    nextInput.focus();
}

function resetInputs() {
    inputs.forEach((input, index) => {
        if (index === 0) {
            input.removeAttribute('readonly');
            input.value = '';
        } else {
            input.setAttribute('readonly', 'readonly');
            input.value = ''
            input.placeholder = ''
        }
    });
}

async function makeRequest(pokemonList, teamWeaknesses, event) {
    const response = await fetch('https://gilliardrodrigues.pythonanywhere.com/suggestions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify({ team: pokemonList }),
    });

    const data = await response.json();
    const suggestions = Array.isArray(data) ? data : [data];

    // Ordenando as sugestões pela confiança em ordem decrescente, pegando o valor máximo de cada linha:
    suggestions.sort(function(a, b) {
        // Verificar se 'Confiança' é um array ou um valor único
        const confA = Array.isArray(a.Confiança) ? a.Confiança : [a.Confiança];
        const confB = Array.isArray(b.Confiança) ? b.Confiança : [b.Confiança];
        // Calcular a média das porcentagens ou usar o valor único, dependendo do caso
        const maxA = Math.max(...confA);
        const maxB = Math.max(...confB);
        // Comparar os valores máximos para ordenar em ordem decrescente
        return maxB - maxA;
    });

    const containerSugestoes = document.querySelector('#container-sugestoes');
    containerSugestoes.style.display = 'block';
    const tableBody = document.querySelector('tbody');
    const firstRow = tableBody.querySelector('tr:first-child');
    firstRow.style.display = 'table-row';
    // Selecionar as linhas a partir do segundo <tr>
    const rowsToRemove = tableBody.querySelectorAll('tr:not(:first-child)');

    // Remover as linhas selecionadas
    rowsToRemove.forEach((row) => {
        tableBody.removeChild(row);
    });

    if (suggestions.length === 1 && typeof suggestions[0] === 'string') {
        const rowToHidden = tableBody.querySelector('tr:first-child');
        rowToHidden.style.display = 'none';
        const noSuggestionsRow = tableBody.insertRow();
        const noSuggestionsCell = noSuggestionsRow.insertCell();
        noSuggestionsCell.colSpan = 5;
        noSuggestionsCell.textContent = suggestions[0];
    }
    else {
        suggestions.forEach((suggestion, index) => {

            const row = tableBody.insertRow();
            row.classList.add('linha');
            row.innerHTML = `
            <td><img class="sprite" src="${suggestion.Sprite}" alt="${suggestion.Pokémon}"></td>
            <td>${suggestion.Pokémon}</td>
            <td><img class="type" src="${suggestion['1º tipo']}" alt="${suggestion.Pokémon}">
            ${suggestion['2º tipo'] !== '-' ?
                    `<img class="type" src="${suggestion['2º tipo']}" alt="${suggestion.Pokémon}">` : ''}</td>
            <td class="tooltip">
                Visualizar
                <span class="tooltip-text">
                    Freq. utilizado com: <br>${formatAntecedents(suggestion['Freq. utilizado com'])}
                    <br>
                    Confiança (%): <br>${formatMetricValue(suggestion.Confiança)}
                </span>
            </td>
            <td class="tooltip">
                Visualizar
                <span class="tooltip-text">
                    Freq. utilizado com: <br>${formatAntecedents(suggestion['Freq. utilizado com'])}
                    <br>
                    Lift: <br>${formatMetricValue(suggestion.Lift)}
                </span>
            </td>
            <td>
                ${buildChoiceAdvantagesImgsHTML(parseChoiceAdvantage(suggestion["É um reforço contra"][0]))}
            </td>`;

            if (!data[data.length - 1].hasOwnProperty("Confiança")) {
                teamWeaknesses = data.pop()['Fraquezas']; // Armazena a lista de fraquezas atuais .
            }
        });
    }
    const pokemon = pokemonList[pokemonList.length - 1];
    const currentInput = event.target;

    fillSlot(currentInput, pokemon);

    // Armazenar os resultados no sessionStorage
    sessionStorage.setItem('suggestions', JSON.stringify(suggestions));

    let weaknessesContainer = document.getElementById('team-weaknesses');
    if (!weaknessesContainer) {
        weaknessesContainer = document.createElement('div');
        weaknessesContainer.id = 'team-weaknesses';
        const containerSlots = document.getElementById('container-slots');
        containerSlots.appendChild(weaknessesContainer);
    }

    weaknessesContainer.innerHTML = ''; // Limpar o conteúdo anterior
    if (teamWeaknesses.length) {
        const weaknessesTitle = document.createElement('h3');
        weaknessesTitle.textContent = 'Fraquezas da equipe:';
        weaknessesContainer.appendChild(weaknessesTitle);

        teamWeaknesses.forEach(weakness => {
            const typeImg = document.createElement('img');
            typeImg.src = `https://play.pokemonshowdown.com/sprites/types/${capitalizeFirstLetter(weakness)}.png`;
            typeImg.style.marginTop = '5px';
            typeImg.style.marginRight = '5px';
            weaknessesContainer.appendChild(typeImg);
        });
    }
}

function fillSlot(currentInput, pokemon) {
    // Encontre o slot relevante com base no ID do input
    let slotElement = null;
    switch (currentInput.id) {
        case 'barra-1':
            slotElement = document.querySelector('#slot-1');
            break;
        case 'barra-2':
            slotElement = document.querySelector('#slot-2');
            break;
        case 'barra-3':
            slotElement = document.querySelector('#slot-3');
            break;
        case 'barra-4':
            slotElement = document.querySelector('#slot-4');
            break;
        case 'barra-5':
            slotElement = document.querySelector('#slot-5');
            break;
        case 'barra-6':
            slotElement = document.querySelector('#slot-6');
            break;
    }
    var spriteUrl = '';
    var type1 = '';
    var type2 = '';
    for (var i = 0; i < sprites.length; i++) {
        if (sprites[i]['Pokémon'] === pokemon) {
            spriteUrl = sprites[i].Sprite;
            type1 = sprites[i]['1º tipo'];
            type2 = sprites[i]['2º tipo'];
            break;
        }
    }
    if (spriteUrl !== '') {
        var divElement = document.createElement('div');
        divElement.classList.add('conteudo-slot');
        var imgElement = document.createElement('img');
        imgElement.src = spriteUrl;
        imgElement.style.width = "115px";
        imgElement.style.height = "115px";
        divElement.appendChild(imgElement);
        textElement = document.createElement('span');
        textElement.textContent = pokemon;
        textElement.classList.add('nomePokemonSlot');
        divElement.appendChild(textElement);
        type1Element = document.createElement('img');
        type1Element.src = type1;
        divElement.appendChild(type1Element);
        if (type2 != '-') {
            type2Element = document.createElement('img');
            type2Element.src = type2;
            divElement.appendChild(type2Element);
        }
        slotElement.replaceWith(divElement);
        currentInput.parentElement.style.opacity = 0;
        currentInput.parentElement.style.pointerEvents = "none";
    }
}

function handleInputChange(event) {

    const currentInput = event.target;
    const inputValue = currentInput.value.trim();
    if (inputValue !== '') {
        currentInput.setAttribute('readonly', 'readonly');
        pokemonList.push(inputValue);
        if (pokemonList.length < 6) {
            makeRequest(pokemonList, teamWeaknesses, event);
            enableNextInput(currentInput);
        }
        else {
            const pokemon = pokemonList[pokemonList.length - 1];
            fillSlot(currentInput, pokemon);
            document.querySelector(".conjunto-barras").style.padding = 0;
            hiddenSuggestions();
        }
    }
}

function renderResults(results) {
    const tableBody = document.querySelector('tbody');

    // Selecionar as linhas a partir do segundo <tr>
    const rowsToRemove = tableBody.querySelectorAll('tr:not(:first-child)');

    // Remover as linhas selecionadas
    rowsToRemove.forEach((row) => {
        tableBody.removeChild(row);
    });

    // Ordenar as sugestões pela confiança em ordem decrescente
    results.sort((a, b) => b.Confiança - a.Confiança);

    results.forEach((suggestion, index) => {
        const row = tableBody.insertRow();
        row.classList.add('linha');
        row.innerHTML = `
        <td><img class="sprite" src="${suggestion.Sprite}" alt="${suggestion.Pokémon}"></td>
        <td>${suggestion.Pokémon}</td>
        <td><img class="type" src="${suggestion['1º tipo']}" alt="${suggestion.Pokémon}">
        ${suggestion['2º tipo'] !== '-' ? `<img class="type" src="${suggestion['2º tipo']}" alt="${suggestion.Pokémon}">` : ''}</td>
        <td class="tooltip">
            Visualizar
            <span class="tooltip-text">
                Freq. utilizado com: <br>${formatAntecedents(suggestion['Freq. utilizado com'])}
                <br>
                Confiança (%): <br>${formatMetricValue(suggestion.Confiança)}
            </span>
        </td>
        <td class="tooltip">
            Visualizar
            <span class="tooltip-text">
                Freq. utilizado com: <br>${formatAntecedents(suggestion['Freq. utilizado com'])}
                <br>
                Lift: <br>${formatMetricValue(suggestion.Lift)}
            </span>
        </td>
        <td>
            ${buildChoiceAdvantagesImgsHTML(parseChoiceAdvantage(suggestion["É um reforço contra"][0]))}
        </td>`;
    });
}

function loadResultsFromSessionStorage() {
    const results = sessionStorage.getItem('suggestions');

    if (results) {
        const parsedResults = JSON.parse(results);
        renderResults(parsedResults);
    }
}

function hiddenSuggestions() {
    const containerSugestoes = document.querySelector('#container-sugestoes');
    containerSugestoes.style.display = 'none';
}

function resetSlots() {
    const slots = document.querySelectorAll('.conteudo-slot');
    const barrasPesquisa = document.querySelectorAll('.barra-pesquisa');
    const lupas = document.querySelectorAll('.lupa');
    const weaknessesContainer = document.getElementById('team-weaknesses');
    // Restaurar os slots para o estado inicial
    slots.forEach((slot, index) => {
        const slotElement = document.createElement('img');
        slotElement.classList.add('slot');
        slotElement.id = `slot-${index + 1}`;
        slotElement.src = '/static/img/slot.png';
        slot.replaceWith(slotElement);
    });

    // Restaurar os inputs e lupas para o estado inicial
    barrasPesquisa.forEach((barraPesquisa, index) => {
        if (index > 0) {
            barraPesquisa.parentElement.style.opacity = 1;
            barraPesquisa.parentElement.style.pointerEvents = 'auto';
        }
    });

    lupas.forEach((lupa) => {
        lupa.parentElement.style.opacity = 1;
        lupa.parentElement.style.pointerEvents = 'auto';
    });

    // Restaurar o estilo da seção
    document.querySelector('.conjunto-barras').style.padding = '0% 2% 2%;';
    weaknessesContainer.style.display = 'none';

}

function formatAntecedents(data) {
    return data.map(item => item.toString().replace(',', ', ')).join('<br>');
}

function formatMetricValue(data) {
    return data.map(item => item.toString().replace(',', ', ')).join(', ');
}
function parseChoiceAdvantage(choiceAdvantagesText) {
    return choiceAdvantagesText.split(', ');
}
function buildChoiceAdvantagesImgsHTML(choiceAdvantagesList) {
    let html = '';
    if (hasChoiceAdvantages(choiceAdvantagesList)) {
        choiceAdvantagesList.forEach(type => html += `<img class='choiceAdvantages' src='https://play.pokemonshowdown.com/sprites/types/${capitalizeFirstLetter(type)}.png' alt='${capitalizeFirstLetter(type)}'>`);
    }
    return html;
}
function hasChoiceAdvantages(choiceAdvantagesList) {
    return choiceAdvantagesList[0] !== '';
}
function capitalizeFirstLetter(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}