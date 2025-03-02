import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
from flask import Flask, render_template

app = Flask(__name__)


API_KEY = "34c7ecd702364c61a2ea050779f06a97"

CITY = "Sao Paulo"

def coletar_dados():
    """Coleta dados de temperatura e umidade da API OpenWeatherMap."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()

        temperatura = data["main"]["temp"]
        umidade = data["main"]["humidity"]
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clima_id = data["weather"][0]["id"]

        if 200 <= clima_id < 300:
            clima = "chuva"
            emoji = "️"
        elif 300 <= clima_id < 600:
            clima = "nublado"
            emoji = "☁️"
        elif 800 == clima_id:
            clima = "sol"
            emoji = "☀️"
        else:
            clima = "desconhecido"
            emoji = "❓"

        return {"data_hora": data_hora, "temperatura": temperatura, "umidade": umidade, "clima": clima, "emoji": emoji}

    except requests.exceptions.RequestException as e:
        print(f"Erro ao coletar dados: {e}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Erro ao processar dados da API: {e}")
        return None

def gerar_grafico(dados):
    """Gera um gráfico com os dados de temperatura e umidade."""
    if dados:
        df = pd.DataFrame([dados])
        df["data_hora"] = pd.to_datetime(df["data_hora"])

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["data_hora"], y=df["temperatura"], mode="lines", name="Temperatura (°C)"))
        fig.add_trace(go.Scatter(x=df["data_hora"], y=df["umidade"], mode="lines", name="Umidade (%)"))

        fig.update_layout(title="Variação de Temperatura e Umidade ao Longo do Tempo", xaxis_title="Data e Hora", yaxis_title="Valor")
        return fig.to_html(full_html=False, include_plotlyjs="cdn")
    else:
        return "Gráfico não disponível. Dados insuficientes."

@app.route("/")
def index():
    dados = coletar_dados()
    grafico_html = gerar_grafico(dados)
    return render_template("index.html", dados=dados, grafico_html=grafico_html)

if __name__ == "__main__":
    app.run(debug=True)