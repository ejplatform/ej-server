import csv
from .models import Candidate


CSV_PATH = '/tmp/candidatos.csv'
class CandidatesImporter():

    @staticmethod
    def import_candidates():
        with open(CSV_PATH, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                CandidatesImporter.create_candidate_from_row(row)

    @staticmethod
    def create_candidate_from_row(row):
        if (row[0] == "uf"):
            return
        uf = row[0]
        candidacy = row[1]
        urn = int(row[2])
        full_name = row[3]
        name = row[4]
        public_email = row[6]
        party = row[7]
        occupation = row[9]
        adhered_to_the_measures = row[10]
        justify_adhered_to_the_measures = row[11]
        riches = row[12]
        lawsuits = row[13]
        has_clean_pass = row[19]
        committed_to_democracy = row[20]
        try:
            candidate = Candidate(uf=uf, candidacy=candidacy, name=name,
                                  urn=urn, party=party, full_name=full_name,
                                  justify_adhered_to_the_measures=justify_adhered_to_the_measures,
                                  has_clean_pass=has_clean_pass,
                                  riches=riches,
                                  lawsuits=lawsuits,
                                  committed_to_democracy=committed_to_democracy,
                                  adhered_to_the_measures=adhered_to_the_measures,
                                  public_email=public_email)
            candidate.save()
            print("imported candidate: ", name)
        except Exception as e:
            print(e)
            print("could not import candidate")

