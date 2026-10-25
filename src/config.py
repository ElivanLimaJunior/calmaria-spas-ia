"""Configurações centralizadas do projeto Calmaria Spas.

Tudo o que se repete entre os scripts (caminhos, modelo, thresholds, categorias,
arquivos de prompt) fica aqui. Segredos NÃO ficam aqui: vêm do .env.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
PASTA_DADOS = RAIZ / "dados"
PASTA_PROMPTS = RAIZ / "prompts"
PASTA_RESULTADOS = RAIZ / "etapa-3-avaliacao" / "resultados"

DATASET = PASTA_DADOS / "calmaria_interacoes.csv"
COLUNAS_OBRIGATORIAS = [
    "id", "pergunta_cliente", "categoria", "intencao", "resposta_esperada", "perfil_cliente",
]

# Intenções aceitas pelo classificador. "others" é uma opção válida de resposta,
# mesmo não aparecendo no dataset.
INTENCOES = [
    "recomendar_tratamento",
    "consultar_preco",
    "agendar_horario",
    "tirar_duvida",
    "cancelar_agendamento",
    "reclamar",
    "others",
]

# Prompts
PROMPT_ASSISTENTE = "assistente_calmaria.md"
PROMPT_FILES = {
    "baseline": "assistente_baseline.md",
    "improved": "assistente_improved.md",
}
PROMPT_FALLBACK = PROMPT_FILES["improved"]
PROMPT_INTENCAO = "classificar_intencao.md"
PROMPT_JUIZ = "juiz_calmaria.md"

# Avaliação (Etapa 3)
SCORE_THRESHOLD_REVIEW = 3
SCORE_THRESHOLD_FALLBACK = 2
SCORE_FALHA = 0
AMOSTRA = 10  # mesmas 10 primeiras linhas: cobrem as 6 intenções do dataset
LIMITE_RESPOSTA_LONGA = 200
PALAVRAS_ESPERADAS = 5
# Falha de parsing do juiz não é evidência de resposta ruim; por padrão vai para
# revisão humana em vez de gastar uma nova geração. Ver DECISOES.md (D7).
REGENERAR_EM_FALHA_DE_AVALIACAO = False

# Modelo
TEMPERATURA_ASSISTENTE = 0.3
TEMPERATURA_AVALIACAO = 0.0  # classificador e juiz: o mais determinístico possível
MAX_TOKENS_RESPOSTA = 300
MAX_TOKENS_AVALIACAO = 120
TIMEOUT_SEGUNDOS = 30
MAX_TENTATIVAS = 2

# Observabilidade
TAGS_BASE = ["calmaria", "assistente"]


def carregar_ambiente():
    """Lê o .env (se existir) e devolve o nome do modelo configurado."""
    load_dotenv(RAIZ / ".env")
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def credenciais_faltando():
    """Lista as variáveis obrigatórias que estão vazias (sem mostrar valores)."""
    obrigatorias = ["OPENAI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
    return [nome for nome in obrigatorias if not os.getenv(nome)]
