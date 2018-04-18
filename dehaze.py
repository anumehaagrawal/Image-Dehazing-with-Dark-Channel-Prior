"""Single image dehazing."""
from __future__ import division
import cv2
import numpy as np


class Channel_value:
    val = -1.0
    intensity = -1.0


def atmospheric_light(img, gray):
    top = int(img.shape[0] * img.shape[1] * 0.001)
    print(img.shape[0],img.shape[0])
    toplist = [Channel_value()] * top
    dark_channel = darkchannel(img)
    print(dark_channel)
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            # Accessing the rgb values separately
            val = img.item(y, x, dark_channel)
            # Calculating the intensity in the gray scale image so it is easy to find the lightest one
            intensity = gray.item(y, x)
            # This finds the highest intensity of the dark channel pixels
            for t in toplist:
                if t.val < val or (t.val == val and t.intensity < intensity):
                    t.val = val
                    t.intensity = intensity
                    break
    # This is compared with the pixels in the dark channel and max one is taken as atmospheric light
    max_channel = Channel_value()
    for t in toplist:
        if t.intensity > max_channel.intensity:
            max_channel = t
    #Thus we calculate A which is used in calculation of dehazing   
    return max_channel.intensity


def darkchannel(img):
    # This is the lightest of the three channels R,G,B to give the pixel with least intensity . This is generally around 0.
    return np.unravel_index(np.argmin(img), img.shape)[2]


def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))


def dehaze(img, light_intensity, windowSize, t0, w ,roh):
    # Calculating the size of image
    size = (img.shape[0], img.shape[1])
    # Designing layout of the output image
    outputimg = np.zeros(img.shape, img.dtype)
    # calculating transmission map
    for y in range(size[0]):
        for x in range(size[1]):
            x_low = max(x-(windowSize//2), 0)
            y_low = max(y-(windowSize//2), 0)
            x_high = min(x+(windowSize//2), size[1])
            y_high = min(y+(windowSize//2), size[0])
            sliceimg = img[y_low:y_high, x_low:x_high]
            #using the sliding windows  to calculate the corner vertices
            dark_channel = darkchannel(sliceimg)
            #This is the transmission value. w will be the weight and roh added will be to avoid unnatural haze
            t = 1.0 - (w * img.item(y, x, dark_channel) / light_intensity) + roh
            # Each R,G,B channel needs to be modified
            outputimg.itemset((y,x,0), clamp(0, ((img.item(y,x,0) - light_intensity) / max(t, t0) + light_intensity), 255))
            outputimg.itemset((y,x,1), clamp(0, ((img.item(y,x,1) - light_intensity) / max(t, t0) + light_intensity), 255))
            outputimg.itemset((y,x,2), clamp(0, ((img.item(y,x,2) - light_intensity) / max(t, t0) + light_intensity), 255))
    return outputimg


def main():
    imageName = input()  # eg. fg5.jpg
    img = cv2.imread(imageName)
    cv2.namedWindow("Dehazed image")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    light_intensity = atmospheric_light(img, gray)
    w = 0.95
    t0 = 0.50
    roh = 0.012
    outimg = dehaze(img, light_intensity, 20, t0, w , roh)
    name = imageName+'output'+'.jpg'
    cv2.imwrite(name, outimg)

if __name__ == "__main__": main()
