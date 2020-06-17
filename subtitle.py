import re
import random
import argparse
import requests
from datetime import datetime
from googletrans import Translator

parser = argparse.ArgumentParser()
parser.add_argument('--sub_file', help='Name of the sub file')
parser.add_argument('--time_file', help='timestamps of the sub file')
parser.add_argument('--sub_type',default=False, help='true|false')

args = parser.parse_args()

sub_file = args.sub_file
time_file = args.time_file
sub_type = args.sub_type

translator = Translator()
#if subtitle already made
def rtn_lst_timestamp(text):

	timestamp = re.findall(r'\d{1,}\n\d{2}:\d{2}:\d{2}.*', text)
	return timestamp
#if subtitle already made
def rtn_lst_dialogue(text):
	temp_list = []
	dialogues = re.split(r'\d{1,}\n\d{2}:\d{2}:\d{2}.*', text)[1:]
	for dialogue in dialogues:
		text = re.sub(r'\n',' ', dialogue)
		text = re.sub(r'<.*?>',' ', text)
		text = re.sub(r'\s{1,}',' ', text)
		text = text.strip()

		temp_list.append(text)

	dialogues = temp_list
	return dialogues

#if subtitle is not yet made
def rtn_lst_undialogue(text):
	dialogues = text.split('\n')
	return dialogues

#create timestamp from "time.tmp" file format "hh:mm:ss"
def rtn_cnvt_lst_timestamp(text):
	sub = ""
	temp_timestamps = []
	timestamps = text.split('\n')
	for timestamp in timestamps:
		try:
			time = datetime.strptime(timestamp,"%M:%S")
		except:
			time = datetime.strptime(timestamp,"%H:%M:%S")

		time = str(time.strftime("%H:%M:%S"))

		#timestamps.insert(timestamps.index(timestamp),time)
		temp_timestamps.append(time)

	timestamps = temp_timestamps
	for i in range(len(timestamps) - 1):
		sub += str(i) + "\n" + str(timestamps[i]) + ",000 --> " + str(timestamps[i+1]) + ",000\n"
	#outside of for block to add for last item in list
	sub += str(len(timestamps)) + "\n" + str(timestamps[-1]) + ",000 --> 01:00:00,000\n"

	timestamps = rtn_lst_timestamp(sub)
	return timestamps

#return translate text
def rtn_translate(text):
	try:
		# url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=fr&tl=en&dt=t&q=" + text
		# r = requests.get(url)
		# return str(r.json()[0][0][0])

		return translator.translate(text, src = 'fr', dest = 'en').text
	except Exception as e:
		return e


def create_subtitle(text, time, subtitle):
	meaning = ""
	subtitle_en = ""
	subtitle_color = ""

	meaning_word = []
	en_trans = ""

	if subtitle:
		#for Original Subtitle
		dialogue_list = rtn_lst_dialogue(text)
		timestamps = rtn_lst_timestamp(text)  #already made subtitle have timestamp
	else:
		dialogue_list = rtn_lst_undialogue(text)
		timestamps = rtn_cnvt_lst_timestamp(time)

	for each_dialogue in dialogue_list:
		en_trans += each_dialogue + "\n"

	en_trans = rtn_translate(en_trans).split('\n')

	for timestamp, each_dialogue, english in zip(timestamps, dialogue_list, en_trans):
		
		words = each_dialogue.split(' ')
		#small error handling temp code
		if len(words) < 2:
			words.append(".")
			words.append(".")
			
		count_word = len(words)
		index = random.sample(range(0,count_word),2)

		meaning_word.append(words[index[0]])
		meaning_word.append(words[index[1]])

		words[index[0]] = "<font color=\"#0080ff\">" + words[index[0]] + "</font>"
		words[index[1]] = "<font color=\"#ff0000\">" + words[index[1]] + "</font>"

		word = ""
		for w in words:
			word += w + " "

		subtitle_color += timestamp + "\n" + word + "\n\n"
		subtitle_en += timestamp + "\n" + english + "\n\n"

	#convert word list into string
	str_word = ""
	for word in meaning_word:
		str_word += word + "\n"
	en_meaning_word = rtn_translate(str_word).split('\n')

	for i in range(0,len(meaning_word),2):
		meaning += "" \
				"<font color=\"#0080ff\">" + meaning_word[i] + "</font>	•	" \
				"<font color=\"#ff0000\">" + en_meaning_word[i] + "</font><br/>" \
				"<font color=\"#0080ff\">" + meaning_word[i+1] + "</font>	•	" \
				"<font color=\"#ff0000\">" + en_meaning_word[i+1] + "</font>"\
				+ "\n"
	meanings = meaning.split('\n')
	meaning = ""

	for t, w in zip(timestamps, meanings):
		meaning += t + "\n" + w + "\n\n"


	file_meaning = open('meaning.srt', 'w', encoding='utf8')
	file_en_sub = open('subtitle_en.srt', 'w', encoding = 'utf8')
	file_color_sub = open('subtitle_color.srt', 'w', encoding = 'utf8')

	file_meaning.write(meaning)
	file_en_sub.write(subtitle_en)
	file_color_sub.write(subtitle_color)

text = str(open(sub_file, 'r', encoding='utf8').read())
time = str(open(time_file, 'r', encoding='utf8').read())

create_subtitle(text, time, sub_type)
