from __future__ import print_function
import binascii
from PIL import Image, ImageFilter
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
import colorsys
from termcolor import cprint
import os
import glob
import imageio
import math
import colorama
colorama.init()

Image.MAX_IMAGE_PIXELS = None

cprint('*****************************************************************************', 'green')
cprint('***    Dominant Colour and sorting script | https://github.com/jibatsu    ***', 'green')
cprint('*****************************************************************************', 'green')

cprint('This script will calculate the most dominant colour of an image and save it with the hue appended to the beginning of the name of the file.\nIt will do this for every .jpg in a given folder and save them to a new folder.\nYou can choose to save a duplicate of the images with the colours clustered as per Kmeans processing, so you can see its effect, into a new folder of your choice.\nFinally it will calculate the size of the final image and "paste" in the sorted images in order as per their hue.', 'green')

fullpath = input("Enter the absolute path of your folder of images. i.e.'C:\\Users\\<user>\\Pictures\\images': ")
path = fullpath[:-4]
extension = fullpath[-4:]

efolder = input('Name of the folder for processed images to be placed: ')
if not os.path.exists('%s/%s' % (fullpath, efolder)):
    os.makedirs('%s/%s' % (fullpath, efolder))

entries = os.listdir(fullpath)

t_files = len(glob.glob1(fullpath,"*.jpg"))


directory = os.fsencode(fullpath)

num_clusters = input('The number of clusters for KMeans processing. Must be an integer. 1-5 are fast and innacurate, 7-10 are more accurate and recommended, 11+ is most accurate but slower: ')
NUM_CLUSTERS = int(num_clusters)
basewidth = input('Size in pixels for resizing of images for processing. Larger images are more accurate but slower. 50-200 is recommnded: ')     # set image size in pixels

kmeans = input('Would you like to save an additional copy of the kmeans image in a sperate folder? y/n: ')
cprint('Files will be saved with the number of clusters used at the end. e.g. "Autumn Leaves_5.jpg"', 'blue', attrs=['bold'])

if kmeans == 'y':
    nfolder = input('Name of the folder for kmeans processed images to be placed: ')

    if not os.path.exists('%s/%s' % (fullpath, nfolder)):
        os.makedirs('%s/%s' % (fullpath, nfolder))

basewidth = int(basewidth)

oname = input('Enter the name for the final sorted output grid image (excluding the file extension): ')

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".jpg"):
        cprint('%s files remaining' % t_files, 'yellow')
        cprint('Reading image...', 'red')
        cprint(filename,'cyan', attrs=['bold'])

        im = Image.open('%s/%s' % (fullpath, filename)) # The image we would like to process. This is also what is saved at the end to retain the original details
        im2 = Image.open('%s/%s' % (fullpath, filename))# This will become the image that gets resized and blurred for processing. This will be saved in the spereate folder if selected.
        
        wpercent = (basewidth/float(im2.size[0])) # Next 3 lines: resize proportional to original image ratio.
        hsize = int((float(im2.size[1])*float(wpercent)))
        im2 = im2.resize((basewidth,hsize), Image.ANTIALIAS)
        im2 = im2.filter(ImageFilter.GaussianBlur(radius=3)) #Guassian blur
        ar = np.asarray(im2)
        shape = ar.shape
        ar = ar.reshape(np.product(shape[:2]), shape[2]).astype(float)

        cprint('Finding clusters...', 'green')
        codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
        #print('Cluster centres:\n', codes)

        vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
        counts, bins = np.histogram(vecs, len(codes))    # count occurrences

        index_max = np.argmax(counts)                    # find most frequent
        peak = codes[index_max]
        colour = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
        cprint('The most frequent colour is %s (#%s)' % (peak, colour),'cyan')

        # convert rgb values to string
        peakrgb = ' '.join(format(f, '.3f') for f in peak)
        prgb = peakrgb.split(' ')
        r = float(prgb[0])
        g = float(prgb[1])
        b = float(prgb[2])

        # convert rgb string to hsv
        hsv = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        #print(hsv)

        # convert hsv values to string
        peakhsv = ' '.join(format(f, '.3f') for f in hsv)
        phsv = peakhsv.split(' ')
        h = float(phsv[0]) # convert hsv float to degrees
        s = float(phsv[1])
        v = float(phsv[2])

        h = (h*360) 
        if h != 360:
            h += 0.01 #+0.01 ensures there are no 0.0 floats
        h = round(h,2)

        print('H=%3f S=%3f V=%3f' % (h,s,v))

        # bonus: save image using only the N most common colours
        if kmeans == 'n':
            newpath = '%s/%s/%s %s' % (fullpath,efolder,h,filename)
            c = im.copy()
            imageio.imwrite(('%s' % newpath), c)

            cprint('Saved clustered image as - %s' % newpath, 'magenta', attrs=['bold'])
        elif kmeans == 'y':
            newpath = '%s/%s/%s_%s_%d.jpg' % (fullpath,nfolder,h,filename[:-4],NUM_CLUSTERS)
            b = ar.copy()
            for i, code in enumerate(codes):
                b[scipy.r_[np.where(vecs==i)],:] = code
            imageio.imwrite(('%s' % newpath), b.reshape(*shape).astype(np.uint8))

            cprint('Saved clustered image as - %s' % newpath, 'magenta', 'on_white', attrs=['bold'])

            newpath = '%s/%s/%s %s' % (fullpath,efolder,h,filename)
            c = im.copy()
            imageio.imwrite(('%s' % newpath), c)

            cprint('Saved clustered image as - %s' % newpath, 'magenta', attrs=['bold'])

        t_files -= 1

