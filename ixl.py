#!/usr/bin/python

import httplib2
from BeautifulSoup import BeautifulSoup
import urllib
import sys
import smtplib

EMAIL_FROM = "meshko@scorch2000.com"
EMAIL_REPLY_TO = "meshko@gmail.com"
EMAILS_TO = ["meshko@gmail.com", "boriskruk@gmail.com"]

def send_email(addr_from, addr_from_reply, addrs_to, subject, msg):
	server = smtplib.SMTP('localhost')
	server.sendmail(addr_from, addrs_to, 
		"From: %s\r\nTo: %s\r\nReply-to: %s\r\nSubject: %s\r\n\r\n%s" % (addr_from, ", ".join(addrs_to), addr_from_reply, subject, msg))
	server.quit()

class IXLTopic:
	"""topic"""
	def __init__(self, element):		
		self.name = element.find("a", attrs={"class":"skillLink"}).text
		self.url = element.find("a", attrs={"class":"skillLink"})['href']
		scoreElt = element.find("span", attrs={"class":"stdsScoreMedal"})
		if scoreElt: 
			self.score = int(scoreElt.text.strip('()'))
		else:
			self.score = 0

	def __str__(self):
		return " ".join([self.name, str(self.score), "www.ixl.com" + self.url])

def produce_report(name, userid, familyid, grade):
	http = httplib2.Http()
	#page = conn.request(u"http://www.ixl.com/","GET")

	#url = 'https://www.ixl.com/signin'   
	#body = {'username': 'boriskruk', 'password': 'mashakruk'}
	headers = {'Content-type': 'application/x-www-form-urlencoded'}
	#response, content = http.request(url, 'POST', headers=headers, body=urllib.urlencode(body))

	#print content
	url = 'https://www.ixl.com/signin/subaccount'
	body = {'userId': userid, 'familyUserId': familyid}
	response, content = http.request(url, 'POST', headers=headers, body=urllib.urlencode(body))

	headers = {'Cookie': response['set-cookie']}

	url = 'http://www.ixl.com/math/%s' % grade   
	response, content = http.request(url, 'GET', headers=headers)

	#print content
	#sys.exit(0)

	soup = BeautifulSoup(content)
	#topics = soup.findAll('li')
	allTopics = soup.findAll('li', attrs={"class":"hasIcon"})
	allTopics = map(lambda el: IXLTopic(el), allTopics)

	notStartedTopics = filter(lambda t: t.score == 0, allTopics)
	totalTopics = len(allTopics)
	startedTopics = filter(lambda t: t.score in range(1,100), allTopics)
	completedTopics = filter(lambda t: t.score == 100, allTopics)
	completedTopicsNum = len(completedTopics)

	report = "%s's IXL Report\n\nTotal: %d\nCompleted: %d (%.2f%%)\nNot started: %d\nStarted but incomplete: %d" %\
	(name, totalTopics, completedTopicsNum, (completedTopicsNum/(totalTopics/100.0)), len(notStartedTopics), len(startedTopics))

	report += "\n\nStarted:\n\n"
	startedTopics = sorted(startedTopics, key=lambda topic: topic.score, reverse=True)
	for topic in startedTopics:
		report += str(topic)
		report += "\n"

	report += "\n\nNot Started:\n\n"
	for topic in notStartedTopics:
		report += str(topic)
		report += "\n"

	#print report
	send_email(EMAIL_FROM, EMAIL_REPLY_TO, EMAILS_TO, "%s's IXL report" % name, report)

produce_report(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])


