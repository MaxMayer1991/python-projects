import tkinter as tk
from tkinter import *
import datetime as dt
from PIL import Image, ImageTk
import requests
from io import BytesIO
import math
link = "http://api.openweathermap.org/data/2.5/weather?"
klucz_api = "fd825c3b4172c59e3c7de42108e88159"


def draw_wind_direction_arrow(line_id, canvas, angle_degrees, length=100):
    angle_radians = math.radians(angle_degrees)

    end_x = length * math.cos(angle_radians)
    end_y = length * math.sin(angle_radians)

    canvas.coords(line_id, length, length, end_x, end_y)





def temp_conv(temp_k):
    temp_c = round(temp_k - 273.15, 1)
    temp_f = round(temp_c * (9/5) + 32, 1)
    return temp_c, temp_f

def wyszukaj():
    miasto = naz_miasta.get()
    miasto_lab['text'] = f"{miasto}"
    urlApi = link + "appid=" + klucz_api + "&q=" + miasto

    response = requests.get(urlApi).json()
    print(response)
    urlImg = "https://openweathermap.org/img/wn/" + f"{response['weather'][0]['icon']}" + "@2x.png"
    photo_img = show_image(urlImg)
    img_label['image'] = photo_img
    img_label.image = photo_img

    draw_wind_direction_arrow(line_id,canvas, response['wind']['deg'])

    temp_k = response['main']['temp']
    od_temp_k = response['main']['feels_like']
    cisnienie = response['main']['pressure']
    humidity = response['main']['humidity']
    opis = response['weather'][0]['description']
    pr_wiatru = response['wind']['speed']

    temp_c, temp_f = temp_conv(temp_k)
    od_temp_c, od_temp_f = temp_conv(od_temp_k)

    od_temp_l['text'] = f"{od_temp_c:.2f}C lub {od_temp_f}F odczuwalne stopni w mieście {miasto}"
    temp_l['text'] = f"{temp_c:.2f}C lub {temp_f}F stopni w mieście {miasto}"
    pr_wiatru_l['text'] = f"Prędkość wiatru: {pr_wiatru} m/s"
    wilg_l['text'] = f"Wilgotność: {humidity}%"
    opis_l['text'] = f"Opis pogody: {opis}"
    cisnienie_l['text'] = f"Ciścinienie {cisnienie}Pa"


def load_image_from_url(url):
    response = requests.get(url)
    img_data = BytesIO(response.content)
    img = Image.open(img_data)
    return ImageTk.PhotoImage(img)
def show_image(url):
    image = load_image_from_url(url)
    return image


widget = Tk()
widget.title("Widget pogodowy")
widget.geometry("700x700+400+200")
ico = PhotoImage(file="Weather.png")
widget.config(bg="#001111")
widget.iconphoto(True,ico)

tekst_m = StringVar()
naz_miasta = Entry(widget, textvariable=tekst_m)
naz_miasta.pack()

wyszukaj_miasto = Button(widget, text="Wyszukaj miasto", width=12, command=wyszukaj)
wyszukaj_miasto.pack()


miasto_lab = Label(widget, text='', font=('bold', 20))

miasto_lab.pack()
temp_l = Label(widget, text='')
temp_l.pack()
od_temp_l = Label(widget, text='')
od_temp_l.pack()
pr_wiatru_l = Label(widget, text='')
pr_wiatru_l.pack()
wilg_l = Label(widget,text='')
wilg_l.pack()
opis_l = Label(widget,text='')
opis_l.pack()
cisnienie_l = Label(widget,text='')
cisnienie_l.pack()

img_label = Label(widget, image='')
img_label.pack()


canvas = tk.Canvas(widget, width=200, height=200)
line_id = canvas.create_line(0, 0, 0, 0, width=2, fill='red', arrow=tk.FIRST)

canvas.pack()



widget.mainloop()