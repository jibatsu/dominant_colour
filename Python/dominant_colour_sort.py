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
#from operator import itemgetter
import operator

fullpath = input("Enter the absolute path of your folder of images. i.e.'C:\\Users\\<user>\\Pictures\\images': ")
#path = fullpath[:-4]
#extension = fullpath[-4:]

efolder = "Sorted" #input('Name of the temporary folder for processed images to be placed: ')
if not os.path.exists('%s/%s' % (fullpath, efolder)):
    os.makedirs('%s/%s' % (fullpath, efolder))

#entries = os.listdir(fullpath)

t_files = len(glob.glob1(fullpath,"*.jpg"))
a_files = len(glob.glob1(fullpath,"*.jpg"))

proc_list = []
proc_list_rgb = []

directory = os.fsencode(fullpath)

num_clusters = input('The number of clusters for KMeans processing. Must be an integer. 1-5 are fast and innacurate, 7-10 are more accurate and recommended, 11+ is most accurate but slower: ')
NUM_CLUSTERS = int(num_clusters)
basewidth = input('Size in pixels for resizing of images for processing. Larger images are more accurate but slower. 50-200 is recommnded: ')     # set image size in pixels

bands = int(input('How many colour bands would you like in the output image? 8 is recommended:'))

cprint('Additional copies of the files can be saved with the number of clusters used at the end. e.g. "Autumn Leaves_5.jpg"', 'blue', attrs=['bold'])
kmeans = input('Would you like to save an additional copy of the kmeans image in a sperate folder? y/n: ')

if kmeans == 'y':
    nfolder = input('Name of the folder for kmeans processed images to be placed: ')

    if not os.path.exists('%s/%s' % (fullpath, nfolder)):
        os.makedirs('%s/%s' % (fullpath, nfolder))

basewidth = int(basewidth)

sort_type = input('How would you like to sort your images? By (H)ue, (L)uminosity or (O)ld hue: ')

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
        hsv = colorsys.rgb_to_hls(r/255, g/255, b/255)

        # convert hsv values to string
        peakhsv = ' '.join(format(f, '.3f') for f in hsv)
        phsv = peakhsv.split(' ')
        h = float(phsv[0]) # convert hsv float to degrees
        l = float(phsv[1])
        s = float(phsv[2])

        h = (h*360) 
        if h != 360:
            h += 0.01 #+0.01 ensures there are no 0.0 floats
        h = round(h,2)

        print('H=%3f S=%3f V=%3f' % (h,l,s))

        file_id = a_files - t_files
        processed = file_id, h, l, s, filename
        proc_rgb = file_id, r, g, b, filename
        proc_list_rgb.append(proc_rgb)
        proc_list.append(processed)
        proc_str = ' '.join(map(str,processed))

        with open('%s/tuple_log.txt' % (fullpath), 'a+', encoding="utf-8") as output_file:
                output_file.write(proc_str)
                output_file.write('\n')

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
images_count = len(proc_list_rgb)
print('Images count: ', images_count)

#Sort types | Hue, Luminosity & Old Hue
if sort_type == 'h':
    def step (r,g,b,repetitions):
        lum = math.sqrt( .299 * r + .587 * g + .114 * b )

        h, s, v = colorsys.rgb_to_hsv(r,g,b)

        h2 = int(h * repetitions)
        lum2 = int(lum * repetitions)
        v2 = int(v * repetitions)

        if h2 % 2 == 1:
            v2 = repetitions - v2
            lum = repetitions - lum

        return (h2, lum, v2)

    proc_list_rgb.sort(key=lambda r_g_b: step(r_g_b[1],r_g_b[2],r_g_b[3],bands) )

if sort_type == 'l':
    def lum (r,g,b):
        return math.sqrt( .299 * r + .587 * g + .114 * b )
    proc_list_rgb.sort(key=lambda rgb: lum(rgb[1],rgb[2],rgb[3]))

sorted_list_rgb = proc_list_rgb

if sort_type == 'o':
    images_count = len(proc_list)
    sorted_list = sorted(proc_list, key = operator.itemgetter(1))
    #sorted_list.sort(key = operator.itemgetter(2), reverse=True)

    sorted_list_rgb = sorted_list

# Calculate the grid size:
grid_size = math.ceil(math.sqrt(images_count))

mod = grid_size**2 % images_count

cprint('mod: %s' % mod,'red', attrs=['bold'])

blank = Image.new('RGB', (100, 100))

# Create blank spaces to fill out the modulus 
blanks = []
n = 0
for m in range(mod):
    blank.save('%s/blankx %s.jpg' % (fullpath, n))
    n_string = str(n)
    blanks = 'blankx ' + n_string + '.jpg'
    blank_tup = '999','999','999','999',blanks
    sorted_list_rgb.append(blank_tup)
    n += 1

# true Config: This counts the number of 'real' files + blanks and calculates the square again. 
images_count = len(proc_list) + mod

# Calculate the grid size:
grid_size = math.ceil(math.sqrt(images_count))

mod = grid_size**2 % images_count

rows = grid_size
cols = grid_size

# get filenames
sorted_filenames = []

for f in sorted_list_rgb:
    sorted_filenames.append(f[4])

cprint('    rows=%s' % rows, 'cyan', attrs=['bold'])
cprint('    cols=%s' % cols, 'cyan', attrs=['bold'])

with open('%s/%s/log.txt' % (fullpath, efolder), 'w', encoding="utf-8") as output_file:
    for entry in sorted_filenames:
        output_file.write(entry + '\n')

# load images and resize to (100, 100)
cprint('Loading images...', 'magenta')
filenames = [fullpath + '/' + x for x in sorted_filenames]
images = [Image.open(name).resize((100, 100)) for name in filenames]

# create empty 'canvas' to put thumbnails
cprint('Creating canvas...', 'green')
new_image = Image.new('RGB', (cols*100, rows*100))

# put thumbnails on the 'canvas'
cprint('Pasting images onto canvas...', 'yellow', attrs=['bold'])
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
yarea = rows*100
area = (0,0,xarea,yarea)
new_image = new_image.crop(area)

# save it
new_image.save('%s/%s.png' % (fullpath, oname))
cprint('Sorted grid saved as %s/%s.png' % (fullpath, oname), 'yellow', attrs=['bold'])

import re 

directory = fullpath
pattern = "blankx"
files_in_directory = os.listdir(fullpath)
filtered_files = [file for file in files_in_directory if ( re.search(pattern,file))]
for file in filtered_files:
    path_to_file = os.path.join(directory, file)
    os.remove(path_to_file)


delete = input('Would you like to delete the temporary folder? y/n: ')

import shutil

if delete == 'y':
    try:
        shutil.rmtree(images_dir)
    except OSError as e:
        print(e)
    else:
        cprint('%s has been deleted successfully' % images_dir, 'red', attrs=['bold'])