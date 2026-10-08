from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Permissão somente para leitura do Google Agenda
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly"
]

BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

TIMEZONE = ZoneInfo("America/Sao_Paulo")


def conectar_google_agenda():
    credenciais = None

    # Recupera uma autorização salva anteriormente
    if TOKEN_FILE.exists():
        credenciais = Credentials.from_authorized_user_file(
            str(TOKEN_FILE), SCOPES
        )

    # Solicita autorização quando necessário
    if not credenciais or not credenciais.valid:

        if credenciais and credenciais.expired and credenciais.refresh_token:
            credenciais.refresh(Request())

        else:
            fluxo = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )

            credenciais = fluxo.run_local_server(port=0)

        # Salva a autorização para próximas execuções
        TOKEN_FILE.write_text(
            credenciais.to_json(),
            encoding="utf-8"
        )

    return build("calendar", "v3", credentials=credenciais)


def buscar_compromissos(dias=7):
    servico = conectar_google_agenda()

    agora = datetime.now(TIMEZONE)
    inicio = agora.replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    fim = inicio + timedelta(days=dias + 1)

    resultado = servico.events().list(
        calendarId="primary",
        timeMin=inicio.isoformat(),
        timeMax=fim.isoformat(),
        maxResults=250,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    eventos = resultado.get("items", [])

    compromissos = []

    for evento in eventos:
        inicio_evento = evento["start"].get(
            "dateTime",
            evento["start"].get("date")
        )

        compromissos.append({
            "titulo": evento.get("summary", "Sem título"),
            "inicio": inicio_evento,
            "descricao": evento.get("description", "")
        })

    return compromissos


if __name__ == "__main__":
    eventos = buscar_compromissos()

    print("\n=== MEUS COMPROMISSOS ===\n")

    if not eventos:
        print("Nenhum compromisso encontrado.")

    for evento in eventos:
        print(f"Título: {evento['titulo']}")
        print(f"Data: {evento['inicio']}")
        print("-" * 30)