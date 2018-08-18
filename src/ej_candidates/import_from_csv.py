import csv
from .models import Candidate


class CandidatesImporter(object):

    """A class responsible to import candidates from csv file"""

    def __init__(self):
        self.csv = '/tmp/candidatos.csv'

    def import_candidates(self):
        with open(self.csv, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                self.create_candidate_from_row(row)

    def create_candidate_from_row(self, row):
        if (row[0] == "uf"):
            return
        uf = row[0]
        candidacy = row[1]
        name = row[5]
        urn = int(row[3])
        party = row[6]
        has_clean_pass = row[10]
        committed_to_democracy = row[11]
        adhered_to_the_measures = row[12]
        site_url = row[13]
        crowdfunding_url = row[14]
        facebook_url = row[15]
        twitter_url = row[16]
        instagram_url = row[17]
        youtube_url = row[18]
        try:
            candidate = Candidate(uf=uf, candidacy=candidacy, name=name,
                                  urn=urn, party=party,
                                  has_clean_pass=has_clean_pass,
                                  committed_to_democracy=committed_to_democracy,
                                  adhered_to_the_measures=adhered_to_the_measures,
                                  site_url=site_url,
                                  crowdfunding_url=crowdfunding_url,
                                  facebook_url=facebook_url,
                                  twitter_url=twitter_url,
                                  instagram_url=instagram_url,
                                  youtube_url=youtube_url)
            candidate.save()
            print("imported candidate: ", name)
        except Exception as e:
            print(e)
            print("could not import candidate")

