#!/usr/bin/python3

from os import listdir
from re import findall
from statistics import stdev, mean
from collections import defaultdict
# from urllib import request
# from urllib.parse import urlparse

with open("data/keywords") as f:
	keywords = [line.strip().lower() for line in f.readlines()[1:]]

with open("data/spammers") as f:
	spammers = dict([line.strip().lower().split() for line in f.readlines()[1:]])

with open("additional_keywords") as f:
	additional_keywords = [line.strip().lower() for line in f.readlines()[1:]]

# Remove duplicates
for word in keywords:
	if word in additional_keywords:
		additional_keywords.remove(word)

nr_emails = len(listdir("data/emails"))

# Stores the frequency of each keyword in each email
freq = defaultdict(lambda : [0] * nr_emails)

length, caps, spammer_score = [0] * nr_emails, [0] * nr_emails, [0] * nr_emails
# url_score = [0] * nr_emails

for i in range(nr_emails):
	with open("data/emails/" + str(i)) as f:
		date = f.readline().strip()
		subject = f.readline().strip()
		sender = f.readline().strip()
		sender_address = findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", sender)[0].lower()
		if sender_address in spammers:
			spammer_score[i] = int(spammers[sender_address])

		# Skipping charachters which are not part of body ("\nBody: ")
		f.read(7)

		for line in f.readlines():
			for keyword in keywords:
				freq[keyword][i] += line.lower().count(keyword)
			for keyword in additional_keywords:
				freq[keyword][i] += line.lower().count(keyword)
			caps[i] += sum(c.isupper() for c in line)
			length[i] += sum(len(word) for word in line.split())
			# Attempted to use a URL score but this takes way too long even with
			# the lowest timeout and I get TLE
			# for link in findall("http://(?:[\w]+\.)(?:\.?[\w]{2,})+", line):
			# 	try:
			# 		response = request.urlopen(link, timeout=1)
			# 		domain = '.'.join(urlparse(link).netloc.split('.')[-2:])
			# 		new_domain = '.'.join(urlparse(response.geturl()).netloc.split('.')[-2:])
			# 		if domain != new_domain:
			# 			url_score[i] += 1
			# 		if urlparse(response.geturl()).scheme != "https":
			# 			url_score[i] += 1
			# 	except:
			# 		url_score[i] += 1
			# 		continue

with open("statistics.out", "w") as f:
	for keyword in keywords:
		v = [freq[keyword][i] for i in range(nr_emails)]
		f.write("{:s} {:d} {:.6f}\n".format(keyword, sum(v), stdev(v)))

avg_length = mean(length)

keywords += additional_keywords

with open("prediction.out", "w") as f:
	for i in range(nr_emails):
		keywords_score = sum(freq[keyword][i] for keyword in keywords) * avg_length / length[i]
		caps_score = caps[i] > 0.5 * length[i]
		score = 10 * keywords_score + 30 * caps_score + spammer_score[i] # + 15 * url_score[i]
		f.write("1\n" if score > 35 else "0\n")