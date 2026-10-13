# origem-recomendador

Mockup do **Módulo de Recomendação de Produtos** do **Origem**, implementado em [BentoML](https://www.bentoml.com/) (AV1, Inteligência Artificial Aplicada).

O Origem é uma plataforma que conecta artesãos e produtores criativos a compradores. O módulo de recomendação sugere peças artesanais nas páginas inicial e de produto, combinando **similaridade** (mesma técnica e mesmo polo de origem), **popularidade** (vendas e visualizações) e **disponibilidade** (estoque e publicação).

Este mockup implementa o caminho feliz da especificação da AV1, que está em [`docs/`](docs/):

- [`product.md`](docs/product.md): problema, público e objetivo do módulo
- [`requirements.md`](docs/requirements.md): requisitos funcionais (RF) e não funcionais (RNF)
- [`design.md`](docs/design.md): arquitetura, regra de recomendação e contrato da API

## Equipe

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/elistenorio">
        <img src="https://github.com/elistenorio.png" width="100px;" alt="Foto de elistenorio"/><br/>
        <sub><b>Elis Tenório</b></sub><br/>
        <sub>@elistenorio</sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/netokemon">
        <img src="https://github.com/netokemon.png" width="100px;" alt="Foto de netokemon"/><br/>
        <sub><b>Aguinaldo Neto</b></sub><br/>
        <sub>@netokemon</sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/eulalialbuquerque">
        <img src="https://github.com/eulalialbuquerque.png" width="100px;" alt="Foto de eulalialbuquerque"/><br/>
        <sub><b>Eulália Albuquerque</b></sub><br/>
        <sub>@eulalialbuquerque</sub>
      </a>
    </td>
  </tr>
</table>

## Estrutura do repositório

```
├── dados/
│   └── catalogo.json    # catálogo de peças
├── docs/                # especificação da AV1
├── service.py           # serviço BentoML
├── pyproject.toml       # dependências
├── uv.lock              # versões travadas
├── .python-version      # versão do Python (3.13)
├── README.md
└── LICENSE
```

## Pré-requisitos

- [Git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/), gerenciador de projetos Python. Ele baixa sozinho o Python 3.13 usado no projeto.

## Instalação

```bash
git clone https://github.com/elistenorio/origem-recomendador.git
cd origem-recomendador
uv sync
```

O `uv sync` cria o ambiente virtual e instala exatamente as versões travadas no `uv.lock`.

## Como subir o serviço

```bash
uv run bentoml serve service:RecomendadorOrigem
```

Espere a mensagem `Service RecomendadorOrigem initialized`. O serviço fica disponível em `http://localhost:3000` enquanto o terminal estiver aberto (para parar: `Ctrl + C`).

Abrindo `http://localhost:3000` no navegador, aparece a documentação interativa (Swagger), onde também dá para testar o endpoint pelo botão **Try it out**.

## Contrato da API

### `POST /v1/recomendacoes`

**Entrada** (corpo JSON):

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `sessao_id` | texto | Sim | Identificador da sessão do comprador |
| `contexto` | texto | Sim | `"pagina_inicial"` ou `"pagina_produto"` |
| `peca_referencia_id` | texto | Não | Peça que o comprador está vendo. Se não existir no catálogo, a similaridade é ignorada (não é erro) |
| `limite` | inteiro | Não | Quantas peças devolver. Padrão 10, máximo 50, mínimo 1 |

**Saída** (200 OK):

| Campo | Descrição |
|---|---|
| `recomendacao_id` | Identificador único da recomendação (muda a cada chamada) |
| `estrategia` | Estratégia usada. No mockup é sempre `"cold_start"`, pois não há histórico de comprador |
| `contexto` | O mesmo valor recebido |
| `gerado_em` | Data e hora da geração, em UTC (muda a cada chamada) |
| `itens` | Lista ordenada de peças |
| `itens[].peca_id` | Identificador da peça no catálogo |
| `itens[].posicao` | Posição na lista, a partir de 1 |
| `itens[].pontuacao` | Pontuação de 0 a 1 |
| `itens[].criterios` | O que contribuiu para a peça entrar: `"similaridade"` e/ou `"popularidade"` |

**Erros:** campo obrigatório ausente, tipo inválido, `contexto` fora dos valores permitidos ou `limite` menor que 1 retornam **400**, indicando o campo com problema (formato padrão do BentoML).

## Como a recomendação funciona

Regra da AV1 (`design.md`, seções 4.1 e 4.2):

1. **Filtra** peças esgotadas (`estoque` 0), despublicadas e a própria peça de referência.
2. **Popularidade** de cada peça: `ln(1 + 5 × vendas + visualizações) ÷ ln(1 + maior valor do catálogo)`, de 0 a 1.
3. **Similaridade** com a peça de referência: 1,0 (mesma técnica e mesmo polo), 0,7 (mesma técnica, outro polo) ou 0.
4. **Pontuação:** com peça de referência, `0,7 × similaridade + 0,3 × popularidade`; sem referência, só a popularidade.
5. **Ordena** primeiro pelo grupo de similaridade e, dentro de cada grupo, pela pontuação.
6. **Corta** a lista no `limite` pedido.

## Tabela RF → endpoint

| Requisito da AV1 | Situação no mockup | Onde |
|---|---|---|
| **RF-01** Similaridade (técnica e polo) | ✅ Implementado | `POST /v1/recomendacoes`: funções `buscar_peca` e `calcular_similaridade` |
| **RF-02** Popularidade | ✅ Implementado (contagens dos últimos 30 dias simuladas no catálogo) | `POST /v1/recomendacoes`: função `calcular_popularidades` |
| **RF-03** Histórico do comprador | ❌ Fora do escopo (trabalho futuro) | — |
| **RF-04** Cold start | 🟡 Parcial: sem histórico, toda resposta usa a estratégia `cold_start` | `POST /v1/recomendacoes`: método `recomendar` |
| **RF-05** Exclusão de peças indisponíveis | ✅ Implementado (catálogo lido a cada requisição) | `POST /v1/recomendacoes`: método `recomendar` |
| **RF-06** Quantidade configurável | ✅ Implementado (padrão 10, máximo 50) | `POST /v1/recomendacoes`: campo `limite` |
| **RF-07** Interface de integração | ✅ Implementado | `POST /v1/recomendacoes` |
| **RF-08** Registro das recomendações | ❌ Fora do escopo | — |
| **RF-09** Registro de interações | ❌ Fora do escopo (trabalho futuro) | — |
| **RNF-01 a RNF-05** | ❌ Fora do escopo do mockup | — |

## Catálogo

O catálogo fica em [`dados/catalogo.json`](dados/catalogo.json). Os nomes e números são fictícios; as técnicas e os polos são tradições reais do artesanato pernambucano. `vendas_janela` e `visualizacoes_janela` simulam as contagens dos últimos 30 dias.

| `peca_id` | Nome | Técnica | Polo | Estoque | Publicada | Vendas | Visualizações | Popularidade |
|---|---|---|---|---|---|---|---|---|
| p-01 | Lampião e Maria Bonita | Cerâmica | Caruaru | 5 | sim | 40 | 350 | 0,94 |
| p-02 | Trio de forró | Cerâmica | Caruaru | 3 | sim | 12 | 150 | 0,80 |
| p-03 | Bumba meu boi | Cerâmica | Caruaru | 2 | sim | 0 | 0 | 0,00 |
| p-04 | Conjunto Maracatu | Cerâmica | Caruaru | 4 | sim | 20 | 210 | 0,86 |
| p-05 | São Francisco de Assis | Cerâmica | Tracunhaém | 6 | sim | 26 | 250 | 0,89 |
| p-06 | Santo Antônio | Cerâmica | Tracunhaém | 2 | sim | 5 | 90 | 0,71 |
| p-07 | Toalha de mesa redonda | Renda renascença | Poção | **0** | sim | 60 | 500 | 1,00 |
| p-08 | Caminho de mesa | Renda renascença | Poção | 3 | **não** | 32 | 300 | 0,92 |
| p-09 | Centro de mesa | Renda renascença | Poção | 4 | sim | 15 | 180 | 0,83 |
| p-10 | Jogo americano | Renda renascença | Poção | 5 | sim | 7 | 105 | 0,74 |
| p-11 | Toalha de bandeja | Renda renascença | Pesqueira | 3 | sim | 9 | 125 | 0,77 |
| p-12 | Gravura Festa de São João | Xilogravura | Bezerros | 10 | sim | 52 | 400 | 0,97 |
| p-13 | Boneco de mamulengo | Entalhe em madeira | Glória do Goitá | 8 | sim | 3 | 80 | 0,68 |
| p-14 | Bata bordada | Bordado manual | Passira | 7 | sim | 2 | 65 | 0,65 |

São 12 peças disponíveis. A p-07 está esgotada e a p-08 está despublicada.

## Casos de teste

Com o serviço rodando, execute cada comando em **outro terminal**. Os comandos usam `curl` em Linux, macOS ou Git Bash (Windows); veja a [nota para o PowerShell](#windows-powershell) abaixo.

A resposta do serviço vem em uma linha só. Os campos `recomendacao_id` e `gerado_em` mudam a cada chamada; todo o resto deve ser igual ao esperado.

### Teste 1: página inicial, visitante sem histórico (RF-02, RF-04, RF-05, RF-06)

```bash
curl -X POST http://localhost:3000/v1/recomendacoes \
  -H "Content-Type: application/json" \
  -d '{"sessao_id": "s-001", "contexto": "pagina_inicial"}'
```

**Resultado esperado:** estratégia `cold_start` e **10 itens** (o padrão) das 12 peças disponíveis, em ordem de popularidade.

| Posição | Peça | Pontuação | Critérios |
|---|---|---|---|
| 1 | p-12 Gravura Festa de São João | 0.97 | popularidade |
| 2 | p-01 Lampião e Maria Bonita | 0.94 | popularidade |
| 3 | p-05 São Francisco de Assis | 0.89 | popularidade |
| 4 | p-04 Conjunto Maracatu | 0.86 | popularidade |
| 5 | p-09 Centro de mesa | 0.83 | popularidade |
| 6 | p-02 Trio de forró | 0.8 | popularidade |
| 7 | p-11 Toalha de bandeja | 0.77 | popularidade |
| 8 | p-10 Jogo americano | 0.74 | popularidade |
| 9 | p-06 Santo Antônio | 0.71 | popularidade |
| 10 | p-13 Boneco de mamulengo | 0.68 | popularidade |

**O que conferir:** a p-07 (a mais popular do catálogo, mas esgotada) e a p-08 (despublicada) não aparecem. As 2 peças disponíveis menos populares (p-14 e p-03) ficam de fora pelo limite padrão de 10.

<details>
<summary>JSON completo esperado</summary>

```json
{
  "recomendacao_id": "rec-xxxxxxxx",
  "estrategia": "cold_start",
  "contexto": "pagina_inicial",
  "gerado_em": "AAAA-MM-DDTHH:MM:SS+00:00",
  "itens": [
    {"peca_id": "p-12", "posicao": 1, "pontuacao": 0.97, "criterios": ["popularidade"]},
    {"peca_id": "p-01", "posicao": 2, "pontuacao": 0.94, "criterios": ["popularidade"]},
    {"peca_id": "p-05", "posicao": 3, "pontuacao": 0.89, "criterios": ["popularidade"]},
    {"peca_id": "p-04", "posicao": 4, "pontuacao": 0.86, "criterios": ["popularidade"]},
    {"peca_id": "p-09", "posicao": 5, "pontuacao": 0.83, "criterios": ["popularidade"]},
    {"peca_id": "p-02", "posicao": 6, "pontuacao": 0.8, "criterios": ["popularidade"]},
    {"peca_id": "p-11", "posicao": 7, "pontuacao": 0.77, "criterios": ["popularidade"]},
    {"peca_id": "p-10", "posicao": 8, "pontuacao": 0.74, "criterios": ["popularidade"]},
    {"peca_id": "p-06", "posicao": 9, "pontuacao": 0.71, "criterios": ["popularidade"]},
    {"peca_id": "p-13", "posicao": 10, "pontuacao": 0.68, "criterios": ["popularidade"]}
  ]
}
```

</details>

### Teste 2: página de produto, peças similares (RF-01, RF-02)

O comprador está vendo a **p-04 Conjunto Maracatu** (Cerâmica, Caruaru).

```bash
curl -X POST http://localhost:3000/v1/recomendacoes \
  -H "Content-Type: application/json" \
  -d '{"sessao_id": "s-002", "contexto": "pagina_produto", "peca_referencia_id": "p-04"}'
```

**Resultado esperado:** as peças aparecem em três grupos de similaridade.

| Posição | Peça | Grupo | Pontuação | Critérios |
|---|---|---|---|---|
| 1 | p-01 Lampião e Maria Bonita | Mesma técnica e mesmo polo (Cerâmica, Caruaru) | 0.98 | similaridade, popularidade |
| 2 | p-02 Trio de forró | Mesma técnica e mesmo polo | 0.94 | similaridade, popularidade |
| 3 | p-03 Bumba meu boi | Mesma técnica e mesmo polo | 0.7 | similaridade |
| 4 | p-05 São Francisco de Assis | Mesma técnica, outro polo (Tracunhaém) | 0.76 | similaridade, popularidade |
| 5 | p-06 Santo Antônio | Mesma técnica, outro polo | 0.7 | similaridade, popularidade |
| 6 | p-12 Gravura Festa de São João | Técnica diferente | 0.29 | popularidade |
| 7 | p-09 Centro de mesa | Técnica diferente | 0.25 | popularidade |
| 8 | p-11 Toalha de bandeja | Técnica diferente | 0.23 | popularidade |
| 9 | p-10 Jogo americano | Técnica diferente | 0.22 | popularidade |
| 10 | p-13 Boneco de mamulengo | Técnica diferente | 0.2 | popularidade |

**O que conferir:**
- A própria p-04 não aparece na lista.
- A **p-03 (0.7) vem antes da p-05 (0.76)**, mesmo com pontuação menor. Isso é intencional: o RF-01 manda priorizar o mesmo polo, então a ordem segue primeiro o grupo de similaridade e só depois a pontuação.
- A p-03 não tem nenhuma venda (popularidade 0, critério só `similaridade`), mas continua elegível (RF-02) e aparece bem posicionada por ser parecida com a peça vista.

<details>
<summary>JSON completo esperado</summary>

```json
{
  "recomendacao_id": "rec-xxxxxxxx",
  "estrategia": "cold_start",
  "contexto": "pagina_produto",
  "gerado_em": "AAAA-MM-DDTHH:MM:SS+00:00",
  "itens": [
    {"peca_id": "p-01", "posicao": 1, "pontuacao": 0.98, "criterios": ["similaridade", "popularidade"]},
    {"peca_id": "p-02", "posicao": 2, "pontuacao": 0.94, "criterios": ["similaridade", "popularidade"]},
    {"peca_id": "p-03", "posicao": 3, "pontuacao": 0.7, "criterios": ["similaridade"]},
    {"peca_id": "p-05", "posicao": 4, "pontuacao": 0.76, "criterios": ["similaridade", "popularidade"]},
    {"peca_id": "p-06", "posicao": 5, "pontuacao": 0.7, "criterios": ["similaridade", "popularidade"]},
    {"peca_id": "p-12", "posicao": 6, "pontuacao": 0.29, "criterios": ["popularidade"]},
    {"peca_id": "p-09", "posicao": 7, "pontuacao": 0.25, "criterios": ["popularidade"]},
    {"peca_id": "p-11", "posicao": 8, "pontuacao": 0.23, "criterios": ["popularidade"]},
    {"peca_id": "p-10", "posicao": 9, "pontuacao": 0.22, "criterios": ["popularidade"]},
    {"peca_id": "p-13", "posicao": 10, "pontuacao": 0.2, "criterios": ["popularidade"]}
  ]
}
```

</details>

### Teste 3: página de produto com peças indisponíveis e limite 3 (RF-05, RF-06)

O comprador está vendo a **p-09 Centro de mesa** (Renda renascença, Poção) e o sistema pede só 3 peças.

```bash
curl -X POST http://localhost:3000/v1/recomendacoes \
  -H "Content-Type: application/json" \
  -d '{"sessao_id": "s-003", "contexto": "pagina_produto", "peca_referencia_id": "p-09", "limite": 3}'
```

**Resultado esperado:** exatamente **3 itens**.

| Posição | Peça | Grupo | Pontuação | Critérios |
|---|---|---|---|---|
| 1 | p-10 Jogo americano | Mesma técnica e mesmo polo (Renda renascença, Poção) | 0.92 | similaridade, popularidade |
| 2 | p-11 Toalha de bandeja | Mesma técnica, outro polo (Pesqueira) | 0.72 | similaridade, popularidade |
| 3 | p-12 Gravura Festa de São João | Técnica diferente | 0.29 | popularidade |

**O que conferir:** a p-07 (esgotada) e a p-08 (despublicada) têm a mesma técnica e o mesmo polo da referência e são as mais populares. Sem o filtro de disponibilidade, elas ocupariam as posições 1 e 2. Como estão indisponíveis, não aparecem.

<details>
<summary>JSON completo esperado</summary>

```json
{
  "recomendacao_id": "rec-xxxxxxxx",
  "estrategia": "cold_start",
  "contexto": "pagina_produto",
  "gerado_em": "AAAA-MM-DDTHH:MM:SS+00:00",
  "itens": [
    {"peca_id": "p-10", "posicao": 1, "pontuacao": 0.92, "criterios": ["similaridade", "popularidade"]},
    {"peca_id": "p-11", "posicao": 2, "pontuacao": 0.72, "criterios": ["similaridade", "popularidade"]},
    {"peca_id": "p-12", "posicao": 3, "pontuacao": 0.29, "criterios": ["popularidade"]}
  ]
}
```

</details>

### Windows (PowerShell)

No PowerShell, `curl` é outro comando. Use o Git Bash, o Swagger (`http://localhost:3000`) ou o equivalente abaixo, trocando o texto depois de `-Body` pelo JSON de cada teste:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:3000/v1/recomendacoes -ContentType "application/json" -Body '{"sessao_id": "s-001", "contexto": "pagina_inicial"}' | ConvertTo-Json -Depth 5
```

## Diferenças em relação à AV1

- **POST em vez de GET:** na AV1 o endpoint foi especificado como `GET` com parâmetros na URL. No mockup é `POST` com corpo JSON, o padrão do BentoML. Os campos são os mesmos.
- **`comprador_id`:** o campo é aceito, mas ignorado, porque o mockup não guarda histórico. Por isso a estratégia é sempre `cold_start`.
- **Dados:** o catálogo é um arquivo JSON, sem banco de dados. As vendas e visualizações são números fixos que simulam o job periódico de popularidade do design.
- **Erros:** seguem o formato padrão do BentoML, e não o formato `{"erro": {...}}` do design.

## Créditos

Estrutura inspirada no repositório de referência da disciplina, [lgallindo/recomendador-bentoml](https://github.com/lgallindo/recomendador-bentoml).
