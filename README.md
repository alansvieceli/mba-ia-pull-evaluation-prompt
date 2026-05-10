# Pull, Otimizacao e Avaliacao de Prompts com LangChain e LangSmith

Projeto Python para fazer pull de um prompt inicial do LangSmith Prompt Hub, otimizar esse prompt com tecnicas de Prompt Engineering, publicar a versao otimizada no LangSmith e avaliar a qualidade com metricas customizadas.

O caso trabalhado transforma relatos de bugs em User Stories estruturadas.

## Estrutura Obrigatoria do Projeto

```text
mba-ia-pull-evaluation-prompt/
├── .env.example
├── requirements.txt
├── README.md
├── prompts/
│   ├── bug_to_user_story_v1.yml
│   └── bug_to_user_story_v2.yml
├── datasets/
│   └── bug_to_user_story.jsonl
├── src/
│   ├── pull_prompts.py
│   ├── push_prompts.py
│   ├── evaluate.py
│   ├── metrics.py
│   └── utils.py
└── tests/
    └── test_prompts.py
```

Arquivos implementados ou ajustados:

- `src/pull_prompts.py`: faz pull do prompt inicial `leonanluppi/bug_to_user_story_v1` e salva em YAML.
- `src/push_prompts.py`: publica o prompt otimizado `bug_to_user_story_v2` no LangSmith Prompt Hub.
- `prompts/bug_to_user_story_v2.yml`: prompt otimizado com System Prompt, User Prompt, metadados e exemplos.
- `tests/test_prompts.py`: testes de validacao do prompt usando `pytest`.
- `README.md`: documentacao do processo, execucao e resultados.

## Técnicas Aplicadas (Fase 2)

### Few-shot Learning

Usei Few-shot Learning com exemplos claros de entrada e saida diretamente no `system_prompt`.

Justificativa: a avaliacao compara a resposta gerada com uma referencia esperada. Exemplos de entrada/saida ajudam o modelo a reproduzir o formato, o nivel de detalhe e o vocabulário esperado, reduzindo variacoes desnecessarias.

Exemplo de aplicacao no prompt:

```text
Entrada: Campo de email aceita texto sem @, permitindo cadastros invalidos.
Saida:
Como um usuario criando uma conta, eu quero que o sistema valide meu email corretamente, para que eu nao insira um endereco invalido por engano.

Critérios de Aceitação:
- Dado que estou no formulário de cadastro
- Quando digito um email sem o caractere @
- Então devo ver uma mensagem de erro
- E não devo conseguir prosseguir com o cadastro
- E a mensagem deve explicar o formato correto
```

Tambem foram adicionados exemplos para bugs de carrinho, iOS, dashboard, Safari, webhook, performance, seguranca, calculo, z-index e estoque.

### Role Prompting

O prompt define uma persona explicita:

```text
Você é um Senior Product Manager especializado em converter relatos de bugs em User Stories para Produto, QA e Desenvolvimento.
```

Justificativa: a persona orienta o modelo a escrever com foco em Produto, QA e Desenvolvimento, mantendo o formato de User Story e criterios de aceite testaveis.

### Skeleton of Thought

O prompt usa um processo interno estruturado antes da resposta final:

```text
PROCESSO DE ANÁLISE (Skeleton of Thought):
1. Quem é o usuário ou sistema afetado?
2. Qual ação corrigida a pessoa/sistema precisa conseguir?
3. Qual benefício direto aparece no relato?
4. Quais fatos, números, plataformas, endpoints, logs e sintomas devem aparecer?
5. Qual é o menor conjunto de seções necessário para espelhar o bug?
```

Justificativa: essa tecnica organiza a analise sem expor raciocinio desnecessario na resposta final. Isso ajudou a manter a saida objetiva, com menos inferencias e maior aderencia ao dataset.

### Regras de Precisao e Controle de Verbosidade

O prompt final prioriza respostas proximas do relato original e da referencia esperada.

Exemplos de regras aplicadas:

- reutilizar termos, numeros, plataformas, endpoints e status do relato;
- nao inventar detalhes ausentes;
- nao criar secoes extras sem gatilho explicito;
- manter Markdown simples;
- preferir 5 criterios para bugs simples;
- usar secoes tecnicas apenas quando o bug trouxer logs, SQL, z-index, performance, seguranca, race condition ou outro gatilho claro.

Justificativa: as metricas mais baixas antes da otimizacao eram F1-Score e Precision. Portanto, a estrategia foi reduzir conteudo inventado e aumentar a semelhanca com as referencias.

## Resultados Finais

Prompt avaliado:

```text
alansvieceli/bug_to_user_story_v2
```

Prompt publicado no LangSmith:

