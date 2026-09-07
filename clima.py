"""
Clima CLI
---------
Ferramenta de linha de comando que consulta o clima atual de qualquer
cidade do mundo, usando a API pública gratuita da Open-Meteo
(https://open-meteo.com/) — não é necessário criar conta nem chave de API.

Uso:
    python clima.py "São Paulo"
    python clima.py "Lisboa" --pais PT
"""

import argparse
import sys

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Tradução simplificada dos códigos de clima (WMO) retornados pela API.
# Referência: https://open-meteo.com/en/docs
CODIGOS_CLIMA = {
    0: "Céu limpo",
    1: "Poucas nuvens",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Neblina",
    48: "Neblina com geada",
    51: "Garoa fraca",
    53: "Garoa moderada",
    55: "Garoa forte",
    61: "Chuva fraca",
    63: "Chuva moderada",
    65: "Chuva forte",
    71: "Neve fraca",
    73: "Neve moderada",
    75: "Neve forte",
    80: "Pancadas de chuva fracas",
    81: "Pancadas de chuva moderadas",
    82: "Pancadas de chuva fortes",
    95: "Tempestade",
}


class CidadeNaoEncontradaError(Exception):
    """Lançada quando a API de geocodificação não encontra a cidade informada."""


def geocodificar_cidade(nome_cidade: str, pais: str | None = None) -> dict:
    """
    Converte o nome de uma cidade em coordenadas (latitude/longitude).

    Args:
        nome_cidade: nome da cidade a ser buscada.
        pais: código do país (ISO 3166-1 alfa-2, ex: "BR", "PT") para
            desambiguar cidades com nomes repetidos em países diferentes.

    Returns:
        Dicionário com nome, país, latitude e longitude da cidade encontrada.

    Raises:
        CidadeNaoEncontradaError: se nenhuma cidade correspondente for encontrada.
        requests.RequestException: em caso de erro de rede/conexão.
    """
    parametros = {"name": nome_cidade, "count": 10, "language": "pt"}
    resposta = requests.get(GEOCODING_URL, params=parametros, timeout=10)
    resposta.raise_for_status()
    dados = resposta.json()

    resultados = dados.get("results")
    if not resultados:
        raise CidadeNaoEncontradaError(
            f"Não encontrei nenhuma cidade chamada '{nome_cidade}'."
        )

    if pais:
        filtrados = [
            r for r in resultados if r.get("country_code", "").upper() == pais.upper()
        ]
        if not filtrados:
            raise CidadeNaoEncontradaError(
                f"Encontrei '{nome_cidade}', mas nenhuma no país '{pais}'."
            )
        resultados = filtrados

    melhor = resultados[0]
    return {
        "nome": melhor["name"],
        "pais": melhor.get("country", "Desconhecido"),
        "latitude": melhor["latitude"],
        "longitude": melhor["longitude"],
    }


def buscar_clima_atual(latitude: float, longitude: float) -> dict:
    """
    Busca as condições climáticas atuais para uma coordenada.

    Args:
        latitude: latitude do local.
        longitude: longitude do local.

    Returns:
        Dicionário com temperatura (°C), velocidade do vento (km/h) e
        código de condição climática.

    Raises:
        requests.RequestException: em caso de erro de rede/conexão.
    """
    parametros = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,
    }
    resposta = requests.get(FORECAST_URL, params=parametros, timeout=10)
    resposta.raise_for_status()
    dados = resposta.json()

    clima_atual = dados["current_weather"]
    return {
        "temperatura": clima_atual["temperature"],
        "vento_kmh": clima_atual["windspeed"],
        "codigo_clima": clima_atual["weathercode"],
    }


def descrever_codigo_clima(codigo: int) -> str:
    """Traduz o código numérico de clima (WMO) para uma descrição em português."""
    return CODIGOS_CLIMA.get(codigo, "Condição desconhecida")


def formatar_relatorio(cidade: dict, clima: dict) -> str:
    """Monta o texto final exibido ao usuário."""
    descricao = descrever_codigo_clima(clima["codigo_clima"])
    return (
        f"\nClima em {cidade['nome']}, {cidade['pais']}\n"
        f"{'-' * (12 + len(cidade['nome']) + len(cidade['pais']))}\n"
        f"Condição:    {descricao}\n"
        f"Temperatura: {clima['temperatura']}°C\n"
        f"Vento:       {clima['vento_kmh']} km/h\n"
    )


def consultar_clima_da_cidade(nome_cidade: str, pais: str | None = None) -> str:
    """Função de alto nível: recebe o nome da cidade e devolve o relatório pronto."""
    cidade = geocodificar_cidade(nome_cidade, pais)
    clima = buscar_clima_atual(cidade["latitude"], cidade["longitude"])
    return formatar_relatorio(cidade, clima)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consulta o clima atual de uma cidade usando a API Open-Meteo."
    )
    parser.add_argument("cidade", help="Nome da cidade, ex: 'São Paulo'")
    parser.add_argument(
        "--pais",
        help="Código do país (ex: BR, PT) para desambiguar cidades homônimas",
        default=None,
    )
    args = parser.parse_args()

    try:
        print(consultar_clima_da_cidade(args.cidade, args.pais))
    except CidadeNaoEncontradaError as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as erro:
        print(f"Erro de conexão ao consultar a API: {erro}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
