import csv
from django.core.files.base import ContentFile

from .models import Candidate

CSV_FILE_PATH = '/tmp/candidatos.csv'
PHOTOS_PATH = '/tmp/fotos_candidatos/'

class CandidatesImporter():

    @staticmethod
    def import_candidates():
        with open(CSV_FILE_PATH, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter='|', quotechar='"')
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
        email_tse = row[6]
        email_survey = row[16]
        if (email_tse and email_survey):
            public_email = email_survey
        else:
            public_email = email_tse
        party = row[7]

        occupation_tse = row[9]
        occupation_survey = row[17]
        if (occupation_tse and occupation_survey):
            occupation = occupation_survey
        else:
            occupation = occupation_tse

        riches = row[10]
        lawsuits = row[14]
        site_url = row[18]
        facebook_url = row[19]
        twitter_url = row[20]
        instagram_url = row[21]
        youtube_url = row[22]
        crowdfunding_url = row[23]
        has_clean_pass = row[24]
        adhered_to_the_measures = row[27]
        justify_adhered_to_the_measures = row[28]
        committed_to_democracy = row[29]
        try:
            try:
                # Django not trigger an pre_save or post_save event for the
                # update method, so we need to call save() to do that.
                candidate = Candidate.objects.get(urn=urn, uf=uf)
                print("updating candidate %s" % candidate.name)
                candidate.uf=uf
                candidate.candidacy=candidacy
                candidate.name=name
                candidate.urn=urn
                candidate.party=party
                candidate.full_name=full_name
                candidate.justify_adhered_to_the_measures=justify_adhered_to_the_measures
                candidate.has_clean_pass=has_clean_pass
                candidate.riches=riches
                candidate.lawsuits=lawsuits
                candidate.occupation=occupation
                candidate.committed_to_democracy=committed_to_democracy
                candidate.adhered_to_the_measures=adhered_to_the_measures
                candidate.public_email=public_email
                candidate.site_url=site_url
                candidate.twitter_url=twitter_url
                candidate.instagram_url=instagram_url
                candidate.youtube_url=youtube_url
                candidate.crowdfunding_url=crowdfunding_url
                candidate.save()
            except Exception as e:
                candidate = Candidate(uf=uf, candidacy=candidacy, name=name,
                                    urn=urn, party=party, full_name=full_name,
                                    justify_adhered_to_the_measures=justify_adhered_to_the_measures,
                                    has_clean_pass=has_clean_pass,
                                    riches=riches,
                                    lawsuits=lawsuits,
                                    occupation=occupation,
                                    committed_to_democracy=committed_to_democracy,
                                    adhered_to_the_measures=adhered_to_the_measures,
                                    public_email=public_email,
                                    site_url=site_url,
                                    twitter_url=twitter_url,
                                    instagram_url=instagram_url,
                                    youtube_url=youtube_url,
                                    facebook_url=facebook_url,
                                    crowdfunding_url=crowdfunding_url)
                cpf = row[5]
                candidate.image.name = CandidatesImporter\
                    .set_candidate_photo(candidate, cpf)
                candidate.save()
                print("imported candidate: ", name)
        except Exception as e:
            print(e)
            print("could not import candidate")

    @staticmethod
    def set_candidate_photo(candidate, cpf):
        photo_name = 'img_' + cpf + '.jpg'
        _storage = candidate.image.storage
        try:
            with open(PHOTOS_PATH + photo_name, 'rb') as f:
                photo = f.read()
                _storage.save(photo_name, ContentFile(photo))
                return photo_name
        except Exception as e:
            print(e)
            print('could not import candidate photo')
            return 'card_avatar-default.png'
