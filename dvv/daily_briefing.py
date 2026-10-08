
import os
import sys
import json

from pathlib import Path
PASTA_PRINCIPAL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PASTA_PRINCIPAL))

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Localiza a pasta principal do projeto
PASTA_PRINCIPAL = Path(__file__).resolve().parent.parent

# Permite importar os arquivos da pasta principal
sys.path.insert(0, str(PASTA_PRINCIPAL))

from calendar_service import buscar_compromissos
from gmail_service import enviar_email


# ==================================================
# CONFIGURAÇÕES
# ==================================================

load_dotenv(PASTA_PRINCIPAL / ".env")

TIMEZONE = ZoneInfo("America/Sao_Paulo")
MODELO = "gpt-4.1-mini"

BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_CONTROLE = BASE_DIR / "ultimo_envio.json"


# ==================================================
# GOOGLE AGENDA
# ==================================================

def data_do_evento(evento):
    """Converte a data do evento para o horário de Brasília."""

    inicio = datetime.fromisoformat(evento["inicio"])

    if inicio.tzinfo is not None:
        inicio = inicio.astimezone(TIMEZONE)

    return inicio


def formatar_eventos(eventos):
    """Organiza os compromissos cronologicamente."""

    if not eventos:
        return "Nenhum compromisso encontrado."

    linhas = []

    for evento in sorted(eventos, key=data_do_evento):

        inicio = data_do_evento(evento)

        if "T" in evento["inicio"]:
            horario = inicio.strftime("%d/%m/%Y às %H:%M")
        else:
            horario = inicio.strftime("%d/%m/%Y - Dia inteiro")

        linhas.append(
            f"{horario} | {evento['titulo']}"
        )

    return "\n".join(linhas)


# ==================================================
# CONTROLE DE ENVIOS
# ==================================================

def ja_enviado_hoje():
    """Verifica se o briefing já foi enviado hoje."""

    if not ARQUIVO_CONTROLE.exists():
        return False

    with open(
        ARQUIVO_CONTROLE,
        "r",
        encoding="utf-8"
    ) as arquivo:
        dados = json.load(arquivo)

    hoje = datetime.now(TIMEZONE).strftime("%Y-%m-%d")

    return dados.get("ultimo_envio") == hoje


def registrar_envio(mensagem_id):
    """Registra um envio concluído com sucesso."""

    agora = datetime.now(TIMEZONE)

    dados = {
        "ultimo_envio": agora.strftime("%Y-%m-%d"),
        "horario": agora.strftime("%H:%M:%S"),
        "mensagem_id": mensagem_id
    }

    with open(
        ARQUIVO_CONTROLE,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            dados,
            arquivo,
            indent=4,
            ensure_ascii=False
        )


# ==================================================
# INTELIGÊNCIA ARTIFICIAL
# ==================================================

def gerar_resumo():
    """Consulta a agenda e gera o briefing com IA."""

    agora = datetime.now(TIMEZONE)
    hoje = agora.date()
    limite = hoje + timedelta(days=7)

    eventos = buscar_compromissos(dias=7)

    eventos_hoje = []
    eventos_futuros = []

    for evento in eventos:

        dia = data_do_evento(evento).date()

        if dia == hoje:
            eventos_hoje.append(evento)

        elif hoje < dia < limite:
            eventos_futuros.append(evento)

    agenda_hoje = formatar_eventos(eventos_hoje)
    agenda_futura = formatar_eventos(eventos_futuros)

    prompt = f"""
Você é Lucas Assistant, um assistente pessoal
especializado em produtividade e organização.

DATA ATUAL: {agora.strftime('%d/%m/%Y')}
HORÁRIO ATUAL: {agora.strftime('%H:%M')}
FUSO HORÁRIO: America/Sao_Paulo

AGENDA DE HOJE:
{agenda_hoje}

PRÓXIMOS SEIS DIAS:
{agenda_futura}

Prepare um briefing matinal profissional,
objetivo e agradável de ler por e-mail.

ESTRUTURA:

1. Saudação e resumo geral do dia.
2. Compromissos de hoje em ordem cronológica.
3. Próximos compromissos importantes.
4. Alertas relevantes, quando houver.
5. Uma sugestão prática de organização.

REGRAS:

- Responda sempre em português brasileiro.
- Utilize somente os compromissos informados.
- Não invente datas, horários ou eventos.
- Diferencie fatos de sugestões.
- Não invente duração ou urgência.
- Não afirme existir conflito sem evidência.
- Se não houver eventos, informe isso.
- Seja claro, objetivo e profissional.
- Utilize texto simples, adequado para e-mail.
- Não utilize tabelas ou Markdown complexo.
"""

    modelo = ChatOpenAI(
        model=MODELO,
        temperature=0
    )

    resposta = modelo.invoke(prompt)

    return str(resposta.content)


# ==================================================
# ENVIO DO BRIEFING
# ==================================================

def executar_resumo(automatico=False):
    """Gera e envia o briefing matinal."""

    destinatario = os.getenv(
        "EMAIL_DESTINO", ""
    ).strip()

    if not destinatario:
        raise ValueError(
            "Configure EMAIL_DESTINO no arquivo .env."
        )

    # Bloqueia envios automáticos duplicados
    if automatico and ja_enviado_hoje():
        print(
            "Briefing já enviado hoje. "
            "Nenhum novo envio necessário."
        )
        return

    hoje = datetime.now(TIMEZONE).strftime("%d/%m/%Y")

    assunto = (
        f"Lucas Assistant | Resumo Matinal - {hoje}"
    )

    print("Consultando agenda e gerando briefing...")

    resumo = gerar_resumo()

    print("\n=== RESUMO MATINAL ===\n")
    print(resumo)

    # No modo manual, pede confirmação
    if not automatico:

        resposta = input(
            "\nDeseja enviar por e-mail? (s/n): "
        ).strip().lower()

        if resposta != "s":
            print("Envio cancelado.")
            return

    # Envia pelo Gmail
    mensagem_id = enviar_email(
        destinatario=destinatario,
        assunto=assunto,
        mensagem=resumo
    )

    # Registra o envio após sucesso na API
    registrar_envio(mensagem_id)

    print("\nE-mail enviado com sucesso!")
    print(f"ID da mensagem: {mensagem_id}")


# ==================================================
# EXECUÇÃO
# ==================================================

if __name__ == "__main__":

    try:
        automatico = "--auto" in sys.argv

        executar_resumo(
            automatico=automatico
        )

    except Exception as erro:
        print(f"\nErro ao executar briefing: {erro}")
        sys.exit(1)