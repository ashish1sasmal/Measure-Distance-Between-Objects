import cv2
import numpy as np
import imutils
import time
from imutils import contours
import sys
from imutils import perspective
from scipy.spatial import distance as dist

from live_cam import live

fourcc = cv2.VideoWriter_fourcc(*'XVID')
res = cv2.VideoWriter('Results/output.avi',fourcc, 20.0, (640,480))

cv2.namedWindow("Sort",cv2.WINDOW_NORMAL)

# img = cv2.imread("Test/"+sys.argv[1])

def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)


while True:
	img=live()
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray, (5,5), 0)
	canny = cv2.Canny(gray,100,220)
	canny = cv2.dilate(canny, None, iterations=1)
	canny = cv2.erode(canny, None, iterations=1)

	# thresh = cv2.threshold(gray, 110, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

	cnts = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	out = img.copy()

	print(len(cnts))

	cnts,_ = contours.sort_contours(cnts)
	ind=1

	pixelsPerMetric=None

	centroids = []

	for (i,c) in enumerate(cnts):
		if cv2.contourArea(c)>105:
			box = cv2.minAreaRect(c)
			box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
			box = np.array(box, dtype="int")
			print("Object #{}".format(ind))
			print(box)
			print()
			cv2.drawContours(out, [box], -1, (0, 255, 0), 2)

			box = perspective.order_points(box)
			# for (x, y) in rect:
			# 	cv2.putText(out, "Object #{}".format(ind),(int(rect[0][0] - 15), int(rect[0][1] - 15)),cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 255), 2)

			(tl, tr, br, bl) = box

			(tltrX, tltrY) = midpoint(tl, tr)
			(blbrX, blbrY) = midpoint(bl, br)
			# compute the midpoint between the top-left and top-right points,
			# followed by the midpoint between the top-righ and bottom-right
			(tlblX, tlblY) = midpoint(tl, bl)
			(trbrX, trbrY) = midpoint(tr, br)
			# draw the midpoints on the image

			c1x, c1y = (int(tltrX)+int(blbrX))//2, (int(tltrY)+int(blbrY))//2
			centroids.append([c1x,c1y])
			cv2.circle(out, (c1x,c1y), 10, (3,230,255), -1)
			cv2.circle(out, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
			cv2.circle(out, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
			cv2.circle(out, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
			cv2.circle(out, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)
			# draw lines between the midpoints
			cv2.line(out, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),(255, 0, 255), 2)
			cv2.line(out, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),(255, 0, 255), 2)

			dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
			dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

			if pixelsPerMetric is None:
				pixelsPerMetric = dB / 2.5

			dimA = dA / pixelsPerMetric
			dimB = dB / pixelsPerMetric

			if len(centroids)>1:
				for ind in range(len(centroids)-1):
					cv2.line(out, (centroids[ind][0], centroids[ind][1]), (centroids[ind+1][0], centroids[ind+1][1]),(0, 0, 255), 2)
					dis = dist.euclidean((centroids[ind][0], centroids[ind][1]), (centroids[ind+1][0], centroids[ind+1][1]))

					dis = dis /pixelsPerMetric

					lx = (centroids[ind][0] + centroids[ind+1][0])//2
					ly = (centroids[ind][1] + centroids[ind+1][1])//2
					cv2.putText(out, "{:.1f}cm".format(dis),(int(lx - 15), int(ly - 10)), cv2.FONT_HERSHEY_SIMPLEX,0.75, (255, 3, 83), 2)


			cv2.putText(out, "{:.1f}cm".format(dimA),(int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,0.65, (255, 255, 255), 2)
			cv2.putText(out, "{:.1f}cm".format(dimB),(int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,0.65, (255, 255, 255), 2)
			ind+=1



	cv2.imshow("Sort",out)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break


    # key = cv2.waitKey(1) & 0xFF
    # if key == ord("q"):
    #     break

cv2.destroyAllWindows()
