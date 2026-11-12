"""Classe Assistente: faz o atendimento, guarda o histórico e calcula os indicadores."""

import os
import time
from datetime import datetime

CAMPOS_HIST = ["data", "origem", "pergunta", "id_orientacao",
               "encontrou", "ajudou", "tentativas", "tempo_s"]


def contem_dado_pessoal(texto):
    """8 ou mais dígitos (CPF, telefone...) ou '@' (e-mail) => dado pessoal."""
    digitos = sum(1 for letra in texto if letra.isdigit())
    return digitos >= 8 or "@" in texto


def nivel_confianca(pontos):
    if pontos >= 6:
        return "ALTA"
    if pontos >= 3:
        return "MÉDIA"
    return None


class Assistente:
    def __init__(self, nome, base):
        self.nome = nome
        self.base = base                     # composição: Assistente TEM uma BaseConhecimento
        pasta = os.path.dirname(base.caminho) or "."
        self.arq_historico = os.path.join(pasta, "historico.csv")
        self.arq_atendimentos = os.path.join(pasta, "atendimentos.csv")
        self.arq_notas = os.path.join(pasta, "notas.csv")
        self.historico = []                  # lista de dicionários (um por atendimento)
        self.notas = []                      # notas de facilidade de uso (1 a 5)
        self.entrada_encerrada = False
        self._carregar_historico()
        self._carregar_notas()

    # ---------- entrada segura ----------
    def ler(self, texto):
        try:
            return input(texto).strip()
        except EOFError:
            self.entrada_encerrada = True
            return "0"

    def ler_opcao(self, maximo):
        """Pede um número de 0 a maximo. Opção inválida nunca encerra o programa."""
        while True:
            entrada = self.ler("Escolha uma opção: ")
            if entrada.isdigit() and 0 <= int(entrada) <= maximo:
                return int(entrada)
            print(f"Opção inválida. Digite um número de 0 a {maximo}.")

    def ler_sn(self, texto):
        while True:
            entrada = self.ler(texto).lower()
            if entrada in ("s", "n"):
                return entrada == "s"
            if self.entrada_encerrada:
                return False
            print("Resposta inválida. Digite s ou n.")

    # ---------- histórico ----------
    def _carregar_historico(self):
        try:
            with open(self.arq_historico, "r", encoding="utf-8") as arquivo:
                linhas = arquivo.readlines()
        except (OSError, UnicodeDecodeError):
            return
        for linha in linhas[1:]:
            partes = linha.strip().split(";")
            if len(partes) != len(CAMPOS_HIST):
                continue
            registro = dict(zip(CAMPOS_HIST, partes))
            try:
                registro["tentativas"] = int(registro["tentativas"])
                registro["tempo_s"] = float(registro["tempo_s"])
            except ValueError:
                continue
            self.historico.append(registro)

    def _carregar_notas(self):
        try:
            with open(self.arq_notas, "r", encoding="utf-8") as arquivo:
                linhas = arquivo.readlines()
        except (OSError, UnicodeDecodeError):
            return
        for linha in linhas[1:]:
            partes = linha.strip().split(";")
            if len(partes) == 2 and partes[1].isdigit() and 1 <= int(partes[1]) <= 5:
                self.notas.append(int(partes[1]))

    def _anexar_linha(self, caminho, cabecalho, linha):
        """Acrescenta uma linha ao arquivo (cria com cabeçalho se não existir)."""
        try:
            novo = not os.path.exists(caminho) or os.path.getsize(caminho) == 0
            with open(caminho, "a", encoding="utf-8") as arquivo:
                if novo:
                    arquivo.write(cabecalho + "\n")
                arquivo.write(linha + "\n")
        except OSError:
            print(f"Aviso: não consegui gravar em {caminho}.")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, inicio):
        """Guarda o atendimento na memória e em data/historico.csv."""
        pergunta = pergunta.replace(";", ",").replace("\n", " ").replace("\r", " ")
        registro = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": str(id_orientacao),
            "encontrou": "sim" if encontrou else "nao",
            "ajudou": "sim" if ajudou else "nao",
            "tentativas": tentativas,
            "tempo_s": round(time.time() - inicio, 1),
        }
        self.historico.append(registro)
        linha = ";".join(str(registro[campo]) for campo in CAMPOS_HIST)
        self._anexar_linha(self.arq_historico, ";".join(CAMPOS_HIST), linha)

    # ---------- atendimento por pergunta ----------
    def perguntar(self):
        inicio = time.time()
        tentativas = 0
        encontrou = False
        ajudou = False
        id_orientacao = ""
        ultima_pergunta = ""

        while True:
            texto = self.ler("\nDigite sua dúvida (0 para voltar): ")
            if texto == "0":
                break
            if texto == "":
                print("Você não digitou nada. Escreva sua dúvida ou digite 0 para voltar.")
                continue
            if contem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue  # recusada e NÃO registrada

            tentativas += 1
            ultima_pergunta = texto
            resultados = [t for t in self.base.buscar(texto) if t[0] >= 3]

            if not resultados:
                encontrou = False
                id_orientacao = ""
                print("\nNão encontrei uma orientação para essa dúvida.")
                print("Tente outras palavras (ex.: o nome do documento ou do serviço)")
                categorias = self.base.categorias()
                if categorias:
                    print("ou use a navegação por categorias (opção 2 do menu): "
                          + ", ".join(categorias) + ".")
                continue

            pontos, melhor = resultados[0]
            encontrou = True
            id_orientacao = melhor.id
            print(f"\nConfiança da resposta: {nivel_confianca(pontos)} ({pontos} pontos)")
            melhor.exibir()
            alternativas = resultados[1:3]
            if alternativas:
                print("\nTalvez também ajude:")
                for pts, alt in alternativas:
                    print(f"  - {alt.titulo} [{alt.categoria}] ({pts} pontos)")

            if self.ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): "):
                ajudou = True
                break
            print("Tudo bem. Tente reescrever a dúvida com outras palavras.")

        if tentativas > 0:
            self.registrar("pergunta", ultima_pergunta, id_orientacao,
                           encontrou, ajudou, tentativas, inicio)

    # ---------- atendimento por categorias ----------
    def navegar(self):
        categorias = self.base.categorias()
        if not categorias:
            print("\nA base de conhecimento está vazia. Não há categorias para mostrar.")
            return

        inicio = time.time()
        tentativas = 0
        ultima = None
        ajudou = False

        while not ajudou:
            print("\n=== Categorias ===")
            for i, categoria in enumerate(categorias, start=1):
                print(f"{i}. {categoria}")
            print("0. Voltar")
            escolha = self.ler_opcao(len(categorias))
            if escolha == 0:
                break
            categoria = categorias[escolha - 1]
            orientacoes = self.base.por_categoria(categoria)

            while not ajudou:
                print(f"\n=== {categoria} ===")
                for i, o in enumerate(orientacoes, start=1):
                    print(f"{i}. {o.titulo}")
                print("0. Voltar")
                escolha_o = self.ler_opcao(len(orientacoes))
                if escolha_o == 0:
                    break
                ultima = orientacoes[escolha_o - 1]
                tentativas += 1
                ultima.exibir()
                if self.ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): "):
                    ajudou = True

        if tentativas > 0:
            self.registrar("categoria", ultima.titulo, ultima.id,
                           True, ajudou, tentativas, inicio)

    # ---------- indicadores e exportação ----------
    def indicadores(self):
        total = len(self.historico)
        print("\n=== Indicadores ===")
        if total == 0:
            print("Ainda não há atendimentos registrados.")
            return {}

        encontrados = [h for h in self.historico if h["encontrou"] == "sim"]
        ajudados = [h for h in self.historico if h["ajudou"] == "sim"]
        pct_encontrada = round(100 * len(encontrados) / total, 1)
        pct_ajudou = round(100 * len(ajudados) / total, 1)
        if encontrados:
            tempo_medio = round(sum(h["tempo_s"] for h in encontrados) / len(encontrados), 1)
        else:
            tempo_medio = 0.0
        tentativas_media = round(sum(h["tentativas"] for h in self.historico) / total, 1)
        if self.notas:
            facilidade = round(sum(self.notas) / len(self.notas), 1)
        else:
            facilidade = None

        sem_solucao = []
        for h in self.historico:
            if h["ajudou"] != "sim" and h["pergunta"] not in sem_solucao:
                sem_solucao.append(h["pergunta"])

        print(f"Atendimentos registrados: {total}")
        print(f"Resposta encontrada (%): {pct_encontrada}")
        print(f"Taxa de acerto - ajudou (%): {pct_ajudou}")
        print(f"Tempo médio para encontrar: {tempo_medio} s")
        print(f"Tentativas por atendimento: {tentativas_media}")
        print("Facilidade de uso (1 a 5): "
              + (str(facilidade) if facilidade is not None else "sem notas ainda"))
        print("Dúvidas sem solução:")
        if sem_solucao:
            for pergunta in sem_solucao:
                print(f"  - {pergunta}")
        else:
            print("  (nenhuma)")
        return {"total": total, "encontrada": pct_encontrada, "acerto": pct_ajudou,
                "tempo_medio": tempo_medio, "tentativas": tentativas_media,
                "facilidade": facilidade, "sem_solucao": sem_solucao}

    def exportar_csv(self):
        """Exporta todos os atendimentos para data/atendimentos.csv (open + write, separador ;)."""
        try:
            with open(self.arq_atendimentos, "w", encoding="utf-8") as arquivo:
                arquivo.write(";".join(CAMPOS_HIST) + "\n")
                for h in self.historico:
                    arquivo.write(";".join(str(h[campo]) for campo in CAMPOS_HIST) + "\n")
            print(f"Atendimentos exportados para {self.arq_atendimentos}.")
        except OSError:
            print("Aviso: não consegui exportar o arquivo de atendimentos.")

    def pedir_nota(self):
        """Ao sair: nota de facilidade de 1 a 5 (0 para pular)."""
        while True:
            entrada = self.ler("De 1 a 5, quão fácil foi usar o assistente? (0 para pular): ")
            if entrada == "0":
                return
            if entrada.isdigit() and 1 <= int(entrada) <= 5:
                nota = int(entrada)
                self.notas.append(nota)
                data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._anexar_linha(self.arq_notas, "data;nota", f"{data};{nota}")
                return
            print("Nota inválida. Digite um número de 1 a 5.")

    # ---------- menu principal ----------
    def menu(self):
        print(f"\n===== {self.nome} =====")
        print("Orientações para jovens no primeiro emprego, com fonte oficial.")
        print("Aviso: este assistente NÃO é um canal oficial. Não digite dados pessoais.")
        if not self.base.orientacoes:
            print("Aviso: a base de conhecimento está vazia. Verifique data/base_conhecimento.csv.")

        while True:
            print("\n=== Menu ===")
            print("1. Fazer uma pergunta")
            print("2. Navegar por categorias")
            print("3. Ver indicadores")
            print("4. Exportar atendimentos (CSV)")
            print("0. Sair")
            opcao = self.ler_opcao(4)
            if opcao == 1:
                self.perguntar()
            elif opcao == 2:
                self.navegar()
            elif opcao == 3:
                self.indicadores()
            elif opcao == 4:
                self.exportar_csv()
            else:
                break
            if self.entrada_encerrada:
                break
        self.finalizar()

    def finalizar(self):
        self.pedir_nota()
        self.indicadores()
        self.exportar_csv()
        print("\nObrigado por usar o assistente. Até logo!")
