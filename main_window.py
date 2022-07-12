from dataclasses import dataclass
import subprocess
import threading

import tkinter as tk
import tkinter.ttk as ttk

from typing import BinaryIO, List
from PIL import Image, ImageTk
import win32gui
import numpy as np

preview_width, preview_height = 460, 270
preview_image: Image = None
preview_image_tk: ImageTk.PhotoImage = None
preview_image_view: tk.Label = None

@dataclass
class WindowInfo:
  title: str
  width: int
  height: int

window_info_list: List[WindowInfo] = []
select_window_combobox: ttk.Combobox = None
window_capture_process: subprocess.Popen = None

def update_window_info_list():
  global window_info_list

  new_list: List[WindowInfo] = []

  def map_window(hwnd, title):
    if not win32gui.IsWindowVisible(hwnd):
      return

    title = win32gui.GetWindowText(hwnd)
    if len(title) == 0:
      return

    # left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width = right - left
    height = bottom - top

    new_list.append(WindowInfo(
      title=str(title),
      width=int(width),
      height=int(height),
    ))

  win32gui.EnumWindows(map_window, None)

  window_info_list = new_list

def select_window(event: tk.Event):
  pass

def start_capture(event: tk.Event):
  global select_window_combobox, window_capture_process
  global preview_image, preview_image_tk, preview_image_view

  info = window_info_list[select_window_combobox.current()]

  title = info.title
  width = info.width
  height = info.height

  framerate = 30
  framesize = height * width * 3
  bufsize = framesize * framerate * 10

  print(f'Title: {title}, Width: {width}, Height: {height}')

  # FIXME: non-ASCII char title window cannot be grabbed
  command = [
    'ffmpeg',
    '-f',
    'gdigrab',
    '-framerate',
    str(framerate),
    '-i',
    f'title={title}',
    '-f',
    'image2pipe',
    '-vcodec',
    'rawvideo',
    '-pix_fmt',
    'rgb24',
    '-'
  ]
  window_capture_process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=bufsize)

  def read_stdout(buffer: BinaryIO):
    while True:
      image_bytes = buffer.read(framesize)
      if len(image_bytes) != framesize:
        continue

      image_np = np.frombuffer(image_bytes, dtype=np.uint8)
      image_np = image_np.reshape((height, width, 3))

      preview_image = Image.fromarray(image_np)
      preview_image = preview_image.resize((preview_width, preview_height))

      preview_image_tk = ImageTk.PhotoImage(preview_image)

      preview_image_view['image'] = preview_image_tk

  thread = threading.Thread(target=read_stdout, args=(window_capture_process.stdout, ), daemon=True)
  thread.start()


def stop_capture(event: tk.Event = None):
  if not window_capture_process:
    return

  window_capture_process.kill()
  print('killed capture')

def init_components(root: tk.Tk):
  global select_window_combobox
  global preview_image, preview_image_tk, preview_image_view

  x = 8
  y = 8

  window_label = tk.Label(root, text='Window')
  window_label.place(x=x, y=y)

  root.update()
  x += window_label.winfo_width() + 8

  update_window_info_list()
  select_window_values = list(map(lambda info: f'{info.title} ({info.width}x{info.height})', window_info_list))

  select_window_combobox = ttk.Combobox(root, state='readonly', values=select_window_values)
  select_window_combobox.current(0) # TODO: no window available

  select_window_combobox.place(x=x, y=y, width=390)

  root.update()
  x = 8
  y += select_window_combobox.winfo_height() + 8

  start_capture_button = tk.Button(root, text='Start Capture')
  start_capture_button.bind('<Button-1>', start_capture)
  start_capture_button.place(x=x, y=y)

  root.update()
  x += start_capture_button.winfo_width() + 8

  stop_cature_button = tk.Button(root, text='Stop Capture')
  stop_cature_button.bind('<Button-1>', stop_capture)
  stop_cature_button.place(x=x, y=y)

  root.update()

  x = (window_width - preview_width) // 2
  y += stop_cature_button.winfo_height() + 8

  preview_image = Image.new('RGB', (preview_width, preview_height), color=(255, 0, 255))
  preview_image_tk = ImageTk.PhotoImage(preview_image)

  preview_image_view = tk.Label(root, image=preview_image_tk)
  preview_image_view.place(x=x, y=y)

  root.update()
  print(preview_image_view.winfo_y() + preview_image_view.winfo_height())


if __name__ == '__main__':
  root = tk.Tk()
  root.title('Lavender Window')

  window_width, window_height = 480, (345+16)
  root.geometry(f'{window_width}x{window_height}')

  init_components(root)

  root.mainloop()

  stop_capture()
