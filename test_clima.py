"""
Testes automatizados do clima-cli.

Usamos mocks para simular as respostas da API — assim os testes rodam
rápido, não dependem de internet e não ficam "quebrando" se a API
estiver fora do ar.
"""

from unittest.mock import Mock, patch

import pytest
import requests

from clima import (
    CidadeNaoEncontradaError,
    descrever_codigo_clima,
    formatar_relatorio,
    geocodificar_cidade,
    buscar_clima_atual,
)


def _resposta_mock(json_data, status_ok=True):
    """Cria um objeto que imita uma resposta do requests."""
    resposta = Mock()
    resposta.json.return_value = json_data
    if status_ok:
        resposta.raise_for_status = Mock()
    else:
        resposta.raise_for_status = Mock(side_effect=requests.HTTPError("erro"))
    return resposta


class TestGeocodificarCidade:
    @patch("clima.requests.get")
    def test_encontra_cidade_com_sucesso(self, mock_get):
        mock_get.return_value = _resposta_mock(
            {
                "results": [
                    {
                        "name": "São Paulo",
                        "country": "Brasil",
                        "country_code": "BR",
                        "latitude": -23.55,
                        "longitude": -46.63,
                    }
                ]
            }
        )

        resultado = geocodificar_cidade("São Paulo")

        assert resultado["nome"] == "São Paulo"
        assert resultado["pais"] == "Brasil"
        assert resultado["latitude"] == -23.55

    @patch("clima.requests.get")
    def test_cidade_nao_encontrada_gera_erro(self, mock_get):
        mock_get.return_value = _resposta_mock({"results": []})

        with pytest.raises(CidadeNaoEncontradaError):
            geocodificar_cidade("CidadeQueNaoExiste123")

    @patch("clima.requests.get")
    def test_filtra_por_pais_quando_ha_ambiguidade(self, mock_get):
        mock_get.return_value = _resposta_mock(
            {
                "results": [
                    {
                        "name": "Springfield",
                        "country": "Estados Unidos",
                        "country_code": "US",
                        "latitude": 39.8,
                        "longitude": -89.6,
                    },
                    {
                        "name": "Springfield",
                        "country": "Reino Unido",
                        "country_code": "GB",
                        "latitude": 52.6,
                        "longitude": -1.1,
                    },
                ]
            }
        )

        resultado = geocodificar_cidade("Springfield", pais="GB")

        assert resultado["pais"] == "Reino Unido"

    @patch("clima.requests.get")
    def test_pais_incompativel_gera_erro(self, mock_get):
        mock_get.return_value = _resposta_mock(
            {
                "results": [
                    {
                        "name": "Springfield",
                        "country": "Estados Unidos",
                        "country_code": "US",
                        "latitude": 39.8,
                        "longitude": -89.6,
                    }
                ]
            }
        )

        with pytest.raises(CidadeNaoEncontradaError):
            geocodificar_cidade("Springfield", pais="FR")


class TestBuscarClimaAtual:
    @patch("clima.requests.get")
    def test_retorna_dados_do_clima(self, mock_get):
        mock_get.return_value = _resposta_mock(
            {
                "current_weather": {
                    "temperature": 24.5,
                    "windspeed": 12.3,
                    "weathercode": 1,
                }
            }
        )

        resultado = buscar_clima_atual(-23.55, -46.63)

        assert resultado["temperatura"] == 24.5
        assert resultado["vento_kmh"] == 12.3
        assert resultado["codigo_clima"] == 1


class TestDescreverCodigoClima:
    def test_codigo_conhecido(self):
        assert descrever_codigo_clima(0) == "Céu limpo"

    def test_codigo_desconhecido(self):
        assert descrever_codigo_clima(999) == "Condição desconhecida"


class TestFormatarRelatorio:
    def test_relatorio_contem_dados_principais(self):
        cidade = {"nome": "Lisboa", "pais": "Portugal"}
        clima = {"temperatura": 18.0, "vento_kmh": 10.0, "codigo_clima": 3}

        relatorio = formatar_relatorio(cidade, clima)

        assert "Lisboa" in relatorio
        assert "Portugal" in relatorio
        assert "18.0" in relatorio
        assert "Nublado" in relatorio
