from langchain_core.tools import Tool
from calendar_service import buscar_compromissos


def consultar_agenda(dias: str = "7") -> str:
    """
    Consulta os compromissos do Google Agenda.
    Recebe a quantidade de dias que deseja consultar.
    """

    try:
        dias = int(dias)
    except (ValueError, TypeError):
        return "Erro: informe um número inteiro de dias."

    if dias < 0 or dias > 30:
        return "Informe um período entre 0 e 30 dias."

    eventos = buscar_compromissos(dias=dias)

    if not eventos:
        return "Nenhum compromisso encontrado no período."

    resultado = []

    for evento in eventos:
        resultado.append(
            f"Título: {evento['titulo']}\n"
            f"Data: {evento['inicio']}\n"
            f"Descrição: {evento['descricao']}"
        )

    return "\n\n".join(resultado)


calendar_tool = Tool(
    name="consultar_google_agenda",
    func=consultar_agenda,
    description=(
        "Consulta os compromissos reais do Google Agenda. "
        "Recebe a quantidade de dias futuros como um número inteiro "
        "entre 0 e 30. "
        "Use esta ferramenta para consultar compromissos, "
        "eventos e reuniões do usuário."
    ),
)