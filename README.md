# Citizen Assist AI

Assistente de terminal em Python que orienta **jovens no primeiro emprego** com informações de fontes oficiais, mostrando a fonte, a data de verificação e o aviso de limitação, **sem coletar dados pessoais**.

> GS2026.2 – Pensamento Computacional e Automação com Python (FIAP) – desafio CitizenTech

## Integrantes
| Nome | RM |
|------|----|
| Renan Eskildssen | 571097 |
| Lucas Barros | 571528 |
| Murillo Boyajian | 570774 |

## Público e problema
**Público:** jovens que estão arrumando o primeiro emprego.
**Problema:** a informação sobre CPF, Carteira de Trabalho Digital, direitos, FGTS etc. existe, mas está espalhada, em linguagem técnica e misturada com sites que parecem oficiais e não são.

## ODS relacionados
- **ODS 8** – Trabalho decente e crescimento econômico
- **ODS 10** – Redução das desigualdades
- **ODS 16** – Paz, justiça e instituições eficazes (acesso à informação)

## Como executar
Requisitos: Python 3.8+ (nenhuma biblioteca externa).
```bash
git clone <link do repositório>
cd citizen-assist-ai
python main.py
```

## Estrutura
```
citizen-assist-ai/
├── README.md
├── main.py              # inicia o programa
├── orientacao.py        # classe Orientacao (um registro do CSV)
├── base_conhecimento.py # classe BaseConhecimento (ler CSV, categorias, buscar)
├── assistente.py        # classe Assistente (atendimento, histórico, indicadores)
└── data/
    ├── base_conhecimento.csv  # 14 orientações, 3 categorias
    ├── historico.csv          # um atendimento por linha (gravado na hora)
    ├── atendimentos.csv       # exportação completa dos atendimentos
    └── notas.csv              # notas de facilidade de uso (1 a 5)
```
Composição: `Assistente` → `base: BaseConhecimento` → `orientacoes: [Orientacao, ...]`.

## Regra de pontuação
A pergunta e os textos da base são normalizados (minúsculas, sem acento, sem pontuação).
| Regra | Pontos |
|-------|--------|
| Palavra-chave da orientação aparece na pergunta (palavra inteira) | +3 |
| Palavra da pergunta com 4+ letras aparece no título | +1 |

- **6 pontos ou mais:** confiança ALTA · **3 a 5:** confiança MÉDIA · **menos de 3:** "não encontrei", com sugestão de outras palavras e das categorias.
- `buscar()` devolve uma lista de tuplas `(pontos, orientacao)` da maior para a menor pontuação. O assistente mostra a melhor e até duas alternativas.
- **Ajuste da equipe:** palavras muito comuns (como, para, onde, qual...) não ganham ponto no título, para não dar pontos a toda orientação. A lista está em `PALAVRAS_COMUNS`.

## Regras de atendimento
- Navegação por categorias, com "0 para voltar" em todas as telas.
- Entradas inválidas (fora da faixa, letras, vazio, s/n inválido) nunca encerram o programa.
- Pergunta com 8 ou mais dígitos ou com `@` é recusada e **não é registrada**.
- Toda resposta mostra fonte, data de verificação e o aviso "este assistente NÃO é um canal oficial".
- Base ausente ou com formato inválido gera aviso, sem interromper o programa.

## Indicadores
Resposta encontrada (%), taxa de acerto (ajudou %), tempo médio para encontrar, tentativas por atendimento, facilidade de uso (nota 1 a 5 pedida ao sair) e lista de dúvidas sem solução.

## Integrações com outras disciplinas
_Nenhuma (opcional). Se a equipe integrar algo, descreva aqui._

## Fontes consultadas
Receita Federal, TSE, gov.br, Ministério da Defesa, Ministério do Trabalho e Emprego, Caixa, INSS, Banco Central e Planalto (Leis 11.788/2008 e 7.418/1985). Os links e as datas de conferência estão em cada linha de `data/base_conhecimento.csv`.

## Resultado do teste com usuários
_Preencher depois do teste com pelo menos 3 pessoas de fora da equipe (10 atendimentos ou mais). Não registrar nomes nem dados dessas pessoas._

- Pessoas testadas / atendimentos: _
- Indicadores obtidos: _
- Dúvidas sem solução: _
- Melhoria feita a partir do teste (ex.: nova palavra-chave): _

## Limitações
- A busca é por regras: não entende sinônimos nem erros de digitação que não estejam nas palavras-chave.
- A base é pequena (14 orientações) e precisa ser reconferida nas fontes oficiais de tempos em tempos.
- O assistente não é um canal oficial e não substitui o atendimento do órgão responsável.

## Vídeo técnico
_Link do YouTube (não listado): preencher_
