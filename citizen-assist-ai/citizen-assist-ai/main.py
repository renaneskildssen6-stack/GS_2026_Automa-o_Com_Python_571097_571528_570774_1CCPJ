"""Citizen Assist AI - assistente de terminal para jovens no primeiro emprego.
Execute com: python main.py"""

import os
import sys

from base_conhecimento import BaseConhecimento
from assistente import Assistente


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass

    pasta = os.path.dirname(os.path.abspath(__file__))
    base = BaseConhecimento(os.path.join(pasta, "data", "base_conhecimento.csv"))
    base.carregar()  # usa open(), for e split() para ler a base

    assistente = Assistente("Citizen Assist AI", base)
    try:
        assistente.menu()
    except KeyboardInterrupt:
        print("\n\nEncerrando...")
        assistente.exportar_csv()


if __name__ == "__main__":
    main()
