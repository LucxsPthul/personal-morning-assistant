import base64
from email.message import EmailMessage
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Permissão para enviar e-mails
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]

# Caminhos dos arquivos
BASE_DIR = Path(__file__).resolve().parent

CREDENTIALS_FILE = BASE_DIR / "credentials.json"

# Token exclusivo do Gmail
TOKEN_FILE = BASE_DIR / "gmail_token.json"


def conectar_gmail():
    """Autentica o usuário na API do Gmail."""

    credenciais = None

    if TOKEN_FILE.exists():
        credenciais = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            SCOPES
        )

    if not credenciais or not credenciais.valid:

        if (
            credenciais
            and credenciais.expired
            and credenciais.refresh_token
        ):
            credenciais.refresh(Request())

        else:
            fluxo = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE),
                SCOPES
            )

            credenciais = fluxo.run_local_server(port=0)

        TOKEN_FILE.write_text(
            credenciais.to_json(),
            encoding="utf-8"
        )

    return build(
        "gmail",
        "v1",
        credentials=credenciais
    )


def enviar_email(destinatario, assunto, mensagem):
    """Envia um e-mail utilizando a conta autorizada."""

    servico = conectar_gmail()

    email = EmailMessage()

    email["To"] = destinatario
    email["Subject"] = assunto

    email.set_content(mensagem)

    mensagem_codificada = base64.urlsafe_b64encode(
        email.as_bytes()
    ).decode("utf-8")

    resultado = servico.users().messages().send(
        userId="me",
        body={
            "raw": mensagem_codificada
        }
    ).execute()

    return resultado["id"]


if __name__ == "__main__":

    destinatario = input(
        "Digite seu e-mail para receber o teste: "
    ).strip()

    if not destinatario:
        print("Nenhum destinatário informado.")

    else:
        try:
            mensagem_id = enviar_email(
                destinatario=destinatario,
                assunto="Teste - Lucas Assistant",
                mensagem=(
                    "Olá!\n\n"
                    "Este é um e-mail de teste enviado "
                    "automaticamente pelo Lucas Assistant.\n\n"
                    "A integração com o Gmail está funcionando!"
                )
            )

            print("\nE-mail enviado com sucesso!")
            print("ID da mensagem:", mensagem_id)

        except Exception as erro:
            print("\nErro ao enviar e-mail:")
            print(erro)
