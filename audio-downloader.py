import os
import json
import sys
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Style, Entry, Label, Button, Frame
from threading import Thread
from PIL import Image, ImageTk
import ctypes
import time


# 🔹 Obtém o caminho do ffmpeg.exe
def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):  # Se rodando como .exe
        base_path = sys._MEIPASS
    else:  # Se rodando como script normal
        base_path = os.path.abspath(os.getcwd())

    return os.path.join(base_path, 'bin', 'ffmpeg.exe')


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


# Função para atualizar a barra de progresso dinamicamente
def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip('%')
        try:
            percent = float(percent)
            progress_var.set(percent)
            status_label.config(text=f"Baixando... {percent:.1f}%")
        except ValueError:
            pass
    elif d['status'] == 'finished':
        progress_var.set(100)
        status_label.config(text="Download completo!")


# Função para alterar a data de modificação do arquivo para a data atual
def set_current_timestamp(file_path):
    try:
        current_time = time.time()
        os.utime(file_path, (current_time, current_time))
    except Exception as e:
        print(f"Erro ao modificar data do arquivo: {e}")


# Função de download do áudio
def download_audio(url, destination_folder):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{destination_folder}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': get_ffmpeg_path(),  # 🔹 Usa o caminho correto do ffmpeg
            'progress_hooks': [progress_hook],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0'
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'audio')
            file_path = os.path.join(destination_folder, f"{title}.mp3")

            set_current_timestamp(file_path)

        messagebox.showinfo("Download completo", "O áudio foi baixado com sucesso.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")


# inicia o download em uma thread separada
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
    download_thread = Thread(target=download_audio, args=(url, destination_folder))
    download_thread.start()


# seleciona a pasta de destino
def select_destination_folder():
    folder = filedialog.askdirectory()
    if folder:
        destination_folder_var.set(folder)


# GUI
root = tk.Tk()
root.title("Léozitu Audio Downloader")
root.geometry("600x400")
root.configure(bg='black')

# Ícone
icon_path = os.path.abspath('my_icon.ico')
if os.path.exists(icon_path):
    icon = Image.open(icon_path)
    icon = icon.resize((32, 32), Image.BICUBIC)
    icon = ImageTk.PhotoImage(icon)
    root.iconphoto(True, icon)

# Barra de tarefas
myappid = 'mycompany.myproduct.subproduct.version'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

#  widgets
style = Style()
style.configure('TFrame', background='black')
style.configure('TLabel', background='black', foreground='cyan', font=("Arial", 12))
style.configure('TButton', background='#00FFFF', foreground='black', font=("Arial", 12, 'bold'), padding=5)
style.map('TButton', background=[('active', '#008B8B')])
style.configure('TEntry', font=("Arial", 12), padding=5)

# Centralizando os widgets
frame = Frame(root, style='TFrame')
frame.pack(expand=True, padx=20, pady=20)

# URL Entry
Label(frame, text="Link do Vídeo:", style='TLabel').pack(pady=5)
url_entry = Entry(frame, width=60)
url_entry.pack(pady=5)

# Pasta Destino
Label(frame, text="Pasta de Destino:", style='TLabel').pack(pady=5)
destination_folder_var = tk.StringVar()
destination_folder_var.set(load_config())

destination_frame = Frame(frame, style='TFrame')
destination_frame.pack(pady=5)

Entry(destination_frame, textvariable=destination_folder_var, width=40).pack(side=tk.LEFT, padx=5)
Button(destination_frame, text="Selecionar", command=select_destination_folder, style='TButton').pack(side=tk.LEFT, padx=5)

# Progress Bar
Label(frame, text="Progresso:", style='TLabel').pack(pady=5)
progress_var = tk.IntVar()
progress_bar = Progressbar(frame, orient=tk.HORIZONTAL, length=400, mode='determinate', maximum=100,
                           variable=progress_var)
progress_bar.pack(pady=5)

# Status Label
status_label = Label(frame, text="Aguardando...", style='TLabel')
status_label.pack(pady=5)

# Download Button
Button(frame, text="Baixar Áudio", command=start_download, style='TButton').pack(pady=20)

root.mainloop()
