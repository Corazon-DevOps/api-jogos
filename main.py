from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from scraper import scrape_jogos

app = FastAPI(
    title="API Jogos de Futebol – Onde Assistir (Brasil)",
    description="Lista os jogos do dia com canais de transmissão no Brasil. Fonte: futebolnatv.com.br",
    version="1.0.0",
)

# CORS liberado (necessário para o Lovable e qualquer frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção restrinja ao domínio do seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "mensagem": "API de Jogos de Futebol – Onde Assistir",
        "endpoints": {
            "jogos": "/jogos",
            "health": "/health",
            "docs": "/docs",
        },
    }


@app.get("/jogos", summary="Lista de jogos do dia")
async def get_jogos():
    """
    Retorna todos os jogos de futebol do dia com:
    - campeonato
    - time_casa / time_visitante
    - horário e data
    - onde_assistir (canais)
    - status (Não iniciado / Em andamento / Encerrado)
    """
    try:
        jogos = scrape_jogos()
        return {
            "data": datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d"),
            "total": len(jogos),
            "fonte": "futebolnatv.com.br",
            "jogos": jogos,
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
