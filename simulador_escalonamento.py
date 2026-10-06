
#!/usr/bin/env python3
from dataclasses import dataclass
import sys
import tkinter as tk
from tkinter import ttk


QUANTUM_ROUND_ROBIN = 1


@dataclass(frozen=True)
class Processo:
    nome: str
    cpu: int
    prioridade: int
    ordem_original: int


@dataclass(frozen=True)
class TrechoExecucao:
    processo: str
    inicio: int
    fim: int


CENARIOS = {
    "Cenario 1": [
        Processo("P1", 3, 1, 0),
        Processo("P2", 1, 1, 1),
        Processo("P3", 2, 1, 2),
    ],
    "Cenario 2": [
        Processo("P1", 8, 1, 0),
        Processo("P2", 2, 1, 1),
        Processo("P3", 1, 1, 2),
    ],
    "Cenario 3": [
        Processo("P1", 4, 3, 0),
        Processo("P2", 2, 1, 1),
        Processo("P3", 3, 2, 2),
    ],
}

ALGORITMOS = ["FCFS", "SJF", "Prioridade", "Round Robin"]

CORES_PROCESSOS = {
    "P1": "#3b82f6",
    "P2": "#16a34a",
    "P3": "#f59e0b",
}


def simular_por_ordem(processos, processos_ordenados):
    tempo_atual = 0
    trechos = []
    terminos = {}

    for processo in processos_ordenados:
        inicio = tempo_atual
        fim = inicio + processo.cpu
        trechos.append(TrechoExecucao(processo.nome, inicio, fim))
        terminos[processo.nome] = fim
        tempo_atual = fim

    return montar_resultado(processos, trechos, terminos)


def simular_fcfs(processos):
    return simular_por_ordem(processos, processos)


def simular_sjf(processos):
    processos_ordenados = sorted(
        processos,
        key=lambda processo: (processo.cpu, processo.ordem_original),
    )
    return simular_por_ordem(processos, processos_ordenados)


def simular_prioridade(processos):
    processos_ordenados = sorted(
        processos,
        key=lambda processo: (processo.prioridade, processo.ordem_original),
    )
    return simular_por_ordem(processos, processos_ordenados)


def simular_round_robin(processos, quantum=QUANTUM_ROUND_ROBIN):
    fila = [
        {
            "processo": processo,
            "restante": processo.cpu,
        }
        for processo in processos
    ]

    tempo_atual = 0
    trechos = []
    terminos = {}

    while fila:
        item = fila.pop(0)
        processo = item["processo"]
        tempo_executado = min(quantum, item["restante"])
        inicio = tempo_atual
        fim = inicio + tempo_executado

        trechos.append(TrechoExecucao(processo.nome, inicio, fim))
        item["restante"] -= tempo_executado
        tempo_atual = fim

        if item["restante"] > 0:
            fila.append(item)
        else:
            terminos[processo.nome] = fim

    return montar_resultado(processos, trechos, terminos)


def montar_resultado(processos, trechos, terminos):
    linhas = []
    soma_espera = 0
    soma_turnaround = 0

    for processo in processos:
        turnaround = terminos[processo.nome]
        espera = turnaround - processo.cpu

        linhas.append(
            {
                "processo": processo.nome,
                "cpu": processo.cpu,
                "prioridade": processo.prioridade,
                "turnaround": turnaround,
                "espera": espera,
            }
        )

        soma_espera += espera
        soma_turnaround += turnaround

    quantidade = len(processos)

    return {
        "trechos": trechos,
        "linhas": linhas,
        "espera_media": soma_espera / quantidade,
        "turnaround_media": soma_turnaround / quantidade,
    }


def executar_algoritmo(nome_algoritmo, processos):
    if nome_algoritmo == "FCFS":
        return simular_fcfs(processos)
    if nome_algoritmo == "SJF":
        return simular_sjf(processos)
    if nome_algoritmo == "Prioridade":
        return simular_prioridade(processos)
    if nome_algoritmo == "Round Robin":
        return simular_round_robin(processos)

    raise ValueError(f"Algoritmo desconhecido: {nome_algoritmo}")


def formatar_media(valor):
    return f"{valor:.2f}".replace(".", ",")


def formatar_sequencia(trechos):
    return "\n".join(
        f"{trecho.processo} de {trecho.inicio} a {trecho.fim}"
        for trecho in trechos
    )


def formatar_gantt_texto(trechos):
    linha_processos = "".join(f"| {trecho.processo} " for trecho in trechos) + "|"
    tempos = [str(trechos[0].inicio)] + [str(trecho.fim) for trecho in trechos]
    linha_tempos = "    ".join(tempos)
    return f"{linha_processos}\n{linha_tempos}"


