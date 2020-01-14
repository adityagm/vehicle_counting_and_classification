import cv2
import numpy as np
import Vehicle
from tracker import CentroidTracker
import time
from excel import excel, setName
from datetime import datetime


def vehicleCount():
    cnt_up = 0
    cnt_down = 0
    MTR = 0
    LV = 0
    HV = 0
    DownMTR = 0
    DownLV = 0
    DownHV = 0
    video_name = 'traffic1.MP4'
    # set input video

    datetime_now = datetime.now()
    date_time = datetime_now.strftime("%m%d%Y_%H%M")

    # to split the name of the video so that .mp4 does not conflict with .csv
    vid_name = video_name.split('.', 1)
    filename = vid_name[0] + '_' + date_time + '.csv'

    setName(filename)
    cap = cv2.VideoCapture(video_name)
    cap.set(cv2.CAP_PROP_FPS, 18)

    # Capture the properties of VideoCapture to console (mengambil properties video eg. width, height dll)
    for i in range(19):
        # print properties video
        print(i, cap.get(i))

    # mengambil width dan heigth video dari properties (value w posisi ke 3, h posisi ke 4)
    w = cap.get(3)
    print('Width', w)
    h = cap.get(4)
    print('Height', h)
    # luas frame area h*w
    frameArea = h * w
    areaTH = frameArea / 800
    print('Area Threshold', areaTH)
    # Input/Output Lines
    # yang itung kendaraan turun (biru)
    line_up = int(2 * (h / 5))
    print("line_up", line_up)
    # yang itung kendaraan naik (merah), untuk setting garis
    line_down = int(3 * (h / 5))
    print("line_down", line_down)
    up_limit = int(1 * (h / 5))
    down_limit = int(4 * (h / 5))

    print("Red line y:", str(line_down))
    print("Blue line y:", str(line_up))
    line_down_color = (255, 0, 0)
    line_up_color = (0, 0, 255)
    # set height garis
    pt1 = [0, line_down]
    # set lebar garis sesuai width video
    pt2 = [w, line_down]
    pts_L1 = np.array([pt1, pt2], np.int32)
    pts_L1 = pts_L1.reshape((-1, 1, 2))
    # set height garis
    pt3 = [0, line_up]
    # set lebar garis sesuai width video
    pt4 = [w, line_up]
    pts_L2 = np.array([pt3, pt4], np.int32)
    pts_L2 = pts_L2.reshape((-1, 1, 2))

    pt5 = [0, up_limit]
    pt6 = [w, up_limit]
    pts_L3 = np.array([pt5, pt6], np.int32)
    pts_L3 = pts_L3.reshape((-1, 1, 2))
    pt7 = [0, down_limit]
    pt8 = [w, down_limit]
    pts_L4 = np.array([pt7, pt8], np.int32)
    pts_L4 = pts_L4.reshape((-1, 1, 2))

    # Create the background subtractor
    fgbg = cv2.createBackgroundSubtractorMOG2()

    kernelOp = np.ones((3, 3), np.uint8)
    kernelOp2 = np.ones((5, 5), np.uint8)
    kernelCl = np.ones((11, 11), np.uint8)

    # Variables
    font = cv2.FONT_HERSHEY_SIMPLEX
    vehicles = []
    max_p_age = 5
    tracker = CentroidTracker()

    while (cap.isOpened()):
        # read a frame
        ret, frame = cap.read()

        for i in vehicles:
            i.age_one()  # age every person on frame

        #################
        # PREPROCESSING #
        #################
        fgmask = fgbg.apply(frame)
        fgmask2 = fgbg.apply(frame)

        # Binary to remove shadow
        try:
            # cv2.imshow('Frame', frame)
            # cv2.imshow('Backgroud Subtraction', fgmask)
            ret, imBin = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
            ret, imBin2 = cv2.threshold(fgmask2, 200, 255, cv2.THRESH_BINARY)
            # Opening (erode->dilate) to remove noise
            mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernelOp)
            mask2 = cv2.morphologyEx(imBin2, cv2.MORPH_OPEN, kernelOp)
            # Closing (dilate->erode) to join white region
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernelCl)
            mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernelCl)
            cv2.imshow('Image Threshold', cv2.resize(fgmask, (400, 300)))
            # cv2.imshow('Image Threshold2', cv2.resize(fgmask2, (400, 300)))
            cv2.imshow('Masked Image', cv2.resize(mask, (400, 300)))
            # cv2.imshow('Masked Image2', cv2.resize(mask2, (400, 300)))
        except:
            # If there is no more frames to show...
            print('EOF')
            print('UP:', cnt_up)
            print('DOWN:', cnt_down)
            break

        ##################
        ## FIND CONTOUR ##
        ##################

        _, contours0, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt in contours0:

            # originnal method to draw the contours and bounding boxes
            # membuat kontur/garis mengikuti objek bergerak
            # cv2.drawContours(frame, cnt, -1, (0, 255, 0), 3, 8)

            # trying to have a rotating bounding box as well so that when the vehicle is at an angle,
            # we still can fit the vevicle
            area = cv2.contourArea(
                cnt)  # needed to compute the area of the vehicle, all others that exceed the threshold area are ignored

            cv2.drawContours(frame, cnt, -1, (0, 255, 0), 3, 8)
            # mengatur ukuran kendaraan yang dideteksi

            if areaTH < area < 20000:

                #     print 'Area:::', area
                ################
                #   TRACKING   #
                ################
                M = cv2.moments(cnt)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                x, y, w, h = cv2.boundingRect(cnt)  # for simple bounding box pass 'cnt', for rotating box pass 'box'
                j = 0
                k = 0
                dim = 0
                perimeter = cv2.arcLength(cnt, True)
                new = True
                for i in vehicles:

                    if abs(x - i.getX()) <= w and abs(y - i.getY()) <= h:
                        cv2.putText(frame, "ID {}".format(i.getId()), (int(x + w / 2), int(y - 5)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
                        new = False
                        i.updateCoords(cx, cy)  # Update the coordinates in the object and reset age
                        start = time.time()
                        if i.crossed(line_down, line_up) == 1:
                            i.record_crossed(1, cx, cy)
                        elif i.crossed(line_down, line_up) == -1:
                            i.record_crossed(-1, cx, cy)

                        if i.going_UP(line_down, line_up):

                            roi = frame[y:y + h, x:x + w]
                            cv2.imshow('Region of Interest', roi)
                            height = h
                            width = w

                            if dim < 300:
                                MTR += 1
                                classification = "MTR"
                            elif dim < 500:
                                LV += 1
                                classification = "LV"
                            elif dim > 500:
                                HV += 1
                                classification = "HV"
                            print('Height:::', height)
                            print('Width:::', width)
                            print('Perimeter:::', dim)
                            toc = time.strftime("%c")
                            print("ID:", i.getId(), 'crossed going down at', toc)

                            cnt_up += 1

                        if i.going_DOWN(line_down, line_up):

                            height = y + h
                            width = x + w
                            dim = width * height
                            roi = frame[y:y + h, x:x + w]
                            cv2.imshow('Region of Interest', roi)
                            if dim < 3000:
                                MTR += 1
                                classification = "MTR"
                            elif 5000 < dim < 550000:
                                LV += 1
                                classification = "LV"
                            elif dim > 550000:
                                HV += 1
                                classification = "HV"
                            print('Height:::', height)
                            print('Width:::', width)
                            print('Perimeter:::', perimeter)
                            toc = time.strftime("%c")
                            print("ID:", i.getId(), 'crossed going down at', toc)
                            cnt_down += 1
                            end = time.time()

                        break
                    if i.getState() == 1:
                        if i.getDir() == 'down' and i.getY() > line_down: #i.getY() > down_limit:
                            i.setDone()
                        elif i.getDir() == 'up' and i.getY() < line_up: #i.getY() < up_limit:
                            i.setDone()
                    if i.timedOut() and i.getState() == 1:
                        excel(i.getId(), classification, perimeter, i.avgSpeed(), i.getDir(), toc)
                        # Remove from the list person
                        # idx = vehicles.index(i)
                        # print(vehicles.index())
                        tracker.deregister(i.getId())
                        vehicles.remove(i)
                        del i
                if new:
                    centroid = [cx, cy]
                    pid = tracker.update(centroid)
                    p = Vehicle.MyVehicle(pid, cx, cy, max_p_age)
                    vehicles.append(p)

                ##################
                ##   DRAWING    ##
                ##################
                cv2.circle(frame, (int(cx), int(cy)), 5, (0, 0, 255), -1)
                img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        ###############
        ##   IMAGE   ##
        ###############
        MTR_up = 'Motor: ' + str(MTR)
        LV_up = 'Mobil: ' + str(LV)
        HV_up = 'Truck/Bus: ' + str(HV)

        ##############################################################################################################
        # UPDATE LIST
        List = (LV + HV + MTR)

        ##############################################################################################################
        frame = cv2.polylines(frame, [pts_L1], False, line_down_color, thickness=2)
        frame = cv2.polylines(frame, [pts_L2], False, line_up_color, thickness=2)
        frame = cv2.polylines(frame, [pts_L3], False, (255, 255, 255), thickness=1)
        frame = cv2.polylines(frame, [pts_L4], False, (255, 255, 255), thickness=1)
        # cv2.putText(frame, str_up, (10,40),font,2,(255,255,255),2,cv2.LINE_AA)
        # cv2.putText(frame, str_up, (10,40),font,2,(0,0,255),1,cv2.LINE_AA)
        cv2.putText(frame, MTR_up, (10, 40), font, 2, (255, 255, 255), 4, cv2.LINE_AA)
        cv2.putText(frame, MTR_up, (10, 40), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
        cv2.putText(frame, LV_up, (10, 90), font, 2, (255, 255, 255), 4, cv2.LINE_AA)
        cv2.putText(frame, LV_up, (10, 90), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
        cv2.putText(frame, HV_up, (10, 140), font, 2, (255, 255, 255), 4, cv2.LINE_AA)
        cv2.putText(frame, HV_up, (10, 140), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

        cv2.imshow('Frame', cv2.resize(frame, (640, 480)))
        # cv2.imshow('Frame', cv2.resize(frame, (1280, 720)))
        # cv2.imshow('Backgroud Subtraction', fgmask)

        # Abort and exit with 'Q' or ESC
        k = cv2.waitKey(10) & 0xff
        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    vehicleCount()
