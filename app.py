"""EcoRota: 5 Web services de integração com Inven!RA (Semana 1).

Nesta fase, os dados de analytics são exemplos e o sexto serviço de
realização da atividade pelo aluno NÃO está implementado.
"""

import os
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

app = FastAPI(title="EcoRota - Integração Inven!RA", version="0.1.0")
TEMPLATES = Path(__file__).resolve().parent / "templates"


def base_publica(request: Request) -> str:
    """Deteta o domínio público do Render quando existe; em local usa o pedido."""
    dominio = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
    if dominio:
        return "https://" + dominio.rstrip("/")
    return str(request.base_url).rstrip("/")


async def identificar_instancia(request: Request):
    """Lê activityID de GET query string ou de POST JSON (e formulário)."""
    identificador = request.query_params.get("activityID")
    if request.method == "POST":
        tipo = request.headers.get("content-type", "")
        if "application/json" in tipo:
            try:
                dados = await request.json()
                if isinstance(dados, dict):
                    identificador = dados.get("activityID", identificador)
            except (ValueError, UnicodeError):
                return None
        elif "application/x-www-form-urlencoded" in tipo:
            dados = await request.form()
            identificador = dados.get("activityID", identificador)
    if not isinstance(identificador, str):
        return None
    identificador = identificador.strip()
    if not identificador or len(identificador) > 128:
        return None
    return identificador


@app.get("/", response_class=HTMLResponse)
def inicio():
    return (TEMPLATES / "index.html").read_text(encoding="utf-8")


@app.get("/config", response_class=HTMLResponse)
def config():
    """config_url: formulário de configuração para o professor."""
    return (TEMPLATES / "config.html").read_text(encoding="utf-8")


@app.get("/params")
def params():
    """json_params_url: lista dos campos configuráveis."""
    return [
        {"name": "tema", "type": "text/plain"},
        {"name": "instrucoes", "type": "text/plain"},
        {"name": "categorias", "type": "text/plain"},
        {"name": "minimo_observacoes", "type": "text/plain"},
    ]


@app.api_route("/deploy", methods=["GET", "POST"])
async def deploy(request: Request):
    """user_url: devolve URL da instância como texto, não como JSON."""
    activity_id = await identificar_instancia(request)
    if activity_id is None:
        return JSONResponse({"erro": "Indique um activityID válido (1 a 128 caracteres)."}, status_code=400)
    destino = base_publica(request) + "/atividade/" + quote(activity_id, safe="")
    # /atividade/... corresponde ao sexto serviço, a desenvolver depois.
    return PlainTextResponse(destino)


@app.get("/analytics-list")
def analytics_list():
    """analytics_list_url: indicadores quantitativos e qualitativos."""
    return {
        "qualAnalytics": [
            {"name": "reflexao_final", "type": "text/plain"},
        ],
        "quantAnalytics": [
            {"name": "observacoes_registadas", "type": "integer"},
            {"name": "categorias_identificadas", "type": "integer"},
            {"name": "atividade_concluida", "type": "boolean"},
        ],
    }


@app.post("/analytics")
async def analytics(request: Request):
    """analytics_url: devolve exemplos fictícios para a instância pedida."""
    activity_id = await identificar_instancia(request)
    if activity_id is None:
        return JSONResponse({"erro": "É obrigatório enviar activityID no POST."}, status_code=400)
    # Dados de demonstração, sem persistência e sem dados pessoais reais.
    return [
        {
            "inveniraStdID": "1001",
            "quantAnalytics": [
                {"name": "observacoes_registadas", "type": "integer", "value": 4},
                {"name": "categorias_identificadas", "type": "integer", "value": 3},
                {"name": "atividade_concluida", "type": "boolean", "value": True},
            ],
            "qualAnalytics": [
                {
                    "name": "reflexao_final",
                    "type": "text/plain",
                    "value": "Observei pontos de reciclagem e zonas com resíduos.",
                },
            ],
        },
    ]


@app.get("/registo")
def registo(request: Request):
    """Auxiliar: JSON com os cinco URLs reais que devem constar do registo."""
    base = base_publica(request)
    return {
        "name": "EcoRota - Observação Ambiental",
        "config_url": base + "/config",
        "json_params_url": base + "/params",
        "user_url": base + "/deploy",
        "analytics_url": base + "/analytics",
        "analytics_list_url": base + "/analytics-list",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
