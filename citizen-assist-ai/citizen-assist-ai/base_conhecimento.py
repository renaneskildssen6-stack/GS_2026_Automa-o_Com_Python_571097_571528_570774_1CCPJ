"""Classe BaseConhecimento: lê o CSV, lista categorias e busca a melhor orientação."""

from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ü": "u",
           "ç": "c", "º": "", "ª": ""}

# Palavras muito comuns que não devem ganhar ponto por aparecerem no título.
PALAVRAS_COMUNS = ("como", "para", "onde", "qual", "quais", "quem", "sobre",
                   "minha", "meus", "minhas", "tenho", "posso", "preciso",
                   "quero", "isso", "esse", "essa", "pelo", "pela", "uma")

CAMPOS = ["id", "categoria", "titulo", "palavras_chave", "resposta",
          "documentos", "onde", "fonte", "verificado_em"]


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação. Devolve o texto com espaço nas pontas
    (assim ' cpf ' só casa com a palavra inteira, nunca com pedaço de outra palavra)."""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()-/":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []  # lista de objetos Orientacao

    def carregar(self):
        """Lê o CSV com open() + for + split(';'). Nunca derruba o programa:
        arquivo ausente, cabeçalho inválido ou linha quebrada viram avisos."""
        self.orientacoes = []
        try:
            with open(self.caminho, "r", encoding="utf-8-sig") as arquivo:
                linhas = arquivo.readlines()
        except (OSError, UnicodeDecodeError):
            print(f"Aviso: não consegui abrir a base de conhecimento ({self.caminho}).")
            return 0

        if not linhas or linhas[0].strip().split(";") != CAMPOS:
            print("Aviso: base de conhecimento com formato inválido (cabeçalho incorreto).")
            return 0

        ignoradas = 0
        for linha in linhas[1:]:
            linha = linha.strip()
            if linha == "":
                continue
            partes = linha.split(";")
            if len(partes) != len(CAMPOS):
                ignoradas += 1
                continue
            registro = dict(zip(CAMPOS, partes))          # dicionário: campo -> valor
            if not registro["id"].isdigit():
                ignoradas += 1
                continue
            palavras = [p.strip() for p in registro["palavras_chave"].split("|") if p.strip()]
            documentos = [d.strip() for d in registro["documentos"].split("|") if d.strip()]
            if not palavras:
                ignoradas += 1
                continue
            self.orientacoes.append(Orientacao(
                int(registro["id"]), registro["categoria"], registro["titulo"],
                palavras, registro["resposta"], documentos, registro["onde"],
                registro["fonte"], registro["verificado_em"]))

        if ignoradas:
            print(f"Aviso: {ignoradas} linha(s) inválida(s) da base foram ignoradas.")
        return len(self.orientacoes)

    def categorias(self):
        """Lista de categorias, sem repetição, na ordem em que aparecem."""
        lista = []
        for o in self.orientacoes:
            if o.categoria not in lista:
                lista.append(o.categoria)
        return lista

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta_norm, orientacao):
        """+3 por palavra-chave que aparece na pergunta;
        +1 por palavra da pergunta (4+ letras) que aparece no título."""
        pontos = 0
        for chave in orientacao.palavras_chave:
            if normalizar(chave) in pergunta_norm:
                pontos += 3
        titulo_norm = normalizar(orientacao.titulo)
        for palavra in set(pergunta_norm.split()):
            if len(palavra) >= 4 and palavra not in PALAVRAS_COMUNS:
                if " " + palavra + " " in titulo_norm:
                    pontos += 1
        return pontos

    def buscar(self, pergunta):
        """Devolve lista de tuplas (pontos, orientacao), da maior para a menor pontuação."""
        pergunta_norm = normalizar(pergunta)
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta_norm, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda tupla: tupla[0], reverse=True)
        return resultados
