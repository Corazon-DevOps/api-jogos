"""
Scraper de jogos de futebol do dia + canais de transmissão no Brasil.
Fonte principal: https://www.futebolnatv.com.br/
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict
from zoneinfo import ZoneInfo

import httpx
from bs4 import BeautifulSoup
from cachetools import TTLCache

# Cache em memória: 20 minutos (evita bloqueio e reduz carga)
CACHE = TTLCache(maxsize=10, ttl=20 * 60)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

TZ = ZoneInfo("America/Sao_Paulo")


def _normalize_channel(text: str) -> str:
    """Limpa e normaliza nomes de canais."""
    if not text:
        return "Não informado"
    text = re.sub(r"\s+", " ", text).strip()
    replacements = {
        "PREMIERE": "Premiere",
        "SPORTV": "SporTV",
        "GLOBO": "Globo",
        "CAZÉTV": "CazéTV (YouTube)",
        "CAZETV": "CazéTV (YouTube)",
        "GE TV": "ge tv",
        "DISNEY+": "Disney+",
        "YOUTUBE": "YouTube",
        "RECORD": "Record",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def _parse_status(horario: str) -> str:
    """Determina status com base no horário atual (Brasília)."""
    agora = datetime.now(TZ)
    try:
        h, m = map(int, horario.split(":"))
        jogo_dt = agora.replace(hour=h, minute=m, second=0, microsecond=0)

        if agora > jogo_dt + timedelta(hours=2, minutes=30):
            return "Encerrado"
        if agora >= jogo_dt:
            return "Em andamento"
        return "Não iniciado"
    except Exception:
        return "Não iniciado"


def scrape_jogos() -> List[Dict]:
    """
    Faz o scraping dos jogos do dia.
    Retorna lista de dicionários no formato da API.
    """
    cache_key = "jogos_hoje"
    if cache_key in CACHE:
        return CACHE[cache_key]

    url = "https://www.futebolnatv.com.br/"
    jogos: List[Dict] = []

    try:
        with httpx.Client(timeout=25.0, follow_redirects=True, headers=HEADERS) as client:
            resp = client.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        raise RuntimeError(f"Falha ao acessar o site de origem: {e}") from e

    soup = BeautifulSoup(html, "lxml")
    texto_completo = soup.get_text(separator="\n", strip=True)

    # Padrão heurístico robusto para extrair jogos + canais
    padrao = re.compile(
        r"(?P<campeonato>[^\n]{4,70}?)\n"
        r"(?:[^\n]*Rodada[^\n]*\n)?"
        r"(?P<horario>\d{1,2}:\d{2})\n"
        r"(?P<casa>[^\n]{2,45})\n"
        r"(?P<visitante>[^\n]{2,45})\n"
        r"(?P<canais>[A-Z0-9ÁÉÍÓÚÃÕÇ\s\(\)\+\-\.]{3,100})",
        re.MULTILINE | re.IGNORECASE,
    )

    hoje = datetime.now(TZ).strftime("%Y-%m-%d")

    for match in padrao.finditer(texto_completo):
        campeonato = match.group("campeonato").strip()
        horario = match.group("horario").strip()
        casa = match.group("casa").strip()
        visitante = match.group("visitante").strip()
        canais = _normalize_channel(match.group("canais"))

        # Filtros de qualidade
        if len(casa) < 2 or len(visitante) < 2:
            continue
        if "x" in casa.lower() or "x" in visitante.lower():
            continue
        if any(x in campeonato.lower() for x in ["vídeo", "gols", "destaque", "aplicativo"]):
            continue

        jogo = {
            "campeonato": campeonato,
            "time_casa": casa,
            "time_visitante": visitante,
            "horario": horario,
            "data": hoje,
            "onde_assistir": canais,
            "status": _parse_status(horario),
        }
        jogos.append(jogo)

    # Remove duplicatas
    vistos = set()
    jogos_unicos = []
    for j in jogos:
        chave = (j["time_casa"].lower(), j["time_visitante"].lower(), j["horario"])
        if chave not in vistos:
            vistos.add(chave)
            jogos_unicos.append(j)

    if not jogos_unicos:
        raise RuntimeError(
            "Nenhum jogo encontrado. A estrutura do site pode ter mudado. "
            "Verifique os seletores em scraper.py"
        )

    jogos_unicos.sort(key=lambda x: x["horario"])
    CACHE[cache_key] = jogos_unicos
    return jogos_unicos
