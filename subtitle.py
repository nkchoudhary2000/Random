# This is only for testing 
import re
import random
import argparse
import datetime as duration
from datetime import datetime
from googletrans import Translator

parser = argparse.ArgumentParser()
parser.add_argument('--file',nargs = "*",type = str, default = ["subtitle_src.srt", "time.time", "subtitle_en.srt"], help = 'Support only two file .srt and .time Default file \"subtitle.srt\", \"time.time\"')
parser.add_argument('--lang',nargs = "*",type = str, default = ["fr", "en"], help = 'use --lang sl dl where sl:source language and dl: destination language default sl:fr and dl:en')
parser.add_argument('--count', default = 2, help = 'use --count to color words of this number')
args = parser.parse_args()

#Global variables
color_counter = 0
translator = Translator()

try:
    args.count = int(args.count)
except Exception as e:
    print("Count Error: " + str(e))
    exit()

#validation
if(len(args.file) > 2):
    print("Please use \"subtitle\" and \"time\" file only")
    exit()

if(len(args.lang) != 2):
    print("Please use valid language")
    exit()

def rwfile(fname, mode, codec='utf8', text = ""):
    try:
        file = open(fname, mode, encoding=codec)
        if mode == 'r':
            text = str(file.read())
        else:
            file.write(text)
    except Exception as e:
        print("Exception: " + str(e))
        if(codec=='latin-1'):
            exit()
        else:
            text = rwfile(fname, mode, 'latin-1', text)

    return text

def filter(text):
    text = re.sub(r'\n',' ', text)
    text = re.sub(r'<.*?>',' ', text)
    text = re.sub(r'\s{1,}',' ', text)
    text = text.strip()
    return text

def color(text):
    global color_counter
    text = filter(text)
    colors = ['ff595e','ffca3a','8ac926','1982c4','6a4c93','ee4266','ffd23f','0ead69','197278','ff5400','db3a34','ffc857','6a994e','a7c957','083d77','f4d35e','247ba0','fb6107','7cb518','80ed99']
    color_counter = (color_counter + 1) if (color_counter < len(colors)-1) else 0
    text = "<font color=\'#" + colors[color_counter] + "\'>" + text + "</font>" 
    return text

def is_subtitle(text):
    return True if re.search(r'\d{1,}\n\d{2}:\d{2}:\d{2}.*', text) else False

def to_timestamp(text):
    timestamps = text.split('\n')
    temp_stamps = []
    ftime = ['%S','%M:%S','%H:%M:%S']

    for each_stamp in timestamps:
        index = int(len(each_stamp) / 3)

        try:
            each_stamp = datetime.strptime(each_stamp, ftime[index])
            each_stamp = str(each_stamp.strftime("%H:%M:%S"))
            temp_stamps.append(each_stamp)
        except Exception as e:
            print("Problem in timestamp!", e)
            exit()
    
    index = 0
    for each_stamp in temp_stamps:
        try:
            timestamps[index] = str(index+1) + "\n" \
                                 + temp_stamps[index] \
                                 + ",000 --> " \
                                 + temp_stamps[index+1] + ",000"
            index += 1
        except:
            time = datetime.strptime(temp_stamps[index],"%H:%M:%S")
            time = time + duration.timedelta(0,7)
            time = time.strftime("%H:%M:%S")
            timestamps[index] = str(index+1) + "\n" \
                                 + temp_stamps[index] \
                                 + ",000 --> " \
                                 + time + ",000"

    return  timestamps

def timestamps(text):
    if is_subtitle(text):
        return re.findall(r'\d{1,}\n\d{2}:\d{2}:\d{2}.*', text)
    else:
        return to_timestamp(text)

def dialogues(text):
    temp_dialogues = []
    if is_subtitle(text):
        dialogues = re.split(r'\d{1,}\n\d{2}:\d{2}:\d{2}.*', text)[1:]
        for dialogue in dialogues:
            dialogue = filter(dialogue)
            temp_dialogues.append(dialogue)
        return temp_dialogues
    else:
        dialogues = text.split('\n')
        return dialogues

def to_translated(text, sl='fr', dl='en'):
    try:
        return translator.translate(text, src = sl, dest = dl).text
    except Exception as e:
        print("Translation Error: " + str(e))
        return "Translation Error: " + str(e)

def to_string(rows):
    text = ""
    try:
        for each_row in rows:
            text += each_row + "\n"
        return text
    except Exception as e:
        print ("String Error: " + str(e))
        return False

def apply_timestamps(timestamps, dialogues):
    text = ""
    for t,d in zip(timestamps,dialogues):
        text += t + "\n" + d + "\n\n"
    return text

def meanings(dialogues,count = args.count):
    temp_dialogues = []
    word_count = []
    for dialogue in dialogues:
        words = dialogue.split(' ')
        # words = words + ['.'] * 3 if len(words) < 2 else words
        icount = count if count < len(words) else len(words)

        index = random.sample(range(0,len(words)), icount)

        for i in range(0, len(index)):
            temp_word = re.sub(r'[\[\!\@\#\$\%\^\&\*\(\)_\+\|\"\:\<\>\?\}\{\~\`\=\\\;\,\.\/\"\]]', '', words[index[i]].lower())
            word_count.append(temp_word)
            words[index[i]] = color(words[index[i]])

        temp_dialogues.append(" ".join(words))

    #New method required here 
    word_stat = dict((word, word_count.count(word)) for word in word_count)
    list_of_words = "\n".join(map(str,[*sorted(word_stat.items(), key = lambda x:x[1], reverse= True)]))
    rwfile("dictionary.txt", 'w','utf8',list_of_words)

    return temp_dialogues

#sfile:source_file and tfile:time_file
def create_subtitle(sfile = args.file[0], tfile = args.file[1]):
    text = rwfile(sfile, 'r')
    time = rwfile(tfile, 'r')
    dialogues_temp = dialogues(text)
    timestamps_temp = timestamps(text) if is_subtitle(text) else timestamps(time)

    if (len(dialogues_temp) > len(timestamps_temp)):
        timestamps_temp = timestamps_temp + ['exceed'] * (len(dialogues_temp) -len(timestamps_temp))

    rwfile("temp_sub.txt", 'w','utf8', "\n".join(dialogues_temp))
    rwfile("temp_time.txt", 'w','utf8', "\n".join(timestamps_temp))
    dialogues_en = to_translated("\n".join(dialogues_temp)).split('\n')
        
    dialogues_en = meanings(dialogues_en)
    dialogues_en = apply_timestamps(timestamps_temp, dialogues_en)
    rwfile("subtitle_en.srt", 'w', 'utf8', dialogues_en)

    dialogues_color = meanings(dialogues_temp)
    dialogues_color = apply_timestamps(timestamps_temp, dialogues_color)
    rwfile("subtitle_color.srt", 'w', 'utf8', dialogues_color)


create_subtitle()




