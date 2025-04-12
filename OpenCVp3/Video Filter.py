import cv2
import numpy as np

# Wczytywanie strumienia wideo
video = cv2.VideoCapture('PlakushkoMaksym.mp4')

# Tworzenie obiektu do zapisu przetworzonego strumienia wideo
output_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
output_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
output_video = cv2.VideoWriter('PlakushkoMaksym1.mp4', cv2.VideoWriter_fourcc(*'MJPG'), 30, (output_width, output_height))

while video.isOpened():
    ret, frame = video.read()

    if not ret:
        break

    # Przetwarzanie klatki - ekstrakcja wybranych kolorów
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Definiowanie zakresu kolorów do ekstrakcji
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])
    lower_green = np.array([40, 50, 50])
    upper_green = np.array([80, 255, 255])
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([20, 255, 255])

    # Ekstrakcja poszczególnych kolorów
    blue_mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)
    green_mask = cv2.inRange(hsv_frame, lower_green, upper_green)
    red_mask = cv2.inRange(hsv_frame, lower_red, upper_red)

    # Zastosowanie maski do klatki
    blue_object = cv2.bitwise_and(frame, frame, mask=blue_mask)
    green_object = cv2.bitwise_and(frame, frame, mask=green_mask)
    red_object = cv2.bitwise_and(frame, frame, mask=red_mask)

    # Łączenie wyekstrahowanych obiektów w jednym obrazie
    merged_frame = np.hstack((frame, blue_object, green_object, red_object))

    # Wyświetlanie przetworzonego strumienia wideo
    cv2.imshow('Extracted Colors', merged_frame)

    # Zapisywanie przetworzonego strumienia wideo
    output_video.write(merged_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Zamykanie strumieni wideo
video.release()
output_video.release()

# Zamykanie okien
cv2.destroyAllWindows()
