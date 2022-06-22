from stainerpx import Poly, Stainer
from clustering import Clustering
import os


""" INPUT VALIDATION - input ellenőrzés """

# File list & amount
src = "img_"
file_list = os.listdir(src)
file_num = len(file_list)

# Imagefile selection dictionary
selection = { i : file_list[i] for i in range(file_num) }
print(f"Available images:\n {selection}\n")

# Input validation
print(f"Type the index ( between 0 and {file_num-1} ) of an image from the dictionary above you would like to process!")
while 1:
    try:
        index = int(input())
    except ValueError:
        print("Invalid input! Please, type an integer number as index!")
    else:
        if index <= file_num and index >= 0:
            print(f"Selected image: {file_list[index]}")
            path = f"{src}\\{file_list[index]}"
            break
        else:
            print(f"Invalid input! Please, type an integer number between 0 and {file_num-1}!")


""" GREYSCALED ANALYSIS - Szürkeárnyalatos képelemzés """

# Select an image to analyse
t = Poly(path)

points = t.getCoord()
# print(points)

try:
    # Get masked image
    masked = t.mask()
except:
    print("Bye bye ...")
    exit()

# Set scale of colors
colors = 16
s = Stainer(masked,colors)

# print relative frequency of the colors
print("\nRelative frequencies of detected colors ( rgb, % ):\n")
freq = s.stain()
st_data = tuple(zip(s.stColors,freq))[1:] # [0]=background(255,255,255)
print(st_data)


""" CLUSTERING / K-közép klaszterezés """

# Set the numbers of clusters - minimum cluster: 1, which means n < 1 inputs replace with 1!
clusters = 4
cl = Clustering(masked,clusters)

# Print centers to console (RGB)
print(f"\nCluster centers (RGB):\n{cl.centers}")

# Print results to console (%)
print(f"\nRelative appearances (%):\n{cl.percent}")


""" CREATE TEXT FILE """

if os.path.exists("reports") == False:
    os.mkdir("reports")

with open(f'reports\\report_{selection.get(index)}.txt', 'w') as f:
    f.write(f'{selection.get(index)}\n\nRelative frequencies of detected colors (%):\n{st_data}\n')
    f.write(f"\nCluster centers (RGB):\n{cl.centers}\n")
    f.write(f"\nRelative appearances (%):\n{cl.percent}\n")