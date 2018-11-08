import os
from bs4 import BeautifulSoup
from requests import get
import re
import datetime


def geturl(abbv, yr):
	return 'https://www.pro-football-reference.com/teams/' + abbv + '/' + str(yr) + '/gamelog/';
def getabbv(url):
	m = re.search('.*\/teams\/(.+?)\/\d\d\d\d', url)
	if m:
		return m.group(1)
def crawlurl(opponents, yr):
	#print(opponents)

	for opponent in opponents:
		if opponents[opponent] == None:
			continue
		print(geturl(opponents[opponent], yr))
		response = get(geturl(opponents[opponent], yr))
		html_soup = BeautifulSoup(response.text, 'html.parser')

		for opponent in html_soup.find_all('td',{'data-stat':'opp'}):
			if not opponent.get_text() in mopps:
				abbv = getabbv(opponent.find('a')['href'])
				mopps[opponent.get_text()] = abbv
				new[opponent.get_text()] = abbv

mopps={'base':'nwe'}

yr=1966
while yr<=datetime.datetime.now().year:
	i=1
	print(str(yr) + ' starting with ' + str(len(mopps)) + ' teams')
	new=mopps.copy()
	while len(new) > 0 or i==1:
		current = new.copy()
		new.clear()
		crawlurl(current, yr)
		print('\t' + str(yr) + ' - round ' + str(i) + ' - ' + str(len(current)) + ' seeds - ' + str(len(new)) + ' new records')
		if len(new) > 0:
			print(new)
		i=i+1
	
	print(str(yr) + ' ending with ' + str(len(mopps)) + ' teams')
	yr=yr+1

print(mopps)