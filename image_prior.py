'''
I <- Input Image
J <- generateDarkChannel(I)
A <- estimateA
T_est <- 1 - generateDarkChannel(I./A);
L <- generateMattingLaplacian
T <- L \ T_est * 0.0001
outputImage <- (I - A)/T + A
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PIL import Image
from guidedfilter import *

def DarkChannel(input_img, filter, frame):
  """get dark image from the input image"""
  size = input_img.size
  output = []

  for x in xrange(size[1]):
    temp = []
    for y in xrange(size[0]):
      temp.append(min(input_img.getpixel((y, x))))

    output.append(temp)

  output = filter2d(output, filter, frame)
  output_img = Image.new('L', size)

  for x in xrange(size[1]):
    for y in xrange(size[0]):
      output_img.putpixel((y, x), output[x][y])

  return output_img

def AtmosLight(srcImage, darkImage, cut):
  """get atmospheric light from the picture"""
  size = darkImage.size
  light = []

  for x in xrange(size[0]):
    for y in xrange(size[1]):
      light.append(darkImage.getpixel((x, y)))

  light.sort(reverse = True)
  threshold = light[int(cut * len(light))]
  atmosphere = {}

  for x in xrange(size[0]):
    for y in xrange(size[1]):
      if darkImage.getpixel((x, y)) >= threshold:
        atmosphere.update({(x, y): sum(srcImage.getpixel((x, y))) / 3.0})

  pos = sorted(atmosphere.iteritems(), key = lambda item: item[1], reverse = True)[0][0]

  return srcImage.getpixel(pos)

def TransmissionMap(input_img, light, omiga):
  """get transmission from the picture"""
  size = input_img.size
  output = []

  for x in xrange(size[1]):
    temp = []
    for y in xrange(size[0]):
      temp.append(min(input_img.getpixel((y, x))) / float(min(light)))

    output.append(temp)
    mini = 999
    for i in output:
      for num in i:
        if mini>num:
          mini = num
  transmission = []

  for x in xrange(size[1]):
    temp = []
    for y in xrange(size[0]):
      temp.append(1 - omiga * mini )

    transmission.append(temp)

  return transmission

def getRadiance(input_img, transmission, light, t0):
  """get radiance from the picture"""
  size = input_img.size
  output = Image.new('RGB', size)

  for x in xrange(size[1]):
    for y in xrange(size[0]):
      r, g, b = input_img.getpixel((y, x))

      r = int((r - light[0]) / float(max(t0, transmission[x][y])) + light[0])
      g = int((g - light[1]) / float(max(t0, transmission[x][y])) + light[1])
      b = int((b - light[2]) / float(max(t0, transmission[x][y])) + light[2])

      output.putpixel((y, x), (r, g, b))

  return output

def check_range(n):
  if n < 0:
    return 0
  if n > 255:
    return 255

  return int(n)

if __name__ == '__main__':
  image = Image.open('14.jpg')
  image = image.convert('RGB')
  dark = DarkChannel(image, minimizeFilter, (10, 10))

  # dark.save('3_dark.png')

  light = AtmosLight(image, dark, 0.001)

  transmission = TransmissionMap(image, light, 0.96)

  tranImage = Image.new('L', image.size)
  grayImage = image.convert('L')

  for x in xrange(image.size[0]):
    for y in xrange(image.size[1]):
      tranImage.putpixel((x, y), int(transmission[y][x] * 255))
  guided = guidedFilter(grayImage, tranImage, 25, 0.001)
  guidedImage = Image.new('L', image.size)

  for x in xrange(image.size[0]):
    for y in xrange(image.size[1]):
      guidedImage.putpixel((x, y), check_range(guided[y][x]))
      guided[y][x] /= 255.0

  guidedImage.show()
  # guidedImage.save('3_guided.png')

  output = getRadiance(image, guided, light, 0.85)

output.save('tryoutput.jpg')
