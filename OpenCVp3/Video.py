import cv2
import numpy as np
import math

# Parametry animacji
width, height = 640, 480  # Rozmiar ramki wideo
fps = 30  # Liczba klatek na sekundę
duration = 10  # Czas trwania animacji (w sekundach)
object_count = 3  # Liczba obiektów w animacji

# Tworzenie strumienia wideo
video_writer = cv2.VideoWriter('PlakushkoMaksym.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

# Generowanie klatek wideo
frame_count = int(fps * duration)
for i in range(frame_count):
    t = i / float(fps)  # Czas dla bieżącej klatki

    frame = np.zeros((height, width, 3), dtype=np.uint8)  # Pusty obraz

    # Generowanie pozycji i kolorów obiektów
    for j in range(object_count):
        # Parametry krzywych Lissajous
        freq_x = 2 * (j + 1)  # Częstotliwość dla osi x
        freq_y = 3 * (j + 1)  # Częstotliwość dla osi y
        phase = 2 * math.pi * (j / float(object_count))  # Faza

        # Obliczanie pozycji obiektu na podstawie czasu t
        x = int(width / 2 + width / 4 * math.sin(freq_x * t + phase))
        y = int(height / 2 + height / 4 * math.sin(freq_y * t))

        # Wybór koloru obiektu
        color = (0, 0, 0)  # Domyślnie czarny kolor
        if j == 0:
            color = (255, 0, 0)  # Pierwszy obiekt - niebieski kolor
        elif j == 1:
            color = (0, 255, 0)  # Drugi obiekt - zielony kolor
        elif j == 2:
            color = (0, 0, 255)  # Trzeci obiekt - czerwony kolor

        # Rysowanie obiektu na klatce
        cv2.circle(frame, (x, y), 20, color, -1)

    # Zapisywanie klatki do strumienia wideo
    video_writer.write(frame)

# Zamykanie strumienia wideo
video_writer.release()
