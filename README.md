# dominant_colour
 Python script for finding dominant colour of an image.

 This script will calculate the most dominant colour of an image and save it with the hue appended to the beginning of the name of the file. 
 It will do this for every .jpg in a given folder and save them to a new folder. 
 You can choose to save a duplicate of the images with the colours clustered as per Kmeans processing, so you can see its effect, into a new folder of your choice.
 Finally it will calculate the size of the final image and "paste" in the sorted images in order as per their hue.
 
 **Input:**
 
 ![test folder](https://user-images.githubusercontent.com/7764932/158205936-a18fff59-e66a-4301-9cff-9fb2f7a0649d.png)
 
 
 **Output:**
 
 ![#file](https://user-images.githubusercontent.com/7764932/158213273-fb059f3e-9829-4824-85f0-7c9443a6aa1a.jpg)

 
 ## Info
 
 Images are loaded by Python, resized to a smaller size to speed up calculations, a guassian blur is applied to smooth out detailed images, finally KMeans clustering is applied to find the most dominant colours.
 
 The number of clusters you define will be the number of dominant colours the script will look for.

 ![CNrX2wM - Imgur](https://user-images.githubusercontent.com/7764932/158214052-048a4626-8c5f-45ac-b738-9f7df3aafa04.jpg)

The image above shows how the number of clusters changes the colours the script will find. Starting from the top left NUM_CLUSTERS was set to 15 and decreasing to 5 in steps of 2. Each pass a guassian blur was, and was not, applied.

## Step 1

Firstly you need to organise your images into one folder. This can either be done manually or using a script. I have used the Powershell script as that is what I knew at the time. This can easily be done in any other language you are comfortable with.

To run the powershell script open powershell ISE (installed by default in Windows 10) as an administrator. You will need to enable running scripts on your computer by entering the folowing into the blue terminal.

```
set-executionpolicy remotesigned
```

![powershell](https://user-images.githubusercontent.com/7764932/158216919-5be43d5e-6b9e-455c-8747-5aadc71c5cee.png)

Open the .ps1 file and change the paths for 'Source' and 'Destination'. Click the green 'Run' arrow on the ribbon, or hit 'F5'.

![powershell2](https://user-images.githubusercontent.com/7764932/158216948-8555d768-4d3f-417c-a1d8-be459c798fd8.png)

Below you will see my folder full of images. This is what we are going to try and sort by colour:

![test folder](https://user-images.githubusercontent.com/7764932/158205936-a18fff59-e66a-4301-9cff-9fb2f7a0649d.png)

**Note: All images must have a bit depth of 24. The script fails with 8 and 32 bit images.**

## Step 2

Next you will need to install Python3.7 if you haven't already. You can find it here: https://www.python.org/downloads/release/python-370/ (Scroll to the bottom)

Once installed you will need to install some extra packages to make the script work. There is a requirements.txt located in the Python folder of this project.

```
cd C:'path to folder containing requirments.txt'
```
Then:
```
pip install -r requirements.txt
```

## Step 3

Now find the *dom_colour_input.py* file and double click to run it. A python terminal window should open with a basic description and the first prompt for input from ther user.
![terminal](https://user-images.githubusercontent.com/7764932/158215205-7f801cc2-ec17-4ecc-aa3e-4c0939525813.png)

Type or paste in the path to your images folder (make sure you are using the absolute path) and press enter.

You'll be met with a few more prompts for new folders and filenames. These can just be the new name of the folder, e.g. 'output' and not the absolute path to the new folder.

## Step 4

Once the script has finished you can look in your new 'output' folder and you should see all of your images with their hue (in degrees) appended to the beginning of the filenames. There is also a log.txt file of their names (This is a holdover from testing. Usefull for searching for files if you have quite a few!).

![processed](https://user-images.githubusercontent.com/7764932/158213175-efde5d98-bd46-4412-9942-4b62c877a786.png)

Crucially the final output grid image should also be in this folder. I made sure to name mine with as # at the beginning to make sure it is sorted at the top in windows.

![#file](https://user-images.githubusercontent.com/7764932/158213273-fb059f3e-9829-4824-85f0-7c9443a6aa1a.jpg)

## Step 5

If you chose the option to save the pictures as their clustered images, they will be saved in the folder name of your choice in the root folder of your 'images to be sorted' folder.

![kmeans](https://user-images.githubusercontent.com/7764932/158213550-fb047337-e56d-4ad0-b763-6f043f5a729e.png)

## Thanks & Extra reading

Thank you for your interest in this project. This is something I had at the back of my mind for some time and has been great to see a result!

If anybody has any ideas on improving the script for a smoother final result please do have a go and let me know if you have any success!

Here are some links for some extra reading regarding colour sorting:

https://www.alanzucconi.com/2015/09/30/colour-sorting/

https://en.wikipedia.org/wiki/Color_difference

https://analyticsindiamag.com/guide-to-image-color-analyzer-in-python/

A handy tool for visualising HSV colourspace: http://color.lukas-stratmann.com/color-systems/hsv.html

