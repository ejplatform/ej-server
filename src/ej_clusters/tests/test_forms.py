from django.utils.translation import ugettext as _
from ej_clusters.forms import StereotypeForm
from ej_clusters.models import Stereotype
from ej_clusters.mommy_recipes import ClusterRecipes


class TestStereotypeForm(ClusterRecipes):
    def test_valid_data(self, user_db):
        form = StereotypeForm({"name": "Stereotype", "description": "description"}, owner=user_db)
        assert form.is_valid()
        stereotype = form.save(commit=False)
        stereotype.owner = user_db
        stereotype.full_clean()
        assert stereotype.name == "Stereotype"
        assert stereotype.description == "description"

    def test_blank_data(self, user_db):
        form = StereotypeForm({}, owner=user_db)
        assert not form.is_valid()
        assert form.errors == {"name": [_("This field is required.")]}

    def test_edit_existing_stereotype(self, user_db):
        instance = Stereotype.objects.create(name="Stereotype1", owner=user_db)
        form = StereotypeForm({"name": "Stereotype1", "description": "description"}, instance=instance)
        print(form.errors)
        assert form.is_valid()

    def test_repetead_stereotype_data(self, user_db):
        Stereotype.objects.create(name="Stereotype1", owner=user_db)
        form = StereotypeForm({"name": "Stereotype1", "description": "description"}, owner=user_db)
        assert not form.is_valid()
        assert set(form.errors) == {"__all__"}
