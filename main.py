import tkinter as tk
import tkinter.ttk as ttk

from typing import List
from PIL import Image, ImageTk
import win32gui

preview_width, preview_height = 460, 270
preview_image: Image = None
preview_image_tk: ImageTk.PhotoImage = None

select_screen_combobox: ttk.Combobox = None

def get_visible_window_titles():
  titles: List[str] = []

  def map_window(hwnd, title):
    if not win32gui.IsWindowVisible(hwnd):
      return

    title = win32gui.GetWindowText(hwnd)
    if len(title) == 0:
      return

    titles.append(title)

  win32gui.EnumWindows(map_window, None)
  return titles

def select_screen(event: tk.Event):
  pass

def select_window(event: tk.Event):
  pass

def start_capture(event: tk.Event):
  pass

def stop_capture(event: tk.Event):
  pass


def init_components(root: tk.Tk):
  global select_screen_combobox, select_window_combobox
  global preview_image, preview_image_tk

  x = 8
  y = 8 + 4

  screen_label = tk.Label(root, text='Screen')
  screen_label.place(x=x, y=y)

  root.update()
  x += screen_label.winfo_width() + 8

  select_screen_combobox = ttk.Combobox(root, state='readonly')
  select_screen_combobox.place(x=x, y=y, width=350)

  root.update()
  x += select_screen_combobox.winfo_width() + 8
  y -= 4

  select_screen_button = tk.Button(root, text='Select')
  select_screen_button.bind('<Button-1>', select_screen)
  select_screen_button.place(x=x, y=y)

  root.update()
  x = 8
  y += select_screen_button.winfo_height() + 8

  select_window_button = tk.Button(root, text='Select Window')
  select_window_button.bind('<Button-1>', select_window)
  select_window_button.place(x=x, y=y)

  root.update()
  x = 8
  y += select_window_button.winfo_height() + 8

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
  root.title('Lavender')

  window_width, window_height = 480, 392
  root.geometry(f'{window_width}x{window_height}')

  init_components(root)

  root.mainloop()
