# API Jogos de Futebol – Onde Assistir (Brasil)

API em FastAPI que faz scraping dos jogos do dia e informa onde assistir no Brasil.

## Endpoints

| Método | Rota     | Descrição                    |
|--------|----------|------------------------------|
| GET    | `/`      | Informações básicas          |
| GET    | `/jogos` | Lista completa de jogos      |
| GET    | `/health`| Status da API                |
| GET    | `/docs`  | Documentação interativa      |

## Rodar localmente

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: http://localhost:8000/docs

## Deploy na Integrator Host (Painel ICP)

### Opção 1 – Docker (recomendado)

1. Crie um repositório no GitHub e envie esta pasta.
2. No Painel ICP da Integrator:
   - Crie um novo **App** ou **Container**.
   - Escolha **Docker** / **Container personalizado**.
   - Conecte o repositório GitHub.
   - Build: deixe o padrão (usa o Dockerfile).
   - Porta: 8000 (ou a que o painel indicar).
3. Após o deploy, acesse a URL gerada + `/jogos`.

### Opção 2 – Python nativo

1. No Painel ICP → Novo App → **Python**.
2. Repositório GitHub.
3. Configurações:
   - **Install / Build**: `pip install -r requirements.txt`
   - **Start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Salve e faça o deploy.

### Após o deploy

- Teste: `https://sua-url.integrator.../jogos`
- Documentação: `https://sua-url.integrator.../docs`
- No Lovable: use a URL completa como `VITE_API_BASE_URL`

## Observações

- Cache de 20 minutos para não sobrecarregar o site de origem.
- CORS liberado (`*`) – restrinja em produção se desejar.
- Se o site de origem mudar a estrutura, o scraper pode precisar de ajuste em `scraper.py`.
