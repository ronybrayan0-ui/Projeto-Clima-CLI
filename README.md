# 🌤️ Clima CLI

Ferramenta de linha de comando em Python que consulta o clima atual de
qualquer cidade do mundo, usando a API pública e gratuita da
[Open-Meteo](https://open-meteo.com/) — sem necessidade de cadastro ou
chave de API.

## Por que esse projeto

Feito para praticar consumo de APIs REST em Python, tratamento de erros
de rede e organização de código em funções testáveis, com cobertura de
testes automatizados usando `pytest` e mocks (os testes não dependem de internet).

## Funcionalidades

- Busca automática de coordenadas a partir do nome da cidade (geocodificação)
- Consulta de temperatura, velocidade do vento e condição climática atual
- Suporte a desambiguação por país, para cidades com nomes repetidos
  (ex: existem várias "Springfield" no mundo)
- Tratamento de erros: cidade não encontrada, falha de conexão, etc.

## Como instalar

```bash
git clone https://github.com/ronybrayan0-ui/clima-cli.git
cd clima-cli
pip install -r requirements.txt
```

## Como usar

```bash
python clima.py "São Paulo"
```

Saída esperada:

```
Clima em São Paulo, Brasil
--------------------------
Condição:    Parcialmente nublado
Temperatura: 24.5°C
Vento:       12.3 km/h
```

Para desambiguar cidades com nomes repetidos, use `--pais` com o código
do país (ISO 3166-1 alfa-2):

```bash
python clima.py "Springfield" --pais GB
```

## Como rodar os testes

```bash
python -m pytest tests/ -v
```

## Tecnologias usadas

- Python 3
- [requests](https://docs.python-requests.org/) para chamadas HTTP
- [pytest](https://docs.pytest.org/) para testes automatizados
- API [Open-Meteo](https://open-meteo.com/) (geocodificação + previsão do tempo)

## Possíveis melhorias futuras

- [ ] Adicionar previsão para os próximos dias, não só o clima atual
- [ ] Suporte a unidades imperiais (Fahrenheit, mph)
- [ ] Empacotar como comando instalável via `pip install`
