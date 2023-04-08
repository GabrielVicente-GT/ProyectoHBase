import tkinter as tk
import json

#create "employees", "personal_data", "profesional_data"

def submit_text():
    command = entry.get()
    # si es create
    if command.startswith('create'):
        args = command.split(',')
        print(args)
        table_name = args[0].strip().replace('create ', '').replace('"', '')
        print("table_name: ", table_name)
        columns = [col.strip() for col in args[1:]]
        create_table(table_name, columns)
        output.config(text=f'Table {table_name} created with columns {columns}')
        
    else:
        output.config(text="Comando no reconocido")

# Función para crear la tabla
def create_table(table_name, columns):
    table = {1: {col: '' for col in columns}}
    # Eliminar las comillas del nombre de la tabla
    table_name = table_name.replace('"', '')
    with open(f'{table_name}.json', 'w') as f:
        json.dump(table, f)





#generacion del interfaz y lectura de texto
root = tk.Tk()

# Crear un cuadro de texto
entry = tk.Entry(root)
entry.pack()

# Crear un botón de submit
submit_button = tk.Button(root, text="Submit", command=submit_text)
submit_button.pack()

# Crear un cuadro de texto para la salida
output = tk.Label(root, text="")
output.pack()

root.mainloop()

