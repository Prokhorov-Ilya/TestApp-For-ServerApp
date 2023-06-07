import time
import random
import pandas as pd
import numpy as np
import os
import PySimpleGUI as sg
import threading


def traffic_light_handler(rows_to_change, stop_event):
    while True:
        if stop_event.is_set():
            break
        for row_number in rows_to_change:
            eight_column = df.iloc[row_number, 7]
            seventh_column = df.iloc[row_number, 6]
            fifth_column = df.iloc[row_number, 4]
            if eight_column > seventh_column or eight_column < fifth_column:
                if fifth_column == 0:
                    cell_value = random.randint(0, seventh_column)
                else:
                    cell_value = random.randint(fifth_column, seventh_column)
            else:
                cell_value = random.randint(seventh_column + 1, seventh_column + 6)
            df.iloc[row_number, -1] = cell_value
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce').astype('Int64')
        df.to_csv('../ServerApp/docs/' + filename, index=False)
        print('сохранение файла успешно')
        time.sleep(10)

def randomGenerator():
    stop_event = threading.Event()
    thread = None
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':
            if thread is not None and thread.is_alive():
                stop_event.set()  # Установка флага остановки
                thread.join()
            break
        rows_to_change = [int(row) for row in values['rows_to_change'].split(",")]
        if event == 'OK':
            cell_values = values['cell_values']
            if not cell_values:
                sg.popup("Ошибка: не введены значения для изменения.")
                continue
            cell_values = [int(value) for value in values['cell_values'].split(",")]
            if len(rows_to_change) != len(cell_values):
                sg.popup("Ошибка: количество строк не совпадает с количеством чисел.")
                continue
            for i in range(len(rows_to_change)):
                row_number = rows_to_change[i]
                cell_value = cell_values[i]
                if row_number >= len(df) or row_number < 0:
                    sg.popup(f"Ошибка: неправильный номер строки {row_number}.")
                    continue
                df.iloc[row_number, -1] = cell_value
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce').astype('Int64')
            df.to_csv('../ServerApp/docs/' + filename, index=False)
            sg.popup('сохранение файла успешно')
        if event == 'traffic_light':
            if thread is None or not thread.is_alive():
                stop_event.clear()  # Сброс флага остановки
                thread = threading.Thread(target=traffic_light_handler, args=(rows_to_change, stop_event))
                thread.start()
        if event == 'Stop':
            if thread is not None and thread.is_alive():
                stop_event.set()  # Установка флага остановки
                thread.join()
                sg.popup('Светофор завершил работу')


# Загрузка DataFrame из файла
csv_files = [f for f in os.listdir('../ServerApp/docs/') if f.endswith('.csv')]
filename = max(csv_files)
df = pd.read_csv('../ServerApp/docs/' + filename)
# Создание графического интерфейса
layout = [
    [sg.Text('Введите номера строк через запятую (от 1 до {}): '.format(len(df) - 1))],
    [sg.InputText(key='rows_to_change')],
    [sg.Text('Введите числа для изменения в последней ячейке выбранных строк через запятую: ')],
    [sg.InputText(key='cell_values')],
    [sg.Button('OK', key='OK'), sg.Button('Cancel')],
    [sg.Button('Светофор', key='traffic_light'), sg.Button('Stop', key='Stop')]
]
window = sg.Window('Редактирование CSV файла', layout, element_justification='c')  # Изменение размера окна
randomGenerator()
window.close()

