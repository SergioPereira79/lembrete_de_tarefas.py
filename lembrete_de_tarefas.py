import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import webbrowser
import threading
import time
from pynput import mouse
import os
import sys
import pygetwindow as gw
from urllib.parse import urlparse

# --- LÓGICA PARA ENCONTRAR ARQUIVOS (.ini e .ico) ---
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(application_path, 'settings.ini')

# --- Dicionário de Navegadores ---
BROWSERS = {
    "Padrão do Sistema": "default",
    "Google Chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "Mozilla Firefox": "C:/Program Files/Mozilla Firefox/firefox.exe",
    "Microsoft Edge": "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
}
AVAILABLE_BROWSERS = {name: path for name, path in BROWSERS.items() if path == "default" or os.path.exists(path)}

# --- Variáveis Globais de Estado ---
listener, check_after_id = None, None
is_monitoring, is_user_inactive = False, False
last_activity_time = time.time()
INACTIVITY_SECONDS = 30 * 60

# --- Lógica Principal ---
def perform_reminder_action():
    print("Ação do lembrete disparada!")
    config = configparser.ConfigParser()
    config.read(SETTINGS_FILE)
    url = config.get('Settings', 'target_url', fallback='https://keep.google.com/')
    keyword = config.get('Settings', 'window_keyword', fallback='').strip()
    if keyword:
        try:
            target_window = next((w for w in gw.getAllWindows() if keyword.lower() in w.title.lower()), None)
            if target_window:
                print(f"Janela '{target_window.title}' encontrada. Trazendo para frente.")
                if target_window.isMinimized: target_window.restore()
                target_window.activate()
                reset_state()
                return
        except Exception as e:
            print(f"Ocorreu um erro ao verificar as janelas abertas: {e}.")
    print(f"Nenhuma janela encontrada com a palavra-chave '{keyword}'. Abrindo nova aba/janela.")
    browser_name = config.get('Settings', 'browser_name', fallback='Padrão do Sistema')
    browser_path = AVAILABLE_BROWSERS.get(browser_name)
    try:
        if not browser_path or browser_path == 'default': webbrowser.open(url, new=1)
        else: webbrowser.get(f'"{browser_path}" %s').open(url, new=1)
    except webbrowser.Error as e:
        print(f"Erro ao tentar abrir o navegador '{browser_name}': {e}.")
        webbrowser.open(url, new=1)
    reset_state()

def reset_state():
    global is_user_inactive, last_activity_time
    is_user_inactive = False
    last_activity_time = time.time()
    print("Estado resetado. Monitorando novamente.")

def on_move(x, y):
    global last_activity_time, is_user_inactive
    if not is_user_inactive:
        last_activity_time = time.time()
        return
    perform_reminder_action()
    
def check_inactivity_loop():
    global is_user_inactive, check_after_id
    if not is_monitoring: return
    if is_user_inactive:
        check_after_id = root.after(5000, check_inactivity_loop)
        return
    elapsed = time.time() - last_activity_time
    if elapsed > INACTIVITY_SECONDS:
        print(f"Usuário inativo por mais de {INACTIVITY_SECONDS / 60:.0f} minutos. Aguardando retorno...")
        is_user_inactive = True
    check_after_id = root.after(5000, check_inactivity_loop)

# --- Funções da Interface ---
def start_monitoring():
    global is_monitoring, listener, last_activity_time, INACTIVITY_SECONDS
    if is_monitoring: return
    save_settings(show_message=False)
    try:
        minutes = int(time_entry.get())
        INACTIVITY_SECONDS = minutes * 60
    except ValueError:
        messagebox.showerror("Erro", "O tempo de inatividade deve ser um número.")
        return
    is_monitoring = True
    reset_state()
    if not listener or not listener.is_alive():
        listener = mouse.Listener(on_move=on_move)
        listener.start()
    check_inactivity_loop()
    status_label.config(text="Status: Monitoramento Ativo", foreground="green")
    print("Monitoramento iniciado com sucesso.")

