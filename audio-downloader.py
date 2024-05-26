import os
import json
from pytube import YouTube
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from threading import Thread
from PIL import Image, ImageTk
import ctypes

# Função para salvar a pasta destino no arquivo config.json
def save_config(destination_folder):
    with open('config.json', 'w') as config_file:
        json.dump({'destination_folder': destination_folder}, config_file)

# Função para carregar a pasta destino do arquivo config.json
def load_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            return config.get('destination_folder', '')
    return ''

# Função para atualizar a barra de progresso
def update_progress(percent, progress_var, progress_bar):
    progress_var.set(percent)
    progress_bar.update()

# Função de download do áudio
def download_audio(url, destination_folder, progress_var, progress_bar, status_label):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        out_file = audio_stream.download(output_path=destination_folder)
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        messagebox.showinfo("Download completo", "O áudio foi baixado com sucesso.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

# Função para iniciar o download em uma thread separada
def start_download():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Aviso", "Por favor, insira o link do vídeo.")
        return

    destination_folder = destination_folder_var.get()
    if not destination_folder:
        messagebox.showwarning("Aviso", "Por favor, escolha a pasta de destino.")
        return

    save_config(destination_folder)

    download_thread = Thread(target=download_audio, args=(url, destination_folder, progress_var, progress_bar, status_label))
    download_thread.start()

# Função para selecionar a pasta de destino
def select_destination_folder():
    folder = filedialog.askdirectory()
    if folder:
        destination_folder_var.set(folder)

# GUI
root = tk.Tk()
root.title("Léozitu Audio Downloader")
root.geometry("500x300")

# Caminho absoluto do ícone
icon_path = os.path.abspath('my_icon.ico')

# Carregar o ícone com o Pillow
icon = Image.open(icon_path)
icon = icon.resize((32, 32), Image.BICUBIC)  # Redimensionar o ícone para o tamanho desejado
icon = ImageTk.PhotoImage(icon)

# Adicionando o ícone personalizado
root.iconphoto(True, icon)

# Configurando o ícone para a barra de tarefas (usando ctypes)
myappid = 'mycompany.myproduct.subproduct.version'  # Arbitrário, mas deve ser único para cada aplicativo
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# Alterando a cor de fundo da janela para rosa
root.configure(bg='pink')

# Centralizar os widgets no root
frame = tk.Frame(root, bg='pink')
frame.pack(expand=True)

# URL Entry
tk.Label(frame, text="Link do Vídeo:", bg='pink').pack(pady=5)
url_entry = tk.Entry(frame, width=60)
url_entry.pack(pady=5)

# Pasta Destino
tk.Label(frame, text="Pasta de Destino:", bg='pink').pack(pady=5)
destination_folder_var = tk.StringVar()
destination_folder_var.set(load_config())

destination_frame = tk.Frame(frame, bg='pink')
destination_frame.pack(pady=5)
tk.Entry(destination_frame, textvariable=destination_folder_var, width=50).pack(side=tk.LEFT, padx=5)
tk.Button(destination_frame, text="Selecionar", command=select_destination_folder).pack(side=tk.LEFT, padx=5)

# Progress Bar
tk.Label(frame, text="Progresso:", bg='pink').pack(pady=5)
progress_var = tk.IntVar()
progress_bar = Progressbar(frame, orient=tk.HORIZONTAL, length=400, mode='determinate', maximum=100, variable=progress_var)
progress_bar.pack(pady=5)

# Status Label
status_label = tk.Label(frame, text="Aguardando...", bg='pink')
status_label.pack(pady=5)

# Download Button
tk.Button(frame, text="Baixar Áudio", command=start_download).pack(pady=20)

root.mainloop()