class AplicacaoSimulador:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Simulador de Escalonamento de Processos")
        self.janela.geometry("1080x760")
        self.janela.minsize(940, 660)

        self.cenario_var = tk.StringVar(value="Cenario 1")
        self.algoritmo_var = tk.StringVar(value="FCFS")
        self.resultado_atual = None

        self.configurar_estilo()
        self.criar_interface()
        self.atualizar_tela()

    def configurar_estilo(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("TFrame", background="#f8fafc")
        estilo.configure("TLabel", background="#f8fafc", foreground="#111827")
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 18, "bold"))
        estilo.configure("Subtitulo.TLabel", font=("Segoe UI", 11))
        estilo.configure("Resumo.TLabel", font=("Segoe UI", 12, "bold"))
        estilo.configure("TButton", padding=8)
        estilo.configure("TRadiobutton", background="#f8fafc")
        estilo.configure("TLabelframe", background="#f8fafc")
        estilo.configure("TLabelframe.Label", background="#f8fafc", font=("Segoe UI", 10, "bold"))
        estilo.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def criar_interface(self):
        principal = ttk.Frame(self.janela, padding=16)
        principal.grid(row=0, column=0, sticky="nsew")

        self.janela.columnconfigure(0, weight=1)
        self.janela.rowconfigure(0, weight=1)
        principal.columnconfigure(1, weight=1)
        principal.rowconfigure(1, weight=1)

        cabecalho = ttk.Frame(principal)
        cabecalho.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        cabecalho.columnconfigure(0, weight=1)

        ttk.Label(
            cabecalho,
            text="Simulador de Escalonamento de Processos",
            style="Titulo.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            cabecalho,
            text=f"Uma CPU, todos os processos chegam no instante 0, quantum = {QUANTUM_ROUND_ROBIN}",
            style="Subtitulo.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        controles = ttk.Frame(principal, width=220)
        controles.grid(row=1, column=0, sticky="ns", padx=(0, 16))
        controles.grid_propagate(False)

        self.criar_controles(controles)
        self.criar_painel_resultados(principal)

    def criar_controles(self, pai):
        grupo_cenario = ttk.LabelFrame(pai, text="Cenario")
        grupo_cenario.pack(fill="x", pady=(0, 12))

        for cenario in CENARIOS:
            ttk.Radiobutton(
                grupo_cenario,
                text=cenario,
                value=cenario,
                variable=self.cenario_var,
                command=self.atualizar_tela,
            ).pack(anchor="w", padx=10, pady=6)

        grupo_algoritmo = ttk.LabelFrame(pai, text="Algoritmo")
        grupo_algoritmo.pack(fill="x", pady=(0, 12))

        for algoritmo in ALGORITMOS:
            ttk.Radiobutton(
                grupo_algoritmo,
                text=algoritmo,
                value=algoritmo,
                variable=self.algoritmo_var,
                command=self.atualizar_tela,
            ).pack(anchor="w", padx=10, pady=6)

        ttk.Button(
            pai,
            text="Executar simulacao",
            command=self.atualizar_tela,
        ).pack(fill="x", pady=(0, 8))

        ttk.Button(
            pai,
            text="Mostrar 12 execucoes",
            command=self.abrir_janela_todos_resultados,
        ).pack(fill="x")

        grupo_info = ttk.LabelFrame(pai, text="Dados fixos")
        grupo_info.pack(fill="x", pady=(12, 0))
        ttk.Label(grupo_info, text="Processos: P1, P2 e P3").pack(anchor="w", padx=10, pady=(8, 4))
        ttk.Label(grupo_info, text="Chegada: instante 0").pack(anchor="w", padx=10, pady=4)
        ttk.Label(grupo_info, text=f"Quantum RR: {QUANTUM_ROUND_ROBIN}").pack(anchor="w", padx=10, pady=(4, 8))

    def criar_painel_resultados(self, principal):
        painel = ttk.Frame(principal)
        painel.grid(row=1, column=1, sticky="nsew")
        painel.columnconfigure(0, weight=1)
        painel.rowconfigure(3, weight=1)

        tabela_processos_frame = ttk.LabelFrame(painel, text="Processos do cenario")
        tabela_processos_frame.grid(row=0, column=0, sticky="ew")
        tabela_processos_frame.columnconfigure(0, weight=1)

        self.tabela_processos = ttk.Treeview(
            tabela_processos_frame,
            columns=("processo", "cpu", "prioridade"),
            show="headings",
            height=3,
        )
        self.tabela_processos.heading("processo", text="Processo")
        self.tabela_processos.heading("cpu", text="CPU")
        self.tabela_processos.heading("prioridade", text="Prioridade")
        self.tabela_processos.column("processo", anchor="center", width=120)
        self.tabela_processos.column("cpu", anchor="center", width=80)
        self.tabela_processos.column("prioridade", anchor="center", width=100)
        self.tabela_processos.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        resultado_frame = ttk.LabelFrame(painel, text="Resultado da execucao")
        resultado_frame.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        resultado_frame.columnconfigure(0, weight=1)

        self.label_algoritmo = ttk.Label(resultado_frame, text="", style="Resumo.TLabel")
        self.label_algoritmo.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))

        self.texto_sequencia = tk.Text(
            resultado_frame,
            height=6,
            wrap="word",
            font=("Consolas", 10),
            bg="#ffffff",
            relief="solid",
            borderwidth=1,
        )
        self.texto_sequencia.grid(row=1, column=0, sticky="ew", padx=8, pady=8)
        self.texto_sequencia.configure(state="disabled")

        self.gantt_canvas = tk.Canvas(
            resultado_frame,
            height=130,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#d1d5db",
        )
        self.gantt_canvas.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        self.gantt_canvas.bind("<Configure>", lambda _evento: self.desenhar_gantt())

        tabela_resultados_frame = ttk.LabelFrame(painel, text="Tabela de resultados")
        tabela_resultados_frame.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        tabela_resultados_frame.columnconfigure(0, weight=1)

        self.tabela_resultados = ttk.Treeview(
            tabela_resultados_frame,
            columns=("processo", "cpu", "prioridade", "turnaround", "espera"),
            show="headings",
            height=3,
        )
        cabecalhos = {
            "processo": "Processo",
            "cpu": "CPU",
            "prioridade": "Prioridade",
            "turnaround": "Turnaround",
            "espera": "Espera",
        }
        for coluna, texto in cabecalhos.items():
            self.tabela_resultados.heading(coluna, text=texto)
            self.tabela_resultados.column(coluna, anchor="center", width=110)
        self.tabela_resultados.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        medias = ttk.Frame(tabela_resultados_frame)
        medias.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        medias.columnconfigure(0, weight=1)
        medias.columnconfigure(1, weight=1)

        self.label_espera_media = ttk.Label(medias, text="", style="Resumo.TLabel")
        self.label_espera_media.grid(row=0, column=0, sticky="w")
        self.label_turnaround_media = ttk.Label(medias, text="", style="Resumo.TLabel")
        self.label_turnaround_media.grid(row=0, column=1, sticky="w")

        comparacao_frame = ttk.LabelFrame(painel, text="Comparacao do cenario")
        comparacao_frame.grid(row=3, column=0, sticky="nsew", pady=(12, 0))
        comparacao_frame.columnconfigure(0, weight=1)
        comparacao_frame.rowconfigure(0, weight=1)

        self.tabela_comparacao = ttk.Treeview(
            comparacao_frame,
            columns=("algoritmo", "espera_media", "turnaround_media"),
            show="headings",
            height=4,
        )
        self.tabela_comparacao.heading("algoritmo", text="Algoritmo")
        self.tabela_comparacao.heading("espera_media", text="Espera media")
        self.tabela_comparacao.heading("turnaround_media", text="Turnaround medio")
        self.tabela_comparacao.column("algoritmo", anchor="center", width=160)
        self.tabela_comparacao.column("espera_media", anchor="center", width=120)
        self.tabela_comparacao.column("turnaround_media", anchor="center", width=140)
        self.tabela_comparacao.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

    def atualizar_tela(self):
        cenario = self.cenario_var.get()
        algoritmo = self.algoritmo_var.get()
        processos = CENARIOS[cenario]

        self.preencher_processos(processos)
        self.resultado_atual = executar_algoritmo(algoritmo, processos)
        self.preencher_resultado(algoritmo, self.resultado_atual)
        self.preencher_comparacao(cenario, processos)

    def preencher_processos(self, processos):
        self.limpar_tabela(self.tabela_processos)
        for processo in processos:
            self.tabela_processos.insert(
                "",
                "end",
                values=(processo.nome, processo.cpu, processo.prioridade),
            )

    def preencher_resultado(self, algoritmo, resultado):
        self.label_algoritmo.configure(text=f"Algoritmo: {algoritmo}")
        self.escrever_texto(
            self.texto_sequencia,
            formatar_sequencia(resultado["trechos"])
            + "\n\n"
            + formatar_gantt_texto(resultado["trechos"]),
        )

        self.limpar_tabela(self.tabela_resultados)
        for linha in resultado["linhas"]:
            self.tabela_resultados.insert(
                "",
                "end",
                values=(
                    linha["processo"],
                    linha["cpu"],
                    linha["prioridade"],
                    linha["turnaround"],
                    linha["espera"],
                ),
            )

        self.label_espera_media.configure(
            text=f"Espera media: {formatar_media(resultado['espera_media'])}"
        )
        self.label_turnaround_media.configure(
            text=f"Turnaround medio: {formatar_media(resultado['turnaround_media'])}"
        )

        self.desenhar_gantt()

    def preencher_comparacao(self, cenario, processos):
        self.limpar_tabela(self.tabela_comparacao)
        for algoritmo in ALGORITMOS:
            resultado = executar_algoritmo(algoritmo, processos)
            self.tabela_comparacao.insert(
                "",
                "end",
                values=(
                    algoritmo,
                    formatar_media(resultado["espera_media"]),
                    formatar_media(resultado["turnaround_media"]),
                ),
            )

    def desenhar_gantt(self):
        if not self.resultado_atual:
            return

        trechos = self.resultado_atual["trechos"]
        self.gantt_canvas.delete("all")

        largura = max(self.gantt_canvas.winfo_width(), 600)
        margem_x = 36
        y1 = 34
        y2 = 82
        tempo_total = trechos[-1].fim
        escala = (largura - (margem_x * 2)) / tempo_total

        for trecho in trechos:
            x1 = margem_x + trecho.inicio * escala
            x2 = margem_x + trecho.fim * escala
            cor = CORES_PROCESSOS.get(trecho.processo, "#64748b")

            self.gantt_canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=cor,
                outline="#111827",
            )
            self.gantt_canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text=trecho.processo,
                fill="#ffffff",
                font=("Segoe UI", 11, "bold"),
            )

        tempos = [trechos[0].inicio] + [trecho.fim for trecho in trechos]
        for tempo in tempos:
            x = margem_x + tempo * escala
            self.gantt_canvas.create_line(x, y2, x, y2 + 8, fill="#111827")
            self.gantt_canvas.create_text(
                x,
                y2 + 22,
                text=str(tempo),
                fill="#111827",
                font=("Segoe UI", 10),
            )

    def abrir_janela_todos_resultados(self):
        janela = tk.Toplevel(self.janela)
        janela.title("12 execucoes")
        janela.geometry("760x640")

        texto = tk.Text(janela, wrap="word", font=("Consolas", 10))
        texto.pack(fill="both", expand=True, padx=12, pady=12)
        texto.insert("1.0", gerar_texto_todos_resultados())
        texto.configure(state="disabled")

    @staticmethod
    def limpar_tabela(tabela):
        for item in tabela.get_children():
            tabela.delete(item)

    @staticmethod
    def escrever_texto(caixa_texto, conteudo):
        caixa_texto.configure(state="normal")
        caixa_texto.delete("1.0", "end")
        caixa_texto.insert("1.0", conteudo)
        caixa_texto.configure(state="disabled")


