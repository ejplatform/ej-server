import pytest

from django.utils.translation import ugettext as _

from ej_profiles.choices import Gender, Race
from ej_profiles.models import Profile
from ej_users.models import User
from datetime import date


class TestProfile:
    @pytest.fixture
    def profile(self):
        return Profile(
            user=User(email='user@domain.com', name='name'),
            profile_photo='profile_photo',
            birth_date=date(1996, 1, 17),
            country='country',
            city='city',
            state='state',
            biography='biography',
            occupation='occupation',
            gender=Gender.FEMALE,
            political_activity='political_activity',
            race=Race.INDIGENOUS,
            ethnicity="ethnicity",
            education="undergraduate",
        )

    @pytest.mark.skip(reason="Translations are breaking this kind of test")
    def test_profile_invariants(self, profile):
        assert str(profile) == 'name\'s profile'
        assert profile.profile_fields() == [
            ('Cidade', 'city'),
            ('País', 'country'),
            ('Ocupação', 'occupation'),
            ('Idade', profile.age),
            ('Escolaridade', 'undergraduate'),
            ('Etnia', 'ethnicity'),
            ('Identidade de gênero', 'female'),
            ('Raça', 'indigenous'),
            ('Atividade política', 'political_activity'),
            ('Biografia', 'biography'),
        ]
        assert profile.is_filled
        assert profile.statistics() == {'votes': 0, 'comments': 0, 'conversations': 0}
        assert profile.role() == _('Regular user')

        # Remove a field
        profile.occupation = ''
        assert not profile.is_filled
