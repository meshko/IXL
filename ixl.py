#!/usr/bin/python

import httplib2
from BeautifulSoup import BeautifulSoup
import urllib
import sys
import smtplib

EMAIL_FROM = "meshko@scorch2000.com"
EMAIL_REPLY_TO = "meshko@gmail.com"
EMAILS_TO = ["meshko@gmail.com", "boriskruk@gmail.com"]
#EMAILS_TO = ["meshko@gmail.com"]

def send_email(addr_from, addr_from_reply, addrs_to, subject, msg):
	server = smtplib.SMTP('localhost')
	server.sendmail(addr_from, addrs_to, 
		"From: %s\r\nTo: %s\r\nReply-to: %s\r\nSubject: %s\r\n\r\n%s" % (addr_from, ", ".join(addrs_to), addr_from_reply, subject, msg))
	server.quit()

class IXLTopic:
	"""topic"""
	def __init__(self, element):		
		#print element
		self.done = False		
		self.name = element.find("a", attrs={"class":"skill-tree-skill-link"}).findAll("span")[1].text
		self.url = element.find("a", attrs={"class":"skill-tree-skill-link"})['href']
		scoreElt = element.find("span", attrs={"class":"skill-tree-skill-score"})
		if scoreElt: 
			#print "SCORE ELT: " + socreElt
			self.score = int(scoreElt.text.strip('()'))
			imgElt = scoreElt.find("img")
			if imgElt and imgElt['alt'] == "Medal":
				self.done = True
		else:
			#for e in element.findAll("span"):
			#	print e
			self.score = 0		

	def __str__(self):
		return " ".join([self.name, str(self.score), "www.ixl.com" + self.url])

def produce_report(name, userid, familyid, area, grade):
	http = httplib2.Http()
	#page = conn.request(u"http://www.ixl.com/","GET")

	#url = 'https://www.ixl.com/signin'   	
	#headers = {'Content-type': 'application/x-www-form-urlencoded'}
	#response, content = http.request(url, 'POST', headers=headers) #, body=urllib.urlencode(body))
	#print response
	#sys.exit(0)

	url = 'https://www.ixl.com/signin/subaccount'
	body = {'userId': userid, 'familyUserId': familyid}
	headers = {'Content-type': 'application/x-www-form-urlencoded'}
	headers['User-Agent'] = 'curl/7.24.0 (x86_64-apple-darwin12.0) libcurl/7.24.0 OpenSSL/0.9.8x zlib/1.2.5]'
	response, content = http.request(url, 'POST', headers=headers, body=urllib.urlencode(body))
	#print response
	#print content

	headers = {'Cookie': response['set-cookie']}
	url = 'http://www.ixl.com/%s/%s' % (area, grade)
	response, content = http.request(url, 'GET', headers=headers)

	soup = BeautifulSoup(content)
	#topics = soup.findAll('li')
	#print content
	allTopics = soup.findAll('li', attrs={"class":"skill-tree-skill-node skill-tree-skill-has-icon"})
	#allTopics = soup.findAll('li', attrs={"class":"skill-tree-skill-node"})
	#print "found" , len(allTopics), "topics"
	allTopics = map(lambda el: IXLTopic(el), allTopics)

	notStartedTopics = filter(lambda t: t.score == 0 and not t.done, allTopics)
	totalTopics = len(allTopics)
	startedTopics = filter(lambda t: t.score in range(1,100) and not t.done, allTopics)
	completedTopics = filter(lambda t: t.done, allTopics)
	completedTopicsNum = len(completedTopics)

	print "total: %d, not started: %d, started: %d, completed: %d\n" % (totalTopics, len(notStartedTopics), len(startedTopics), completedTopicsNum)

	report = "%s's IXL Report on %s\n\nTotal: %d\nCompleted: %d (%.1f%%)\nNot started: %d\nStarted but incomplete: %d" %\
	(name, area, totalTopics, completedTopicsNum, (completedTopicsNum/(totalTopics/100.0)), len(notStartedTopics), len(startedTopics))

	if len(startedTopics) > 0:
		report += "\n\nStarted:\n\n"
		startedTopics = sorted(startedTopics, key=lambda topic: topic.score, reverse=True)
		for topic in startedTopics:
			report += str(topic)
			report += "\n"

	if len(notStartedTopics) > 0:
		report += "\n\nNot Started:\n\n"
		for topic in notStartedTopics:
			report += str(topic)
			report += "\n"

	#print report
	send_email(EMAIL_FROM, EMAIL_REPLY_TO, EMAILS_TO, "%s's IXL report on %s" % (name, area), report)

produce_report(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])