[bug_to_user_story_v2](https://smith.langchain.com/prompts/bug_to_user_story_v2?organizationId=f3ee703e-98a9-497b-99f5-92d4823a79cb)

Resultado final da avaliacao:

| Metrica | v1 / inicial | v2 / otimizado |
|---|---:|---:|
| Helpfulness | 0.45 | 0.91 |
| Correctness | 0.52 | 0.90 |
| F1-Score | 0.48 | 0.90 |
| Clarity | 0.50 | 0.91 |
| Precision | 0.46 | 0.91 |
| Media geral | 0.4820 | 0.9078 |
| Status | Reprovado | Aprovado |

Resultado do prompt otimizado:

```text
Métricas Derivadas:
  - Helpfulness: 0.91 ✓
  - Correctness: 0.90 ✓

Métricas Base:
  - F1-Score: 0.90 ✓
  - Clarity: 0.91 ✓
  - Precision: 0.91 ✓

MÉDIA GERAL: 0.9078
STATUS: APROVADO - Todas as métricas >= 0.9
```

Processo de iteracao:

| Iteracao | Alteracao principal | Hipotese | Resultado |
|---|---|---|---|
| 1 | Prompt mais extrativo, menos inferencia e primeiros few-shots alinhados ao dataset | Reduzir conteudo inventado para subir F1 e Precision | Reprovado: Helpfulness 0.86, Correctness 0.81, F1 0.78, Clarity 0.88, Precision 0.84 |
| 2 | Inclusao de few-shots para casos medios e gatilho explicito para bugs complexos | Aumentar recall e aderencia ao formato das referencias | Aprovado: todas as metricas >= 0.90 |
| 3 | Reforco do caso offline-first e escape de chaves literais em endpoints de exemplo | Reduzir oscilacao no bug complexo de sincronizacao e evitar variaveis acidentais no LangChain | Aprovado: Helpfulness 0.91, Correctness 0.90, F1 0.90, Clarity 0.91, Precision 0.91 |

## Como Executar

### Pre-requisitos

- Python 3.9 ou superior
- Ambiente virtual Python
- Conta e API key do LangSmith
- API key de LLM configurada, usando OpenAI ou Gemini

### Configuracao

Crie e ative o ambiente virtual:

```bash
python -m venv venv
```

No Windows:

```bash
venv\Scripts\activate
```

No Linux/macOS:

```bash
source venv/bin/activate
```

Instale as dependencias:

```bash
pip install -r requirements.txt
```

Crie o arquivo `.env` a partir do template:

```bash
cp .env.example .env
```

No Windows PowerShell, se preferir:

```powershell
Copy-Item .env.example .env
```

Configure no `.env` as variaveis necessarias, como:

```text
LANGSMITH_API_KEY=
USERNAME_LANGSMITH_HUB=
LLM_PROVIDER=openai
OPENAI_API_KEY=
LLM_MODEL=gpt-4o-mini
EVAL_MODEL=gpt-4o
```

Para Gemini, configure `LLM_PROVIDER=google` e informe `GOOGLE_API_KEY`.

### 1. Fazer Pull do Prompt Inicial

```bash
python src/pull_prompts.py
```

Esse comando baixa o prompt inicial do LangSmith e salva em:

```text
prompts/bug_to_user_story_v1.yml
```

### 2. Revisar o Prompt Otimizado

O prompt otimizado esta em:

```text
prompts/bug_to_user_story_v2.yml
```

Ele contem:

- metadados;
- `system_prompt`;
- `user_prompt`;
- Few-shot Learning;
- Role Prompting;
- Skeleton of Thought;
- regras de precisao e controle de formato.

### 3. Fazer Push do Prompt Otimizado

```bash
python src/push_prompts.py
```

Esse comando publica o prompt otimizado no LangSmith Prompt Hub como:

```text
bug_to_user_story_v2
```

### 4. Executar Avaliacao

```bash
python src/evaluate.py
```

O script avalia o prompt publicado contra o dataset:

```text
datasets/bug_to_user_story.jsonl
```

As metricas calculadas sao:

- Helpfulness
- Correctness
- F1-Score
- Clarity
- Precision

O criterio de aprovacao exige todas as metricas com valor maior ou igual a `0.90`.

### 5. Rodar Testes

```bash
pytest tests/test_prompts.py
```

Os testes verificam:

- existencia de `system_prompt`;
- definicao de persona;
- mencao ao formato Markdown/User Story;
- presenca de exemplos Few-shot;
- ausencia de `[TODO]`;
- minimo de 2 tecnicas listadas nos metadados do YAML.

Resultado validado:

```text
6 passed
```

## Observacoes

O arquivo `.env` contem credenciais locais e nao deve ser versionado.

Diretorios gerados localmente, como `venv`, `.pytest_cache`, `__pycache__` e caches temporarios do pytest, tambem nao devem fazer parte do entregavel no GitHub.
