import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import threading

class MarkitdownConverterApp:
    def __init__(self, logger):
        self.logger = logger

        self.root = tk.Tk()
        self.root.title("Markitdown Converter")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        self.arquivos = []
        self.destino = ""
        self.criar_widgets()

    def criar_widgets(self):
        frame_selecao = ttk.LabelFrame(self.root, text="Seleção de arquivos")
        frame_selecao.pack(fill="x", padx=10, pady=8)

        btn_selecionar = ttk.Button(frame_selecao, text="Selecionar arquivos", command=self.selecionar_arquivos)
        btn_selecionar.pack(side="left", padx=5, pady=5)
        self.lbl_arquivos = ttk.Label(frame_selecao, text="Nenhum arquivo selecionado...")
        self.lbl_arquivos.pack(side="left", padx=5)

        frame_destino = ttk.LabelFrame(self.root, text="Diretório de saída")
        frame_destino.pack(fill="x", padx=10, pady=8)
        btn_destino = ttk.Button(frame_destino, text="Escolher pasta", command=self.selecionar_destino)
        btn_destino.pack(side="left", padx=5, pady=5)
        self.lbl_destino = ttk.Label(frame_destino, text="Nenhuma pasta selecionada")
        self.lbl_destino.pack(side="left", padx=5)

        frame_progresso = ttk.Frame(self.root)
        frame_progresso.pack(fill="x", padx=10, pady=(0,8))
        self.progress = ttk.Progressbar(frame_progresso, mode='determinate')
        self.progress.pack(fill="x", expand=True, padx=5, pady=5)

        frame_logs = ttk.LabelFrame(self.root, text="Terminal de logs")
        frame_logs.pack(fill="both", expand=True, padx=10, pady=(0,8))
        self.text_logs = scrolledtext.ScrolledText(frame_logs, height=12, state='disabled', font=('Consolas', 10))
        self.text_logs.pack(fill="both", expand=True, padx=5, pady=5)

        frame_botoes = ttk.Frame(self.root)
        frame_botoes.pack(fill="x", padx=10, pady=8)
        ttk.Button(frame_botoes, text="Converter Selecionado", command=self.converter_selecionado_thread).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Conversão em Lote", command=self.converter_batch_thread).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Sair", command=self.root.quit).pack(side="right", padx=5)

    def selecionar_arquivos(self):
        arquivos = filedialog.askopenfilenames(
            title="Selecione arquivos para converter",
            filetypes=[
                ("Todos suportados", "*.pdf *.ppt *.pptx *.docx *.json *.txt *.csv *.xlsx"),
                ("PDF", "*.pdf"), ("PPT/PPTX", "*.ppt;*.pptx"),
                ("DOCX", "*.docx"), ("JSON", "*.json"),
                ("TXT", "*.txt"), ("CSV", "*.csv"), ("XLSX", "*.xlsx")
            ]
        )
        self.arquivos = list(arquivos)
        self.lbl_arquivos.config(text=f"{len(arquivos)} arquivo(s) selecionado(s)" if arquivos else "Nenhum arquivo selecionado...")

    def selecionar_destino(self):
        destino = filedialog.askdirectory(title="Escolher diretório de saída")
        if destino:
            self.destino = destino
            self.lbl_destino.config(text=destino)
        else:
            self.lbl_destino.config(text="Nenhuma pasta selecionada")

    def log(self, mensagem):
        self.text_logs['state'] = 'normal'
        self.text_logs.insert('end', mensagem + '\n')
        self.text_logs.see('end')
        self.text_logs['state'] = 'disabled'
        self.logger.info(mensagem)

    def converter_selecionado_thread(self):
        threading.Thread(target=self.converter_selecionado).start()

    def converter_selecionado(self):
        if not self.arquivos or not self.destino:
            messagebox.showwarning("Aviso", "Selecione arquivos e diretório de saída.")
            return
        from converter.file_converter import FileConverter
        self.progress.config(value=0, maximum=len(self.arquivos))
        for idx, arquivo in enumerate(self.arquivos, 1):
            try:
                self.log(f"Convertendo: {arquivo}")
                FileConverter.converter(arquivo, self.destino, self.log)
                self.progress.config(value=idx)
            except Exception as e:
                self.log(f"[ERRO] {arquivo}: {str(e)}")
        self.log("Conversão concluída.")

    def converter_batch_thread(self):
        threading.Thread(target=self.converter_batch).start()

    def converter_batch(self):
        self.converter_selecionado()  # Aqui pode expandir para lógica em lote

    def run(self):
        self.root.mainloop()
