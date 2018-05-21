import pytest

from ej_configurations import fragments
from ej_configurations.models import Fragment


pytestmark = pytest.mark.django_db

MISSING_FRAGMENT_HTML = '''
<h1>Missing "name" fragment</h1>
<p>Click <a href="/debug/fragments/name/" up-modal="main">here</a> to know more</p>
'''


@pytest.fixture
def fragment_db(db):
    fragment = Fragment(
        name='name',
        format='html',
        content='content'
    )
    fragment.save()
    return fragment


def test_get_non_existent_fragment_withouth_default_fragment():
    # test method call raising error
    try:
        test_fragment = fragments.fragment('name')
    except ValueError:
        assert True

    # test method call without raise error
    test_fragment = fragments.fragment('name', False)
    assert test_fragment.content == MISSING_FRAGMENT_HTML


def test_get_existent_fragment(fragment_db):
    test_fragment = fragments.fragment('name')
    assert test_fragment.name == 'name'
    assert test_fragment.format == 'html'
    assert test_fragment.content == 'content'