def stop_monitoring():
    global is_monitoring, listener, check_after_id
    if not is_monitoring: return
    is_monitoring = False
    if check_after_id:
        root.after_cancel(check_after_id)
        check_after_id = None
    if listener and listener.is_alive():
        listener.stop()
        listener.join()
        listener = None
    status_label.config(text="Status: Desligado", foreground="red")
    print("Monitoramento parado.")

def save_settings(show_message=True):
    config = configparser.ConfigParser()
    config['Settings'] = {
        'inactivity_minutes': time_entry.get(),
        'target_url': url_entry.get(),
        'browser_name': browser_combobox.get(),
        'window_keyword': keyword_entry.get()
    }
    with open(SETTINGS_FILE, 'w') as configfile:
        config.write(configfile)
    if show_message: messagebox.showinfo("Sucesso", "Configurações salvas!")

def on_closing():
    stop_monitoring()
    root.destroy()

# --- Criação da Interface Gráfica ---
root = tk.Tk()
root.title("Lembrete de Tarefas")
root.geometry("450x350") 
root.resizable(False, False)

# Estilos
style = ttk.Style(root)
style.configure("Active.TLabel", foreground="green", font=('Segoe UI', 11, 'bold'))
style.configure("Inactive.TLabel", foreground="red", font=('Segoe UI', 11, 'bold'))
style.configure("Info.TLabel", foreground="navy", font=('Segoe UI', 9, 'bold'))

# Carregar Configurações
config = configparser.ConfigParser()
config.read(SETTINGS_FILE)
initial_minutes = config.get('Settings', 'inactivity_minutes', fallback='30')
initial_url = config.get('Settings', 'target_url', fallback='https://keep.google.com/')
initial_browser = config.get('Settings', 'browser_name', fallback='Padrão do Sistema')
initial_keyword = config.get('Settings', 'window_keyword', fallback='')

# Widgets
main_frame = ttk.Frame(root, padding="15")
main_frame.pack(expand=True, fill=tk.BOTH)

# --- ADIÇÃO DA DICA NO CABEÇALHO ---
info_text = "Dica: Para detectar a janela, deixe sua tarefa (Keep, Notion, etc.) em uma janela separada."
info_label = ttk.Label(main_frame, text=info_text, style="Info.TLabel", wraplength=400, justify='center')
info_label.pack(pady=(0, 10))


ttk.Label(main_frame, text="Tempo de Inatividade (minutos):").pack(anchor='w')
time_entry = ttk.Entry(main_frame)
time_entry.insert(0, initial_minutes)
time_entry.pack(fill='x', pady=(0, 10))

ttk.Label(main_frame, text="Link para abrir (URL):").pack(anchor='w')
url_entry = ttk.Entry(main_frame)
url_entry.insert(0, initial_url)
url_entry.pack(fill='x', pady=(0, 10))

ttk.Label(main_frame, text="Palavra-Chave para Janela (ex: Keep, Notion):").pack(anchor='w')
keyword_entry = ttk.Entry(main_frame)
keyword_entry.insert(0, initial_keyword)
keyword_entry.pack(fill='x', pady=(0, 10))

ttk.Label(main_frame, text="Abrir com o navegador:").pack(anchor='w')
browser_combobox = ttk.Combobox(main_frame, values=list(AVAILABLE_BROWSERS.keys()), state="readonly")
if initial_browser not in AVAILABLE_BROWSERS: initial_browser = "Padrão do Sistema"
browser_combobox.set(initial_browser)
browser_combobox.pack(fill='x', pady=(0, 10))

status_label = tk.Label(main_frame, text="Status: Desligado", fg="red", font=('Segoe UI', 11, 'bold'))
status_label.pack(pady=5)

buttons_frame = ttk.Frame(main_frame)
buttons_frame.pack(fill='x', side='bottom')

start_button = ttk.Button(buttons_frame, text="Ligar", command=start_monitoring)
start_button.pack(side='left', expand=True, fill='x', padx=(0, 5))
stop_button = ttk.Button(buttons_frame, text="Desligar", command=stop_monitoring)
stop_button.pack(side='left', expand=True, fill='x', padx=5)
save_button = ttk.Button(buttons_frame, text="Salvar", command=save_settings)
save_button.pack(side='right', expand=True, fill='x', padx=(5, 0))

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()