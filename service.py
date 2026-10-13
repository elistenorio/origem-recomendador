"""Mockup do Módulo de Recomendação de Produtos do Origem (docs/design.md, seções 4 e 5.1)."""

import json
import math
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import bentoml

CATALOGO = Path(__file__).parent / "dados" / "catalogo.json"


def buscar_peca(pecas, peca_id):
    for peca in pecas:
        if peca["peca_id"] == peca_id:
            return peca
    return None


def calcular_popularidades(pecas):
    brutos = {}
    for peca in pecas:
        brutos[peca["peca_id"]] = 5 * peca["vendas_janela"] + peca["visualizacoes_janela"]

    maior_bruto = max(brutos.values())

    popularidades = {}
    for peca_id, bruto in brutos.items():
        popularidades[peca_id] = math.log(1 + bruto) / math.log(1 + maior_bruto)
    return popularidades


def calcular_similaridade(peca, referencia):
    if referencia is None:
        return 0.0
    if peca["tecnica_artesanal"] != referencia["tecnica_artesanal"]:
        return 0.0
    if peca["polo_origem"] == referencia["polo_origem"]:
        return 1.0
    return 0.7


@bentoml.service
class RecomendadorOrigem:
    @bentoml.api(route="/v1/recomendacoes")
    def recomendar(
        self,
        sessao_id: str,
        contexto: Literal["pagina_inicial", "pagina_produto"],
        peca_referencia_id: str | None = None,
        limite: int = 10,
    ) -> dict:
        """Recomenda peças do catálogo do Origem (RF-01, RF-02 e RF-04 a RF-07).

        Entrada:
          - sessao_id: identificador da sessão do comprador
          - contexto: "pagina_inicial" ou "pagina_produto"
          - peca_referencia_id: peça que o comprador está vendo (opcional)
          - limite: quantas peças devolver (padrão 10, máximo 50)
        """
        if limite < 1:
            raise bentoml.exceptions.InvalidArgument("limite deve ser maior ou igual a 1")

        pecas = json.loads(CATALOGO.read_text(encoding="utf-8"))["pecas"]
        referencia = buscar_peca(pecas, peca_referencia_id)
        popularidades = calcular_popularidades(pecas)

        candidatas = []
        for peca in pecas:
            if peca["estoque"] == 0 or not peca["publicada"]:
                continue
            if peca["peca_id"] == peca_referencia_id:
                continue

            popularidade = popularidades[peca["peca_id"]]
            similaridade = calcular_similaridade(peca, referencia)

            if referencia:
                pontuacao = 0.7 * similaridade + 0.3 * popularidade
            else:
                pontuacao = popularidade

            criterios = []
            if similaridade > 0:
                criterios.append("similaridade")
            if popularidade > 0:
                criterios.append("popularidade")

            candidatas.append({
                "peca_id": peca["peca_id"],
                "similaridade": similaridade,
                "pontuacao": pontuacao,
                "criterios": criterios,
            })

        candidatas.sort(key=lambda c: (c["similaridade"], c["pontuacao"]), reverse=True)

        itens = []
        for posicao, c in enumerate(candidatas[: min(limite, 50)], start=1):
            itens.append({
                "peca_id": c["peca_id"],
                "posicao": posicao,
                "pontuacao": round(c["pontuacao"], 2),
                "criterios": c["criterios"],
            })

        return {
            "recomendacao_id": f"rec-{uuid.uuid4().hex[:8]}",
            "estrategia": "cold_start",
            "contexto": contexto,
            "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "itens": itens,
        }
