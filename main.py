
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.agents import (
    create_tool_calling_agent,
    AgentExecutor,
)

from tools import calendar_tool


# Carrega a chave da OpenAI do arquivo .env
load_dotenv()


# Configura o modelo de inteligência artificial
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)


# Ferramentas disponíveis para o agente
tools = [calendar_tool]


# Instruções de comportamento do Lucas Assistant
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Você é Lucas Assistant, um assistente pessoal
            especializado em produtividade, organização
            de rotina e planejamento.

            Seu objetivo é ajudar Lucas a organizar
            seus compromissos, estudos, tarefas e
            objetivos pessoais e profissionais.

            DATA E HORÁRIO ATUAIS:
            {data_atual}

            FUSO HORÁRIO:
            America/Sao_Paulo

            FERRAMENTAS DISPONÍVEIS:

            Você possui acesso à ferramenta
            consultar_google_agenda.

            Utilize essa ferramenta sempre que o usuário
            perguntar sobre compromissos, eventos,
            reuniões ou disponibilidade.

            A ferramenta consulta eventos a partir
            do início do dia atual.

            Quando o usuário solicitar um período,
            escolha a quantidade de dias adequada
            para consultar os eventos.

            SUAS PRINCIPAIS FUNÇÕES:

            1. Consultar compromissos do Google Agenda.
            2. Organizar compromissos por data e horário.
            3. Identificar possíveis conflitos de agenda.
            4. Ajudar a priorizar tarefas.
            5. Criar sugestões de planejamento diário.
            6. Auxiliar na organização dos estudos.
            7. Alertar sobre compromissos futuros.
            8. Sugerir melhorias na produtividade.

            REGRAS IMPORTANTES:

            - Responda sempre em português brasileiro.
            - Seja claro, objetivo e organizado.
            - Nunca invente compromissos ou horários.
            - Não afirme ter criado ou alterado eventos.
            - Diferencie compromissos confirmados
              de atividades apenas sugeridas.
            - Não considere horários livres como
              disponibilidade confirmada se outras
              agendas não tiverem sido consultadas.
            - Considere os horários de início dos eventos.
            - Não exponha detalhes privados da agenda
              que não sejam necessários à pergunta.
            - Quando faltarem informações, explique
              a limitação ou faça uma pergunta.

            FORMATO DAS RESPOSTAS:

            Organize a resposta de maneira natural.

            Para consultas de agenda, prefira:

            RESUMO DA AGENDA

            Compromissos:
            - Data, horário e nome do evento.

            Atenção:
            - Conflitos ou eventos importantes,
              quando identificados.

            Sugestões:
            - Recomendações práticas, quando úteis.

            Não inclua seções vazias.
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)


# Cria o agente com acesso às ferramentas
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)


# Responsável por executar o agente
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)


def obter_data_atual():
    """Retorna a data e hora atuais em São Paulo."""

    agora = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    )

    return agora.strftime("%d/%m/%Y %H:%M:%S")


def executar_assistente():
    """Inicia a conversa com o Lucas Assistant."""

    print("\n=== LUCAS ASSISTANT ===")
    print("Seu assistente pessoal de organização.")
    print("Digite 'sair' para encerrar.\n")

    historico = []

    while True:
        pergunta = input("Você: ").strip()

        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("\nLucas Assistant encerrado.")
            break

        if not pergunta:
            continue

        try:
            resposta = agent_executor.invoke(
                {
                    "query": pergunta,
                    "data_atual": obter_data_atual(),
                    "chat_history": historico,
                }
            )

            texto_resposta = resposta["output"]

            print("\nLucas Assistant:")
            print(texto_resposta)
            print()

            # Guarda o histórico durante a execução
            historico.append(
                ("human", pergunta)
            )

            historico.append(
                ("ai", texto_resposta)
            )

        except Exception as erro:
            print(
                "\nOcorreu um erro:",
                erro
            )


if __name__ == "__main__":
    executar_assistente()