def gerar_texto_todos_resultados():
    partes = []

    for nome_cenario, processos in CENARIOS.items():
        partes.append(f"=== {nome_cenario} ===")
        for algoritmo in ALGORITMOS:
            resultado = executar_algoritmo(algoritmo, processos)
            partes.append(f"\nAlgoritmo: {algoritmo}")
            partes.append("Sequencia:")
            partes.append(formatar_sequencia(resultado["trechos"]))
            partes.append("Gantt:")
            partes.append(formatar_gantt_texto(resultado["trechos"]))
            partes.append("Resultados:")
            partes.append("Processo | CPU | Prioridade | Turnaround | Espera")

            for linha in resultado["linhas"]:
                partes.append(
                    f"{linha['processo']:>8} | "
                    f"{linha['cpu']:>3} | "
                    f"{linha['prioridade']:>10} | "
                    f"{linha['turnaround']:>10} | "
                    f"{linha['espera']:>6}"
                )

            partes.append(
                f"Espera media: {formatar_media(resultado['espera_media'])}"
            )
            partes.append(
                f"Turnaround medio: {formatar_media(resultado['turnaround_media'])}"
            )

        partes.append("")

    return "\n".join(partes)


def executar_no_console():
    print(gerar_texto_todos_resultados())


def executar_interface():
    janela = tk.Tk()
    AplicacaoSimulador(janela)
    janela.mainloop()


if __name__ == "__main__":
    if "--console" in sys.argv:
        executar_no_console()
    else:
        executar_interface()
