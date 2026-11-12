"""Classe Orientacao: representa UMA linha da base de conhecimento (um registro do CSV)."""


class Orientacao:
    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id                          # int
        self.categoria = categoria            # str
        self.titulo = titulo                  # str
        self.palavras_chave = palavras_chave  # lista de str (campo separado por |)
        self.resposta = resposta              # str
        self.documentos = documentos          # lista de str (campo separado por |)
        self.onde = onde                      # str
        self.fonte = fonte                    # str (link oficial)
        self.verificado_em = verificado_em    # str AAAA-MM-DD

    def exibir(self):
        """Mostra a orientação na tela (fonte, data de verificação e aviso incluídos)."""
        print(f"\n>> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        if self.documentos:
            print("Documentos necessários:")
            for doc in self.documentos:
                print(f"  - {doc}")
        else:
            print("Documentos necessários: nenhum informado")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print("Aviso: este assistente NÃO é um canal oficial.")
