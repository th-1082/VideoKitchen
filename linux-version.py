import math, os, subprocess, sys, time
from random import SystemRandom

rng = SystemRandom()

# chunk size is defined in seconds
minChunkSize = 10
maxChunkSize = 20

videoName = ""
videoEndPoint = 0

def clear():
    os.system("tput reset")

# displays the main menu (not used yet)
def displayMenu():
    clear()
    print("Trevor H's Video Kitchen v1.0\n\n")
    print("Select desired cooking method:\n1. Standard boil")
    choice = input("\n>")

    if (isinstance(choice,str)):
        return -1

    if (checkBounds(choice,1,2) == False):
        return False

# checks bounds inclusively
def checkBounds(input,min,max):
    if (input < min or input > max):
        return False;
    return True;

# gets the length of a requested video in seconds
def getVideoLength(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return math.trunc(float(result.stdout))

# this function converts seconds into HH:MM:SS format
def secondsToTime(seconds):
    if (seconds <= 0): # seconds must be positive, not zero or negative
        return -1
    return time.strftime('%H:%M:%S',time.gmtime(seconds))

def createSegmentList():
    currentPosition = 0
    segmentList = []
    while (currentPosition < videoEndPoint): # traverse video for segmentation
        segmentLength = rng.randint(minChunkSize,maxChunkSize)

        # generated segment length exceeds remaining length of video
        if (currentPosition + segmentLength > videoEndPoint):
            segmentLength = videoEndPoint - currentPosition

        segmentList.append(currentPosition + segmentLength)
        currentPosition += segmentLength        

    firstSegment = {
        "start": '00:00:00',
        "stop": secondsToTime(segmentList[0])
    }
    finalSegmentList = [firstSegment]

    # this converts raw seconds in segmentList into a list of dictionaries
    for i in range(0,len(segmentList)):
        if (i < len(segmentList) - 1):
            # use dict to hold formatted times for segmentation 
            currentSegment = {
                "start": secondsToTime(segmentList[i]),
                "stop": secondsToTime(segmentList[i+1])
            }
            finalSegmentList.append(currentSegment)
    return finalSegmentList
        

# BEGIN EXECUTION
# check for proper number of command line arguments
if (len(sys.argv) < 2):
    print("ERROR: Too few arguments! Format: \"python main.py [FILENAME]\"\n")
    exit()

# check that the filename argument is a string
if (isinstance(sys.argv[1],str) == False):
    print("ERROR: Invalid argument type!\n")
    exit()

# check whether provided filename exists within the current directory
if (os.path.isfile(sys.argv[1]) == False):
    print("ERROR: Provided filename is invalid!\n")
    exit()

# store filename and endpoint of the video into respective variables
videoName = sys.argv[1]
videoEndPoint = (getVideoLength(videoName) - 1)

# check if minimum chunk size does not exceed video length
if (minChunkSize >= videoEndPoint):
    print("ERROR: Minimum chunk size exceeds length of video!")
    exit()

mySegments = createSegmentList()

for i in range(0,len(mySegments)):
    begin = mySegments[i].get('start')
    end = mySegments[i].get('stop')
    outputName = "out" + str(i) + ".mp4"
    print("\nSTART: {}\nSTOP: {}\n".format(begin,end))
    os.system('ffmpeg -ss {} -to {} -y -i {} -c copy {}'.format(begin,end,videoName,outputName))
        
segmentOrder = []
# build list containing numbers corresponding to all created segments
for i in range(0,len(mySegments)):
    segmentOrder.append(i)

# shuffle array or segments
rng.shuffle(segmentOrder)

# create list of segments in randomized order for concatenation step
with open('./filelist.txt','w') as concatFile:
    for i in range(0,len(segmentOrder)):
        fileListString = "file \'out" + str(segmentOrder[i]) + ".mp4\'\n"
        concatFile.write(fileListString)

os.system("ffmpeg -f concat -safe 0 -y -i filelist.txt -c copy NEW-{}".format(videoName))

for i in range(0,len(segmentOrder)):
    command = "rm out" + str(i) + ".mp4"
    os.system(command)
