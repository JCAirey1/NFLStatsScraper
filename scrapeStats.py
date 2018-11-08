import os
from bs4 import BeautifulSoup
from requests import get
import datetime
import re

yr = 1966
teamlist = ['atl', 'buf', 'car', 'chi', 'cin', 'cle', 'clt', 'crd', 'dal', 'den', 'det', 'gnb', 'htx', 'jax', 'kan', 'mia', 'min', 'nor', 'nwe', 'nyg', 'nyj', 'oti', 'phi', 'pit', 'rai', 'ram', 'rav', 'sdg', 'sea', 'sfo', 'tam', 'was']

def geturl(abbv, yr):
	return 'https://www.pro-football-reference.com/teams/' + abbv + '/' + str(yr) + '/gamelog/';

def getabbv(url):
	m = re.search('.*\/teams\/(.+?)\/\d\d\d\d', url)
	if m:
		return m.group(1)

def getHeaders(html_soup):
	retval = {}
	stats_headers = [];
	meta_headers = [];
	statsidx = 0
	table = html_soup.find("div", class_="table_wrapper")

	for i, header in enumerate(table.find("tr", class_=lambda x: x!= "over_header").find_all('th')):
		if statsidx > 0:
			stats_headers.append(header["data-stat"])
		elif header["data-stat"] == 'opp':
			statsidx = i + 1
		elif header["data-stat"] == 'boxscore_word':
			None
		elif header["data-stat"] == 'game_outcome':
			None
		elif header["data-stat"] == 'game_location':
			None
		else:
			meta_headers.append(header["data-stat"])

	retval['statsidx'] = statsidx
	retval['val'] = "year," + ",".join(map(str, meta_headers)) + ",h_team," + ",".join(map(lambda x: 'h_' + x, stats_headers)) + ",a_team," + ",".join(map(lambda x: 'a_' + x, stats_headers))

	return retval

def parseGames(table, team, games):
	#table = html_soup.find("table", class_="sliding_cols")
	table = html_soup.find("tbody")
	if table is None:
		return

	for x,row in enumerate(table.find_all("tr")):
		stats = [team];
		meta = [str(yr)];
		away = False
		opp = ''
		instats = False
		week = ''

		for i, cell in enumerate(row.find_all(['td','th'])):
			if cell.has_attr('data-stat'):
				if instats == True:
					stats.append(cell.get_text())
				elif cell["data-stat"] == 'week_num':
					week = cell.get_text()
					meta.append(cell.get_text())
				elif cell["data-stat"] == 'game_location':
					if cell.get_text() == '@':
						away = True
				elif cell["data-stat"] == 'opp':
					opp = getabbv(cell.find('a')['href'])
					instats = True
				elif cell["data-stat"] == 'boxscore_word':
					None
				elif cell["data-stat"] == 'game_outcome':
					None
				else:
					meta.append(cell.get_text())

		if week != '':
			if not week in games and week != '':
				games[week] = {}

			if away == False:
				if not team in games[week]:
					games[week][team] = {}
				games[week][team]['meta'] = meta
				games[week][team]['h'] = stats
				if not 'a' in games[week][team]:
					games[week][team]['a'] = ['N/A' for item in stats]
					games[week][team]['a'][0] = opp
			else:
				if not opp in games[week]:
					games[week][opp] = {}
				games[week][opp]['meta'] = meta
				games[week][opp]['a'] = stats
				if not 'h' in games[week][opp]:
					games[week][opp]['h'] = ['N/A' for item in stats]
					games[week][opp]['h'][0] = opp

while yr <= datetime.datetime.now().year:
	games = {}
	for team in teamlist:
		try:
			response = get(geturl(team, yr))
			html_soup = BeautifulSoup(response.text, 'html.parser')
			headers = getHeaders(html_soup)
			parseGames(html_soup, team, games)
		except Exception as e: 
			print('Error year:' + str(yr) + ' Team:' + team)
			print(e)

	filename = str(yr) + '.csv'
	os.remove(filename) if os.path.exists(filename) else None

	with open(filename, 'a') as f:
		f.write(headers['val'] + '\n')

		for week in games:
			for location in games[week]:
				f.write(','.join('"{0}"'.format(w) for w in games[week][location]['meta']) + ',' +
					','.join('"{0}"'.format(w) for w in games[week][location]['h']) + ',' +
					','.join('"{0}"'.format(w) for w in games[week][location]['a']))
				f.write('\n')
	yr = yr + 1