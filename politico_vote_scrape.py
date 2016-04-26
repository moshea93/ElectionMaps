from bs4 import BeautifulSoup
from urllib2 import urlopen
from datetime import datetime
import csv
import json

#get urls for states(which have county info)
def get_state_urls(overview_url):
	html = urlopen(overview_url).read()
	soup = BeautifulSoup(html, 'lxml')
	targets = soup.find_all('article', class_='timeline-group')

	BASE_URL = 'http://s3.amazonaws.com/origin-east-elections.politico.com/mapdata/2016/'
	urls = []

	#get state abbreviations
	with open('state_abbreviations.csv', 'r') as statefile:
		statelist = csv.DictReader(statefile)
		abbreviations = {}
		for line in statelist:
			abbreviations[line['state_name']] = line['state_abbr']

	for state in targets:
		#get states that have already voted
		days = state.find_all('time')
		for day in days:
			curr = day.get('datetime')
			date = datetime.strptime(curr, '%Y-%m-%d').date()
			if date.today() > date:
				name = state.find('h3').find('a').get_text(strip=True).title()
				#exclude District of Columbia, other non-states
				if name in abbreviations:
					urls.append(BASE_URL + abbreviations[name] + '_' + str(date.strftime('%Y%m%d')) + '.xml?cachebuster=bustit')
	return urls

def create_county_data(urls):
	#information to grab
	state = []
	state_abbreviation = []
	county = []
	fips = []
	party = []
	candidate = []
	votes = []
	vote_share = []

	for link in urls:
		info = urlopen(link).read()
		lines = info.split('\n')

		#match candidate ids to candidates
		d = {}
		candidate_ids = lines[1].split('|')
		for x in candidate_ids:
			bits = x.split(';')
			d[bits[0]] = (bits[2] + ' ' + bits[1]).strip()
		
		state_info = lines[3].split(';')
		currstate = state_info[4]
		currabbrev = state_info[0]
		#cycle through counties
		for x in lines[4:]:
			if x == '':
				continue
			county_info = x.split(';')
			if county_info[1] == 'P':
				currcounty = county_info[4]
				currfips = str('%05d' %int(county_info[3]))
				#check if data not by county
				if currfips == '00000':
					#skip over total state numbers
					if currcounty == currstate:
						continue
					currfips = ''
					currcounty = 'District ' + currcounty
				if currcounty == 'null':
					currfips = ''
					currcounty = 'statewide'
				#cycle through candidates
				people = x.split('|')[2:]
				for person in people:
					candidate_info = person.split(';')
					if candidate_info[1] == 'Dem':
						currparty = 'Democratic'
					elif candidate_info[1] == 'GOP':
						currparty = 'Republican'
					else:
						currparty = 'Other'
					currcandidate = d[candidate_info[0]]
					currvotes = candidate_info[2]
					currvoteshare = candidate_info[3]
					state.append(currstate)
					state_abbreviation.append(currabbrev)
					county.append(currcounty)
					fips.append(currfips)
					party.append(currparty)
					candidate.append(currcandidate)
					votes.append(currvotes)
					vote_share.append(currvoteshare)
	rows = zip(state,state_abbreviation,county,fips,party,candidate,votes,vote_share)
	with open('results.csv', 'w') as f:
		writer = csv.writer(f)
		writer.writerow(['state', 'state_abbreviation', 'county', 'fips', 'party', 'candidate', 'votes', 'vote_share'])
		for row in rows:
			writer.writerow(row)

if __name__ == '__main__':
	state_urls =  get_state_urls('http://www.politico.com/2016-election/results/map/president')
	create_county_data(state_urls)
