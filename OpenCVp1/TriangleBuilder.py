import cv2, numpy as np, os, sys

myXoffsets = [0, 340, 680, 1020, 0, 340, 680, 1020]
myYoffsets = [0, 0, 0, 0, 380, 380, 380, 380]

myParameters = [128, 64, 32, 16, 8, 4, 2]

color = (255, 255, 255)
color2 = (0, 0, 0)
triangle = [(20, 330), (330, 20), (330, 330)]
img = np.zeros((342, 342, 3), np.uint8)

triangle2 = tuple([list(map(lambda num: num // myParameters[6] + 128,
                            trianglex2)) for trianglex2 in triangle])

triangle3 = tuple([list(map(lambda num: num // myParameters[5] + 192,
                            trianglex3)) for trianglex3 in triangle])

triangle4 = tuple([list(map(lambda num: num // myParameters[4] + 224,
                            trianglex4)) for trianglex4 in triangle])

triangle5 = tuple([list(map(lambda num: num // myParameters[3] + 240,
                            trianglex5)) for trianglex5 in triangle])

triangle6 = tuple([list(map(lambda num: num // myParameters[2] + 248,
                            trianglex6)) for trianglex6 in triangle])

triangle7 = tuple([list(map(lambda num: num // myParameters[1] + 252,
                            trianglex7)) for trianglex7 in triangle])

triangle8 = tuple([list(map(lambda num: num // myParameters[0] + 254,
                            trianglex8)) for trianglex8 in triangle])

cv2.fillPoly(img, np.array([triangle]), color)
cv2.imshow('window', img)
cv2.moveWindow('window', myXoffsets[0], myYoffsets[0])
cv2.imwrite('outputFolder\triangle.jpg', img)

cv2.fillPoly(img, np.array([triangle2]), color2)
cv2.imshow('window1', img)
cv2.moveWindow('window1', myXoffsets[1], myYoffsets[1])
cv2.imwrite('outputFolder\triangle1.jpg', img)

cv2.fillPoly(img, np.array([triangle3]), color)
cv2.imshow('window2', img)
cv2.moveWindow('window2', myXoffsets[2], myYoffsets[2])
cv2.imwrite('outputFolder\triangle2.jpg', img)

cv2.fillPoly(img, np.array([triangle4]), color2)
cv2.imshow('window3', img)
cv2.moveWindow('window3', myXoffsets[3], myYoffsets[3])
cv2.imwrite('outputFolder\triangle3.jpg', img)

cv2.fillPoly(img, np.array([triangle5]), color)
cv2.imshow('window4', img)
cv2.moveWindow('window4', myXoffsets[4], myYoffsets[4])
cv2.imwrite('outputFolder\triangle4.jpg', img)

cv2.fillPoly(img, np.array([triangle6]), color2)
cv2.imshow('window5', img)
cv2.moveWindow('window5', myXoffsets[5], myYoffsets[5])
cv2.imwrite('outputFolder\triangle5.jpg', img)

cv2.fillPoly(img, np.array([triangle7]), color)
cv2.imshow('window6', img)
cv2.moveWindow('window6', myXoffsets[6], myYoffsets[6])
cv2.imwrite('outputFolder\triangle6.jpg', img)

cv2.fillPoly(img, np.array([triangle8]), color2)
cv2.imshow('window7', img)
cv2.moveWindow('window7', myXoffsets[7], myYoffsets[7])
cv2.imwrite('outputFolder\triangle7.jpg', img)

cv2.waitKey(0)
cv2.destroyAllWindows()
