import cv2, os, sys, datetime

outputFolder = 'outputFolder'
myFiles = os.listdir('.')
if outputFolder not in myFiles:
    os.mkdir(outputFolder)

myVideo = cv2.VideoCapture(0 + cv2.CAP_DSHOW)

print("Key 'q' for quit")
print("Key 's' for save")

while(myVideo.isOpened()):
    myOK, myFrame = myVideo.read()

    myFrame = cv2.flip(myFrame, 1) # Flip horizontally and vertically
    myFrame = cv2.resize(myFrame, (1280, 960))

    cv2.imshow("myFrame", myFrame)

    myKey = cv2.waitKey(1) & 0xFF
    if myKey == ord('q'): # Press the q key to exit the program
        break
    if myKey == ord('s'): # Press the s key to exit the program
        currentTime = datetime.datetime.now()
        currentTimeString = currentTime.strftime("%Y-%m-%d_%H-%M-%S")
        outputFile = 'screenShot-%s-%s.png' % (str.split(str.split(sys.argv[0], os.sep)[-1], '.')[0], currentTimeString)
        cv2.imwrite( os.path.join( outputFolder, outputFile ), myFrame )
myVideo.release()
cv2.destroyAllWindows()