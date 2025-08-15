import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
from converter.file_converter import FileConverter
from utils.security import SecurityValidator

class MarkitdownConverterApp:
    def __init__(self, logger):
        self.logger = logger
        self.file_converter = FileConverter(log_callback=self.log)

        self.root = tk.Tk()
        self.root.title("Markitdown Converter")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        self.arquivos = []
        self.destino = ""
        
        # Inicializar variáveis de controle
        self.clean_text_var = tk.BooleanVar(value=True)
        self.extract_tables_var = tk.BooleanVar(value=True)
        
        # Controle de threading e concorrência
        self._thread_lock = threading.Lock()
        self._is_processing = False
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._current_futures = []
        
        self.criar_widgets()

    def criar_widgets(self):
        frame_selecao = ttk.LabelFrame(self.root, text="Seleção de arquivos")
        frame_selecao.pack(fill="x", padx=10, pady=8)

        btn_selecionar = ttk.Button(frame_selecao, text="Selecionar arquivos", command=self.selecionar_arquivos)
        btn_selecionar.pack(side="left", padx=5, pady=5)

        btn_selecionar_pasta = ttk.Button(frame_selecao, text="Selecionar Pasta (Lote)", command=self.selecionar_pasta_origem)
        btn_selecionar_pasta.pack(side="left", padx=5, pady=5)

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
        self.text_logs = tk.Text(frame_logs, height=12, state='disabled', font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(frame_logs, orient="vertical", command=self.text_logs.yview)
        self.text_logs.configure(yscrollcommand=scrollbar.set)
        self.text_logs.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Frame para opções de conversão
        frame_opcoes = ttk.LabelFrame(self.root, text="Opções de conversão")
        frame_opcoes.pack(fill="x", padx=10, pady=(0,8))
        
        ttk.Checkbutton(frame_opcoes, text="Limpar texto (remover artefatos)", 
                       variable=self.clean_text_var).pack(side="left", padx=5, pady=5)
        ttk.Checkbutton(frame_opcoes, text="Extrair tabelas como Markdown", 
                       variable=self.extract_tables_var).pack(side="left", padx=5, pady=5)

        frame_botoes = ttk.Frame(self.root)
        frame_botoes.pack(fill="x", padx=10, pady=8)
        
        self.btn_converter = ttk.Button(frame_botoes, text="Converter Selecionado", command=self.converter_selecionado_thread)
        self.btn_converter.pack(side="left", padx=5)
        
        self.btn_batch = ttk.Button(frame_botoes, text="Conversão em Lote", command=self.converter_batch_thread)
        self.btn_batch.pack(side="left", padx=5)
        
        self.btn_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=self.cancelar_operacao, state="disabled")
        self.btn_cancelar.pack(side="left", padx=5)
        
        ttk.Button(frame_botoes, text="Sair", command=self.root.quit).pack(side="right", padx=5)
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", padx=10, pady=(0,5))
        
        self.status_label = ttk.Label(self.root, text="Pronto")
        self.status_label.pack(pady=(0,5))

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
        if arquivos:
            # Validar arquivos selecionados
            valid_files = SecurityValidator.validate_file_list(list(arquivos))
            invalid_count = len(arquivos) - len(valid_files)
            
            self.arquivos = valid_files
            
            if invalid_count > 0:
                self.log(f"⚠️ {invalid_count} arquivo(s) inválido(s) ou inseguro(s) foram ignorados")
        else:
            self.arquivos = list(arquivos)
        self.lbl_arquivos.config(text=f"{len(self.arquivos)} arquivo(s) selecionado(s)" if self.arquivos else "Nenhum arquivo selecionado...")

    def selecionar_destino(self):
        destino = filedialog.askdirectory(title="Escolher diretório de saída")
        if destino:
            # Validar diretório de destino
            if SecurityValidator.validate_directory_path(destino):
                self.destino = destino
                self.lbl_destino.config(text=destino)
            else:
                messagebox.showerror(
                    "Erro de Segurança", 
                    f"Diretório inválido ou sem permissões de escrita:\n{destino}"
                )
                self.log(f"❌ Diretório inválido ou sem permissões: {destino}")
        else:
            self.lbl_destino.config(text="Nenhuma pasta selecionada")

    def log(self, mensagem):
        # Usar after() para thread-safe UI updates
        self.root.after(0, self._safe_log, mensagem)
    
    def _safe_log(self, mensagem):
        """Thread-safe logging method"""
        self.text_logs['state'] = 'normal'
        self.text_logs.insert('end', mensagem + '\n')
        self.text_logs.see('end')
        self.text_logs['state'] = 'disabled'
        self.logger.info(mensagem)
    
    def _update_progress(self, value, status_text=""):
        """Thread-safe progress update"""
        self.root.after(0, self._safe_update_progress, value, status_text)
    
    def _safe_update_progress(self, value, status_text):
         """Update progress bar and status label safely"""
         self.progress_var.set(value)
         if status_text:
             self.status_label.config(text=status_text)
         self.root.update_idletasks()
    
    def _toggle_buttons(self, enabled):
        """Thread-safe button state toggle"""
        self.root.after(0, self._safe_toggle_buttons, enabled)
    
    def _safe_toggle_buttons(self, enabled):
        """Toggle button states safely"""
        state = "normal" if enabled else "disabled"
        cancel_state = "disabled" if enabled else "normal"
        
        self.btn_converter.config(state=state)
        self.btn_batch.config(state=state)
        self.btn_cancelar.config(state=cancel_state)
    
    def _on_operation_complete(self, future):
        """Callback when operation completes"""
        with self._thread_lock:
            self._is_processing = False
            if future in self._current_futures:
                self._current_futures.remove(future)
        
        self._toggle_buttons(True)
        self._update_progress(0, "Pronto")
    
    def cancelar_operacao(self):
        """Cancel current operation"""
        with self._thread_lock:
            if self._is_processing:
                self._is_processing = False
                # Cancel all running futures
                for future in self._current_futures:
                    future.cancel()
                self._current_futures.clear()
                
                # Cancel async operations in FileConverter
                if hasattr(self.file_converter, 'cancel_async_operations'):
                    self.file_converter.cancel_async_operations()
                
                self.log("Cancelando operação...")
                self._toggle_buttons(True)
                self._update_progress(0, "Operação cancelada")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)

    def converter_selecionado_thread(self):
        if not self.arquivos:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado.")
            return
        if not self.destino:
            messagebox.showwarning("Aviso", "Nenhum diretório de destino selecionado.")
            return
        
        with self._thread_lock:
            if self._is_processing:
                messagebox.showinfo("Info", "Uma operação já está em andamento.")
                return
            self._is_processing = True
            self._toggle_buttons(False)
        
        # Usar processamento assíncrono
        future = self._executor.submit(self.converter_selecionado_async)
        self._current_futures.append(future)
        future.add_done_callback(self._on_operation_complete)

    def converter_selecionado_async(self):
        """Conversão assíncrona de arquivos selecionados"""
        if not self.arquivos or not self.destino:
            messagebox.showwarning("Aviso", "Selecione arquivos e diretório de saída.")
            return

        try:
            options = {
                'clean_text': self.clean_text_var.get(),
                'extract_tables': self.extract_tables_var.get()
            }
            
            # Callback para progresso
            def progress_callback(completed, total, current_file):
                if not self._is_processing:  # Verificar cancelamento
                    return False
                progress = (completed / total) * 100
                self._update_progress(progress, f"Processando {completed}/{total}: {os.path.basename(current_file)}")
                return True
            
            # Usar processamento assíncrono do FileConverter
            results = self.file_converter.convert_files_async(
                self.arquivos, 
                self.destino, 
                options=options,
                progress_callback=progress_callback
            )
            
            # Processar resultados (results é um dicionário com 'success', 'errors', 'cancelled')
            if results.get('cancelled', False):
                self.log("Operação cancelada pelo usuário.")
                return
                
            successful = len(results.get('success', []))
            failed = len(results.get('errors', []))
            
            self.log(f"Conversão concluída: {successful} sucessos, {failed} falhas.")
            
            # Exibir sucessos
            for result in results.get('success', []):
                self.log(f"✓ Sucesso: {result.get('output', result.get('file', 'Arquivo desconhecido'))}")
            
            # Exibir erros se houver
            for result in results.get('errors', []):
                self.log(f"❌ Erro em {result.get('file', 'Arquivo desconhecido')}: {result.get('error', 'Erro desconhecido')}")
                    
        except Exception as e:
            self._safe_log(f"Erro inesperado durante conversão assíncrona: {type(e).__name__} - {str(e)}")
            messagebox.showerror("Erro Inesperado", f"Erro inesperado durante conversão:\n{type(e).__name__}: {str(e)}")

    def selecionar_pasta_origem(self):
        pasta_origem = filedialog.askdirectory(title="Selecione uma pasta para conversão em lote")
        if not pasta_origem:
            return

        self.arquivos = []
        supported_exts = self.file_converter.SUPPORTED_EXTENSIONS.keys()
        for root, _, files in os.walk(pasta_origem):
            for file in files:
                if any(file.lower().endswith(ext) for ext in supported_exts):
                    self.arquivos.append(os.path.join(root, file))

        self.lbl_arquivos.config(text=f"{len(self.arquivos)} arquivo(s) encontrado(s) para lote.")
        self.log(f"Pasta para lote selecionada: {pasta_origem} - {len(self.arquivos)} arquivos encontrados.")

    def converter_batch_thread(self):
        if not self.arquivos:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado.")
            return
        if not self.destino:
            messagebox.showwarning("Aviso", "Nenhum diretório de destino selecionado.")
            return
        
        with self._thread_lock:
            if self._is_processing:
                messagebox.showinfo("Info", "Uma operação já está em andamento.")
                return
            self._is_processing = True
            self._toggle_buttons(False)
        
        # Usar processamento assíncrono para lote
        future = self._executor.submit(self.converter_batch_async)
        self._current_futures.append(future)
        future.add_done_callback(self._on_operation_complete)

    def converter_batch_async(self):
        """Conversão assíncrona em lote de arquivos"""
        total_arquivos = len(self.arquivos)
        self._update_progress(0, f"Iniciando conversão de {total_arquivos} arquivos...")
        
        try:
            options = {
                'clean_text': self.clean_text_var.get(),
                'extract_tables': self.extract_tables_var.get()
            }
            
            # Callback para progresso
            def progress_callback(completed, total, current_file):
                if not self._is_processing:  # Verificar cancelamento
                    self.log("Operação cancelada pelo usuário.")
                    return False
                progress = (completed / total) * 100
                self._update_progress(progress, f"Convertendo {completed}/{total}: {os.path.basename(current_file)}")
                self.log(f"Convertendo {completed}/{total}: {current_file}")
                return True
            
            # Usar processamento assíncrono do FileConverter
            results = self.file_converter.convert_files_async(
                self.arquivos, 
                self.destino, 
                options=options,
                progress_callback=progress_callback
            )
            
            # Processar resultados (results é um dicionário com 'success', 'errors', 'cancelled')
            if results.get('cancelled', False):
                self._update_progress(0, "Operação cancelada")
                self.log("Conversão em lote cancelada pelo usuário.")
                return
                
            successful = len(results.get('success', []))
            failed = len(results.get('errors', []))
            
            self._update_progress(100, "Conversão concluída")
            self.log(f"Conversão em lote concluída: {successful} sucessos, {failed} falhas de {total_arquivos} arquivos.")
            
            # Exibir sucessos
            for result in results.get('success', []):
                self.log(f"✓ Sucesso: {result.get('output', result.get('file', 'Arquivo desconhecido'))}")
            
            # Exibir erros se houver
            for result in results.get('errors', []):
                self.log(f"❌ Falha em {result.get('file', 'Arquivo desconhecido')}: {result.get('error', 'Erro desconhecido')}")
                    
        except Exception as e:
            self._safe_log(f"Erro inesperado durante conversão em lote assíncrona: {type(e).__name__} - {str(e)}")
            messagebox.showerror("Erro Inesperado", f"Erro inesperado durante conversão em lote:\n{type(e).__name__}: {str(e)}")

    def run(self):
        self.root.mainloop()
