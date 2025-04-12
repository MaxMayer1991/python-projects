from tkinter import *
from tkinter import messagebox
import tkinter as tk

win = tk.Tk()
def press_key(event):
    print(event.char)
    if event.char.isdigit():
        add_digit(event.char)
    elif event.char in '+-/*':
        add_operation(event.char)
    elif event.char in '\r':
        calculate()
def add_digit(digit):
    value = calc.get()
    if value[0] == '0' and len(value) == 1:
        value = value[1:]
    calc['state'] = tk.NORMAL
    calc.delete(0, tk.END)
    calc.insert(0, value+digit)
    calc['state'] = tk.DISABLED
def add_operation(oper):
    value = calc.get()
    if value[-1] in '+-/*':
        value = value[:-1]
    elif '+' in value or '-' in value or '*' in value or '/' in value:
        calculate()
        value = calc.get()
    calc['state'] = tk.NORMAL
    calc.delete(0, tk.END)
    calc.insert(0, value+oper)
    calc['state'] = tk.DISABLED
def calculate():
    value = calc.get()
    if value[-1] in '+-/*':
        value = value + value[:-1]
    calc['state'] = tk.NORMAL
    calc.delete(0, tk.END)
    try:
        calc.insert(0, eval(value))
    except (NameError, SyntaxError):
        messagebox.showinfo('Warning', 'Digit is only allowed!')
        calc.insert(0, 0)
    except ZeroDivisionError:
        messagebox.showinfo('Warning', 'Division by zero!')
        calc.insert(0,0)
    calc['state'] = tk.DISABLED

def clear():
    calc.delete(0, tk.END)
    calc.insert(0, '0')
def create_button_operation(oper):
    return tk.Button(text=f"{oper}", bd=5, font=('Arial', 20, 'bold'), fg='red', command=lambda: add_operation(oper))
def create_button_digit(digit):
    return tk.Button(text=f"{digit}", bd=5, font=('Arial', 20, 'bold'), command=lambda: add_digit(digit))
def create_button_calc(digit):
    return tk.Button(text=f"{digit}", bd=5, font=('Arial', 20, 'bold'), fg='red', command=calculate)
def create_button_clear(digit):
    return tk.Button(text=f"{digit}", bd=5, font=('Arial', 20, 'bold'), fg='red', command=clear)
calc = tk.Entry(win, justify=tk.RIGHT, font=('Arial', 20, 'bold'), width=20)
calc.grid(row=0, column=0, columnspan=4, stick="wes")
calc.insert(0, '0')
calc['state'] = tk.DISABLED
create_button_digit('1').grid(row=1, column=0, stick="wens", padx=10, pady=10)
create_button_digit('2').grid(row=1, column=1, stick="wens", padx=10, pady=10)
create_button_digit('3').grid(row=1, column=2, stick="wens", padx=10, pady=10)
create_button_digit('4').grid(row=2, column=0, stick="wens", padx=10, pady=10)
create_button_digit('5').grid(row=2, column=1, stick="wens", padx=10, pady=10)
create_button_digit('6').grid(row=2, column=2, stick="wens", padx=10, pady=10)
create_button_digit('7').grid(row=3, column=0, stick="wens", padx=10, pady=10)
create_button_digit('8').grid(row=3, column=1, stick="wens", padx=10, pady=10)
create_button_digit('9').grid(row=3, column=2, stick="wens", padx=10, pady=10)
create_button_digit('0').grid(row=4, column=0, stick="wens", padx=10, pady=10)
create_button_operation('+').grid(row=1, column=3, stick="wens", padx=10, pady=10)
create_button_operation('-').grid(row=2, column=3, stick="wens", padx=10, pady=10)
create_button_operation('*').grid(row=3, column=3, stick="wens", padx=10, pady=10)
create_button_operation('/').grid(row=4, column=3, stick="wens", padx=10, pady=10)
create_button_calc('=').grid(row=4, column=2, stick="wens", padx=10, pady=10)
create_button_clear('C').grid(row=4, column=1, stick="wens", padx=10, pady=10)

win.grid_columnconfigure(0, minsize=100)
win.grid_columnconfigure(1, minsize=100)
win.grid_columnconfigure(2, minsize=100)
win.grid_columnconfigure(3, minsize=100)
win.grid_rowconfigure(0, minsize=50)
win.grid_rowconfigure(1, minsize=100)
win.grid_rowconfigure(2, minsize=100)
win.grid_rowconfigure(3, minsize=100)
win.grid_rowconfigure(4, minsize=100)


def print_info(widget, depth=0):
    widget_class = widget.winfo_class()
    widget_width = widget.winfo_width()
    widget_height = widget.winfo_height()
    widget_x = widget.winfo_x()
    widget_y = widget.winfo_y()
    print(" "*depth + f"{widget_class} width={widget_width} height={widget_height} x={widget_x} y={widget_y}")
    for child in widget.winfo_children():
        print_info(child, depth+1)

win.update()
print_info(win)

win.bind('<Key>', press_key)

win['bg'] = "#FFEEAA"
#win.config(width=400, height=40, padx=2,pady=30)
win.geometry(f"400x450+450+200")
win.resizable(False, False)
win.title("Calculator")
icon = PhotoImage(file="calc.png")
win.iconphoto('wm', icon)
win.mainloop()