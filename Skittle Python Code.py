import time

import numpy as np
import serial
from cv2 import *
from scipy.stats import itemfreq

COLOUR_BOUNDARIES = []
COLOUR_RANGE = 25
COLOURS = ["No Skittle", "Cup 1", "Cup 2", "Cup 3", "Cup 4", "Cup 5", "Null"]
SERIAL_OPTION = {0: "n",  # No skittle
                 1: "r",  # First skittle
                 2: "g",  # Second skittle
                 3: "y",  # Third skittle
                 4: "o",  # Fourth skittle
                 5: "p",  # Fifth skittle
                 6: "u",  # Unknown skittle
                 7: "l",  # Toggle stir
                 8: "f"}  # Force stir on

ser = serial.Serial('COM3', 9600, timeout=0)


def main():
    time.sleep(4)
    # initialize the camera
    cam = VideoCapture(1)  # 0 -> index of camera

    print("Enter a command or 'h' for a list of commands.")

    namedWindow("Image")

    while True:

        choice = waitKey(100) & 0xFF
        if choice == 27:  # escape
            break
        elif choice == 32:  # space

            if len(COLOUR_BOUNDARIES) < 6:

                # done twice to refresh internal camera buffer
                valid_frame, img = cam.read()
                valid_frame, img = cam.read()

                while not valid_frame:
                    valid_frame, img = cam.read()
                    time.sleep(0.1)

                dominant_colour = get_dominant_colour(img)
                #print(dominant_colour)

                COLOUR_BOUNDARIES.append([[dominant_colour[0] - COLOUR_RANGE,
                                           dominant_colour[1] - COLOUR_RANGE,
                                           dominant_colour[2] - COLOUR_RANGE],
                                          [dominant_colour[0] + COLOUR_RANGE,
                                           dominant_colour[1] + COLOUR_RANGE,
                                           dominant_colour[2] + COLOUR_RANGE]])

                img = img[320:450, 250:420]
                imshow("Image", img)

                ser.write(SERIAL_OPTION[len(COLOUR_BOUNDARIES) - 1])

                time.sleep(2.0)

            else:
                print("All colour boundaries set!")

        elif choice == ord('d'):  # Sort one skittle

            # done twice to refresh internal camera buffer
            valid_frame, img = cam.read()
            valid_frame, img = cam.read()

            dominant_colour = get_dominant_colour(img)
            #print(dominant_colour)

            choice = get_colour_choice(dominant_colour)

            ser.write(SERIAL_OPTION[choice])

            img = img[320:450, 250:420]
            imshow("Image", img)

            print(COLOURS[choice])

            time.sleep(2)

        elif choice == ord('a'):  # Automatically sort until no skittle for 3 checks

            empty_count = 0
            ser.write(SERIAL_OPTION[8])  # force stir on

            while True:

                # done twice to refresh internal camera buffer
                valid_frame, img = cam.read()
                valid_frame, img = cam.read()

                dominant_colour = get_dominant_colour(img)
                choice = get_colour_choice(dominant_colour)

                ser.write(SERIAL_OPTION[choice])

                img = img[320:450, 250:420]
                imshow("Image", img)

                print(COLOURS[choice])

                # if empty detected 3 times in a row break
                if choice == 0:
                    empty_count += 1

                    if empty_count == 3:
                        break
                else:
                    empty_count = 0

                time.sleep(2)

            ser.write(SERIAL_OPTION[7])  # Toggle stir off

        elif choice == ord('1'):  # Move to position 1
            ser.write(SERIAL_OPTION[1])
            time.sleep(2)

        elif choice == ord('2'):  # Move to position 2
            ser.write(SERIAL_OPTION[2])
            time.sleep(2)

        elif choice == ord('3'):  # Move to position 3
            ser.write(SERIAL_OPTION[3])
            time.sleep(2)

        elif choice == ord('4'):  # Move to position 4
            ser.write(SERIAL_OPTION[4])
            time.sleep(2)

        elif choice == ord('5'):  # Move to position 5
            ser.write(SERIAL_OPTION[5])
            time.sleep(2)

        elif choice == ord('l'):  # Stir motor toggle
            ser.write(SERIAL_OPTION[7])
            time.sleep(0.1)
        elif choice == ord('h'):
            print("Commands:\n"
                  "ESCAPE: terminates the program.\n"
                  "SPACE: Skittle Calibration.\n"
                  "D: Single Skittle Evaluation.\n"
                  "A: Continuous Skittle Evaluation.\n"
                  "L: Stirring Motor Toggle.\n"
                  "1-5: Move to position.")
            time.sleep(1)

        if cv2.getWindowProperty('Image', 0) < 0:
            break
    cv2.destroyAllWindows()


def get_dominant_colour(image):
    # crop the image
    image = image[320:450, 250:420]

    arr = np.float32(image)
    pixels = arr.reshape((-1, 3))

    n_colors = 3
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, centroids = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)

    palette = np.uint8(centroids)
    quantized = palette[labels.flatten()]
    quantized = quantized.reshape(image.shape)

    return palette[np.argmax(itemfreq(labels)[:, -1])]


# Determines if the dominant colour of the image matches one of the define colour ranges
def get_colour_choice(dominant_colour):
    choice = 6

    for i in range(len(COLOUR_BOUNDARIES)):
        lower = COLOUR_BOUNDARIES[i][0]
        upper = COLOUR_BOUNDARIES[i][1]

        if (lower[0] <= dominant_colour[0] <= upper[0] and
                        lower[1] <= dominant_colour[1] <= upper[1] and
                        lower[2] <= dominant_colour[2] <= upper[2]):
            choice = i

    return choice


main()
cv2.destroyAllWindows()
