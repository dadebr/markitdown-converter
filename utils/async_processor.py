#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Async Processor - Markitdown Converter

Módulo para processamento assíncrono de arquivos com pool de threads configurável.
Fornece controle de concorrência e cancelamento de operações.

Author: dadebr
GitHub: https://github.com/dadebr/markitdown-converter
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from typing import List, Dict, Any, Callable, Optional, Tuple
from pathlib import Path
import time

from utils.logger import get_logger
from .observer import Subject, EventBus

class AsyncProcessor(Subject):
    """
    Processador assíncrono para conversão de arquivos com pool de threads e padrão Observer.
    """
    
    def __init__(self, max_workers: int = 4, log_callback: Optional[Callable] = None):
        """
        Inicializa o processador assíncrono.
        
        Args:
            max_workers: Número máximo de threads no pool
            log_callback: Função de callback para logs
        """
        super().__init__()
        self.max_workers = max_workers
        self.log_callback = log_callback
        self.logger = get_logger(__name__) if log_callback is None else None
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._active_futures: Dict[str, Future] = {}
        self._lock = threading.Lock()
        self._cancelled = False
        self.event_bus = EventBus()
        
    def _log(self, message: str, level: str = 'info'):
        """Registra uma mensagem de log."""
        if self.log_callback:
            self.log_callback(message)
        elif self.logger:
            getattr(self.logger, level)(message)
    
    def process_files_async(self, 
                           files: List[str], 
                           converter_func: Callable,
                           output_dir: str,
                           options: Dict[str, Any] = None,
                           progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Processa múltiplos arquivos de forma assíncrona.
        
        Args:
            files: Lista de caminhos de arquivos para processar
            converter_func: Função de conversão a ser aplicada
            output_dir: Diretório de saída
            options: Opções de conversão
            progress_callback: Callback para atualização de progresso
            
        Returns:
            Dict com resultados do processamento
        """
        if not files:
            return {'success': [], 'errors': [], 'cancelled': False}
            
        options = options or {}
        results = {'success': [], 'errors': [], 'cancelled': False}
        
        self._cancelled = False
        total_files = len(files)
        
        self._log(f"Iniciando processamento assíncrono de {total_files} arquivos")
        
        # Notificar início do processamento
        self.notify('process_start', {
            'total_files': total_files,
            'output_dir': output_dir
        })
        
        # Submeter todas as tarefas
        futures_to_files = {}
        
        with self._lock:
            for i, file_path in enumerate(files):
                if self._cancelled:
                    break
                    
                output_path = self._generate_output_path(file_path, output_dir)
                task_id = f"task_{i}_{Path(file_path).name}"
                
                future = self.executor.submit(
                    self._process_single_file,
                    file_path, output_path, converter_func, options
                )
                
                futures_to_files[future] = {
                    'file_path': file_path,
                    'output_path': output_path,
                    'task_id': task_id
                }
                
                self._active_futures[task_id] = future
        
        # Processar resultados conforme completam
        completed_count = 0
        
        try:
            for future in as_completed(futures_to_files.keys()):
                if self._cancelled:
                    results['cancelled'] = True
                    break
                    
                file_info = futures_to_files[future]
                completed_count += 1
                
                # Notificar progresso via Observer
                self.notify('progress', {
                    'completed': completed_count,
                    'total': total_files,
                    'current_file': file_info['file_path']
                })
                
                try:
                    result = future.result(timeout=30)  # Timeout de 30 segundos por arquivo
                    
                    if result['success']:
                        results['success'].append({
                            'file': file_info['file_path'],
                            'output': file_info['output_path'],
                            'message': result.get('message', 'Convertido com sucesso')
                        })
                        
                        # Notificar conclusão do arquivo
                        self.notify('file_complete', {
                            'file': file_info['file_path'],
                            'success': True,
                            'output_file': file_info['output_path'],
                            'message': result.get('message', 'Convertido com sucesso')
                        })
                        
                        self._log(f"✓ Convertido: {Path(file_info['file_path']).name}")
                    else:
                        results['errors'].append({
                            'file': file_info['file_path'],
                            'error': result.get('error', 'Erro desconhecido')
                        })
                        
                        # Notificar erro
                        self.notify('error', {
                            'file': file_info['file_path'],
                            'error': result.get('error', 'Erro desconhecido')
                        })
                        
                        self._log(f"✗ Erro: {Path(file_info['file_path']).name} - {result.get('error', 'Erro desconhecido')}", 'error')
                        
                except Exception as e:
                    results['errors'].append({
                        'file': file_info['file_path'],
                        'error': f"Timeout ou erro na execução: {str(e)}"
                    })
                    
                    # Notificar erro de timeout
                    self.notify('error', {
                        'file': file_info['file_path'],
                        'error': f"Timeout ou erro na execução: {str(e)}"
                    })
                    
                    self._log(f"✗ Timeout: {Path(file_info['file_path']).name} - {str(e)}", 'error')
                
                # Atualizar progresso
                if progress_callback:
                    # Chamar callback com 3 parâmetros: completed, total, current_file
                    current_file = file_info['file_path']
                    should_continue = progress_callback(completed_count, total_files, current_file)
                    
                    # Se o callback retornar False, cancelar operação
                    if should_continue is False:
                        self._log("Operação cancelada via progress_callback", 'warning')
                        self.cancel_all_operations()
                        results['cancelled'] = True
                        break
                
                # Remover da lista de ativos
                with self._lock:
                    task_id = file_info['task_id']
                    if task_id in self._active_futures:
                        del self._active_futures[task_id]
                        
        except KeyboardInterrupt:
            self._log("Processamento interrompido pelo usuário", 'warning')
            results['cancelled'] = True
            self.cancel_all_operations()
            
            # Notificar cancelamento
            self.notify('process_cancelled', {
                'completed': completed_count,
                'total': total_files
            })
        
        # Notificar conclusão se não foi cancelado
        if not results['cancelled']:
            self.notify('process_complete', {
                'total_processed': len(results['success']) + len(results['errors']),
                'successful': len(results['success']),
                'failed': len(results['errors'])
            })
            
        return results
    
    def _process_single_file(self, 
                           input_path: str, 
                           output_path: str, 
                           converter_func: Callable,
                           options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa um único arquivo.
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho do arquivo de saída
            converter_func: Função de conversão
            options: Opções de conversão
            
        Returns:
            Dict com resultado do processamento
        """
        try:
            if self._cancelled:
                return {'success': False, 'error': 'Operação cancelada'}
                
            start_time = time.time()
            
            # Executar conversão
            result = converter_func(input_path, output_path, options)
            
            processing_time = time.time() - start_time
            
            if result:
                return {
                    'success': True, 
                    'message': f'Convertido em {processing_time:.2f}s',
                    'processing_time': processing_time
                }
            else:
                return {'success': False, 'error': 'Falha na conversão'}
                
        except Exception as e:
            return {'success': False, 'error': f'{type(e).__name__}: {str(e)}'}
    
    def _generate_output_path(self, input_path: str, output_dir: str) -> str:
        """
        Gera o caminho de saída para um arquivo.
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_dir: Diretório de saída
            
        Returns:
            Caminho completo do arquivo de saída
        """
        input_file = Path(input_path)
        output_filename = f"{input_file.stem}.md"
        return str(Path(output_dir) / output_filename)
    
    def cancel_all_operations(self):
        """
        Cancela todas as operações em andamento.
        """
        self._log("Cancelando todas as operações em andamento...")
        
        with self._lock:
            self._cancelled = True
            
            # Cancelar todos os futures ativos
            cancelled_count = 0
            for task_id, future in self._active_futures.items():
                if not future.done():
                    if future.cancel():
                        cancelled_count += 1
                    self._log(f"Cancelado: {task_id}")
            
            self._active_futures.clear()
        
        # Notificar cancelamento via Observer
        self.notify('operations_cancelled', {
            'cancelled_count': cancelled_count,
            'timestamp': self._get_timestamp()
        })
        
        self._log(f"Operações canceladas: {cancelled_count}", 'warning')
    
    def get_active_tasks_count(self) -> int:
        """
        Retorna o número de tarefas ativas.
        
        Returns:
            Número de tarefas em execução
        """
        with self._lock:
            return len([f for f in self._active_futures.values() if not f.done()])
    
    def is_processing(self) -> bool:
        """
        Verifica se há processamento em andamento.
        
        Returns:
            True se há tarefas ativas, False caso contrário
        """
        return self.get_active_tasks_count() > 0
    
    def shutdown(self, wait: bool = True):
        """
        Encerra o processador e limpa recursos.
        
        Args:
            wait: Se deve aguardar a conclusão das tarefas
        """
        self._log("Encerrando processador assíncrono...")
        
        if not wait:
            self.cancel_all_operations()
        
        self.executor.shutdown(wait=wait)
        
        # Notificar encerramento
        self.notify('processor_shutdown', {
            'timestamp': self._get_timestamp()
        })
        
        self._log("Processador assíncrono encerrado")
    
    def _get_timestamp(self):
        """Retorna timestamp atual para eventos."""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def __del__(self):
        """Destrutor para garantir limpeza de recursos."""
        try:
            self.shutdown(wait=False)
        except:
            pass  # Ignorar erros durante destruição