# Pre Config: This will count the number of 'real' pictures and calculate the size of the sqaure
images_dir = ('%s\%s' % (fullpath, efolder))
images_list = sorted(os.listdir(images_dir))
images_count = len(images_list)
#print('Images: ', images_list)
print('Images count: ', images_count)

# Calculate the grid size:
grid_size = math.ceil(math.sqrt(images_count))

cprint('Grid size: %s' % grid_size,'cyan', attrs=['bold'])

mod = grid_size**2 % images_count

cprint('mod: %s' % mod,'red', attrs=['bold'])

blank = Image.new('RGB', (100, 100))

# Create blank spaces to fill out the modulus 
blanks = []
n = 0
for m in range(mod):
    blank.save('%s/%s\\999 blank%s.jpg' % (fullpath, efolder, n))
    blanks.append('999 blank%s' % n)
    n += 1

# true Config: This counts the number of 'real' files + blanks and calculates the square again. 
# This should be the same size as the first calculated square.
images_dir = ('%s\%s' % (fullpath, efolder))
images_list = sorted(os.listdir(images_dir))
images_count = len(images_list)
#print('Images: ', images_list)
print('Images count: ', images_count)

# Calculate the grid size:
grid_size = math.ceil(math.sqrt(images_count))

cprint('Grid size: %s' % grid_size,'cyan', attrs=['bold'])

mod = grid_size**2 % images_count

cprint('mod: %s' % mod,'red', attrs=['bold'])

# get arguments
sorted_list = sorted(images_list, key=lambda s: float(s.split(" ")[0].replace('.jpg','')))
#print(sorted_list)

rows = grid_size
cols = grid_size

# get filenames
filenames = [images_dir +'/' + x for x in sorted_list]
cprint('    rows=%s' % rows, 'cyan', attrs=['bold'])
cprint('    cols=%s' % cols, 'cyan', attrs=['bold'])

with open('%s/%s\log.txt' % (fullpath, efolder), 'w', encoding="utf-8") as output_file:
    for entry in sorted_list:
        output_file.write(entry + '\n')

cprint('Loading images...', 'magenta')
# load images and resize to (100, 100)
images = [Image.open(name).resize((100, 100)) for name in filenames]

cprint('Creating canvas...', 'green')
# create empty 'canvas' to put thumbnails
new_image = Image.new('RGB', (cols*100, rows*100))

cprint('Pasting images onto canvas...', 'yellow', attrs=['bold'])
# put thumbnails on the 'canvas'
i = 0
for y in range(rows):
    if i >= (len(images)):
        break
    y *= 100
    for x in range(cols):
        x *= 100
        img = images[i]
        new_image.paste(img, (x, y, x+100, y+100))
        i += 1


# crop it
xarea = cols*100
rarea = ((rows*100)-100)
area = (0,0,xarea,rarea)
new_image = new_image.crop(area)

# save it
new_image.save('%s/%s\%s.jpg' % (fullpath, efolder, oname))
cprint('Sorted grid saved as %s\%s\%s.jpg' % (fullpath, efolder, oname), 'yellow', attrs=['bold'])

# delete blanks
import re
directory = images_dir
pattern = "999 blank"
files_in_directory = os.listdir(directory)
filtered_files = [file for file in files_in_directory if ( re.search(pattern,file))]
for file in filtered_files:
    path_to_file = os.path.join(directory, file)
    os.remove(path_to_file)

