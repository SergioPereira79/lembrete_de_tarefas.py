# Lembrete de Tarefas por Inatividade

Um simples programa para Windows que ajuda a lembrar de checar sua lista de tarefas ao retornar ao computador após um período de inatividade.

## Funcionalidades

- Monitora a inatividade do mouse.
- Abre um link (Ex: Google Keep, Notion, Trello) quando o usuário retorna.
- Permite configurar o tempo de inatividade e o link.
- Detecta se uma janela com a tarefa já está aberta para evitar abas duplicadas.
- Permite escolher em qual navegador abrir o link.

## Como Usar (Para Usuários)

1.  Baixe o arquivo `lembrete_de_tarefas.exe` da seção "Releases".
2.  Coloque o `.exe` em uma pasta de sua preferência.
3.  Execute o programa e configure suas preferências.
4.  Pronto!

## Como Contribuir (Para Desenvolvedores)

1.  Instale o Python 3.12 ou superior.
2.  Clone este repositório.
3.  Instale as dependências:
    ```bash
    py -m pip install -r requirements.txt
    ```
4.  Execute o script:
    ```bash
    py lembrete_de_tarefas.py
    ```