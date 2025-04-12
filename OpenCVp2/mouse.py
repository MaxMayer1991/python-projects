import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
import threading

def matplotlibService( myFile ):
    plt.figure().canvas.callbacks.connect('button_press_event', onClick)
    myImage = plt.imread(myFile)
    plt.imshow(myImage)
    plt.axis("off")
    plt.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
    plt.show()
    
def onClick(event):
    global clickNumber, screenPoints, controlPoints
    if clickNumber < 4:
        point = [int(event.xdata), int(event.ydata)]
        screenPoints.append(point)
        clickNumber += 1
    elif clickNumber < 8:
        point = [int(event.xdata), int(event.ydata)]
        controlPoints.append(point)
        clickNumber += 1
        if clickNumber == 8:
            processData()
#--------------------------------------------------
def processData():
    print('realPoints:', realPoints)
    print('screenPoints:', screenPoints)
    a = np.array([[screenPoints[0][0], screenPoints[0][1], 1, 0, 0, 0, -realPoints[0][0] * screenPoints[0][0],
                   -realPoints[0][0] * screenPoints[0][1]],
                  [screenPoints[1][0], screenPoints[1][1], 1, 0, 0, 0, -realPoints[1][0] * screenPoints[1][0],
                   -realPoints[1][0] * screenPoints[1][1]],
                  [screenPoints[2][0], screenPoints[2][1], 1, 0, 0, 0, -realPoints[2][0] * screenPoints[2][0],
                   -realPoints[2][0] * screenPoints[2][1]],
                  [screenPoints[3][0], screenPoints[3][1], 1, 0, 0, 0, -realPoints[3][0] * screenPoints[3][0],
                   -realPoints[3][0] * screenPoints[3][1]],
                  [0, 0, 0, screenPoints[0][0], screenPoints[0][1], 1, -realPoints[0][1] * screenPoints[0][0],
                   -realPoints[0][1] * screenPoints[0][1]],
                  [0, 0, 0, screenPoints[1][0], screenPoints[1][1], 1, -realPoints[1][1] * screenPoints[1][0],
                   -realPoints[1][1] * screenPoints[1][1]],
                  [0, 0, 0, screenPoints[2][0], screenPoints[2][1], 1, -realPoints[2][1] * screenPoints[2][0],
                   -realPoints[2][1] * screenPoints[2][1]],
                  [0, 0, 0, screenPoints[3][0], screenPoints[3][1], 1, -realPoints[3][1] * screenPoints[3][0],
                   -realPoints[3][1] * screenPoints[3][1]]])

    b = np.array(
        [realPoints[0][0], realPoints[1][0], realPoints[2][0], realPoints[3][0], realPoints[0][1], realPoints[1][1],
         realPoints[2][1], realPoints[3][1]])
    coeffs = np.linalg.solve(a, b)

    print(70 * '-')
    print('a = ', a)
    print(70 * '-')
    print('b = ', b)
    print(70 * '-')
    print('x = ', coeffs)
    print(70 * '-')

    def xr(xm, ym):
        return (coeffs[0] * xm + coeffs[1] * ym + coeffs[2]) / (coeffs[6] * xm + coeffs[7] * ym + 1)

    def yr(xm, ym):
        return (coeffs[3] * xm + coeffs[4] * ym + coeffs[5]) / (coeffs[6] * xm + coeffs[7] * ym + 1)

    print('Przeliczenie punktow monitorowych na rzeczywiste:')
    letters = ['A', 'B', 'C', 'D']
    i = 0
    for point in controlPoints:
        xm = point[0]
        ym = point[1]

        print(letters[i], point, '->', int(10 * xr(xm, ym)) / 10, int(10 * yr(xm, ym)) / 10)
        i += 1

    cv2.waitKey(0)
    cv2.destroyAllWindows()
#--------------------------------------------------
inputFolder = 'outputFolder'
myFiles = os.listdir(inputFolder)
myFiles = [file for file in myFiles if '.png' in file]
myText = ''
myNumber = 0
for myFile in myFiles:
    myNumber += 1
    myText += '%2d - %s\n' % (myNumber, myFile)
myText += 30 * '-' + '\n'
myText += 'select a file...'
myFileName = myFiles[int(input(myText)) - 1]
print(myFileName)
myFile = os.path.join(inputFolder, myFileName)
#-------------------

clickNumber = 0
screenPoints = []
controlPoints = []

#realPoints = [[80.0, 125.0], [80.0, 55.0], [140.0, 140.0], [150.0, 80.0]] #1 2 3 4
realPoints = [[70.0, 160.0], [50.0, 90.0], [190.0, 140.0], [175.0, 45.0]] #A B C D
matplotlibService(myFile)




