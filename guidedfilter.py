
from PIL import Image

def filter2d(input_img, filter, frame):
  """filter of the 2-dimension picture"""
  size = len(input_img), len(input_img[0])
  output = []

  for i in xrange(size[0]):
    temp = []
    for j in xrange(size[1]):
      temp.append(filter(input_img, (i, j), frame))

    output.append(temp)

  return output

def minimizeFilter(input_img, point, size):
  """minimize filter for the input image"""
  begin = (point[0] - size[0] / 2, point[0] + size[0] / 2 + 1)
  end = (point[1] - size[1] / 2, point[1] + size[1] / 2 + 1)

  l = []

  for i in xrange(*begin):
    for j in xrange(*end):
      if (i >= 0 and i < len(input_img)) and (j >= 0 and j < len(input_img[0])):
        l.append(input_img[i][j])

  return min(l)

def guidedFilter(srcImage, guidedImage, radius, epsilon):
  """guided filter for the image src image must be gray image guided image must be gray image """

  size = srcImage.size
  src = convertImageToMatrix(srcImage)
  guided = convertImageToMatrix(guidedImage)

  one = []
  two=[]

  for x in xrange(size[1]):
    one.append([1.0] * size[0])


  n = boxFilter(one, radius)
  plus = lambda x, y: x + y
  minus = lambda x, y: x - y
  multiple = lambda x, y: x * y
  divide = lambda x, y: x / y

  meanI = dot(boxFilter(src, radius), n, divide)
  meanP = dot(boxFilter(guided, radius), n, divide)
  meanIP = dot(boxFilter(dot(src, guided, multiple), radius), n, divide)

  covIP = dot(meanIP, dot(meanI, meanP, multiple), minus)

  meanII = dot(boxFilter(dot(src, src, multiple), radius), n, divide)
  varI = dot(meanII, dot(meanI, meanI, multiple), minus)

  epsilonMatrix = []

  for x in xrange(size[1]):
    epsilonMatrix.append([epsilon] * size[0])

  a = dot(covIP, dot(varI, epsilonMatrix, plus), divide)
  b = dot(meanP, dot(a, meanI, multiple), minus)

  meanA = dot(boxFilter(a, radius), n, divide)
  meanB = dot(boxFilter(b, radius), n, divide)

  return dot(dot(meanA, src, multiple), meanB, plus)