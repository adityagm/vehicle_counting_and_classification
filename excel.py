import csv

filename = ''
flag = 0
fieldnames = ['vehicle ID', 'classification', 'perimeter', 'avg speed', 'direction', 'time of crossing']


def setName(name):
    global filename
    filename = name


def excel(vid, vehicle_classification, perimeter, speed, direction, toc):
    global filename, flag, fieldnames

    with open(filename, 'a', newline='') as fp:
        filewrite = csv.writer(fp, delimiter=',')
        if flag == 0:
            filewrite.writerow(fieldnames)
            flag = 1
        else:
            filewrite.writerow([vid, vehicle_classification, perimeter, speed, direction, toc])
