import csv
import os

data=[]
with open('trials.csv', 'w', newline='') as writeFile:
    writer = csv.writer(writeFile)
    writer.writerow(['file', 'syllable', 'phoneme', 'visime'])
    for filename in os.listdir("."):
        if ".mp4" in filename:
            data.append(filename)
            syllable = filename.split('.')[0]
            data.append(syllable)
            data.append(syllable.split('_')[0])
            data.append(syllable.split('_')[1])
            writer.writerow(data)
            data=[]
writeFile.close()

