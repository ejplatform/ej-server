import os
from jinja2 import Environment, FileSystemLoader

from ej_boards.models import Board
from ej_conversations.models import Conversation


class Snapshot():

    def __init__(self, conversation, request, template_type='mautic'):
        self.PALETTE_CLASS = {
            'green': CommonPalette,
            'grey': CommonPalette,
            'blue': CommonPalette,
            'orange': CommonPalette,
            'purple': CommonPalette,
            'pink': CommonPalette,
            'campaign': CampaignPalette
        }
        self.template_type = template_type
        self.conversation = conversation
        self.palette = self.palette_from_conversation()
        self.host_url = Snapshot.get_host_url_with_schema(request)

    def get_template(self):
        try:
            return self.render_jinja_template()
        except:
            raise

    def render_jinja_template(self):
        root = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(root, '../integrations')
        env = Environment(loader=FileSystemLoader(templates_dir))
        template = env.get_template('{}_snapshot.html'.format(self.template_type))
        data = template.render(
            conversation_title=self.conversation.text,
            comment_content=self.conversation.comments.all()[0].content,
            comment_author=self.conversation.comments.all()[0].author.name,
            vote_url=self.url_to_compute_vote(),
            site_url=self.host_url,
            tags=self.conversation.tags.all(),
            palette_css=self.palette
        )
        return data

    def palette_from_conversation(self):
        try:
            conversation_palette = self.conversation.boards.first().palette.lower()
        except:
            conversation_palette = 'blue'
        return conversation_palette

    def url_to_compute_vote(self):
        conversation_slug = self.conversation.slug
        conversation_id = self.conversation.id
        comment_id = self.conversation.comments.all()[0].id
        try:
            board_slug = self.conversation.boards.first().slug
            url = '{}/{}/conversations/{}/{}?comment_id={}&action=vote&origin=campaign'
            return url.format(self.host_url, board_slug, conversation_id, conversation_slug, comment_id)
        except:
            url = '{}/conversations/{}/{}?comment_id={}&action=vote&origin=campaign'
            return url.format(self.host_url, conversation_id, conversation_slug, comment_id)

    def get_css_from_palette(self, conversation_palette='blue'):
        paletteClass = self.PALETTE_CLASS[conversation_palette]
        return paletteClass(conversation_palette).css()

    @staticmethod
    def get_host_url_with_schema(request):
        scheme = request.META['wsgi.url_scheme']
        host = request.META['HTTP_HOST']
        _site_url = '{}://{}'.format(scheme, host)
        return _site_url


class CommonPalette():

    def __init__(self, palette='blue'):
        self.INLINE_PALETTES = {
            'green': ['#36C273', '#B4FDD4'],
            'grey': ['#666666', '#EEEEEE'],
            'blue': ['#30BFD3', '#C4F2F4'],
            'orange': ['#F5700A', '#FFE1CA'],
            'purple': ['#7758B3', '#E7DBFF'],
            'pink': ['#C6027B', '#FFE3EA'],
        }
        self.palette = palette

    def css(self):
        colors = self.INLINE_PALETTES[self.palette]
        palette_style = {}
        palette_style['light'] = 'color: {}; background-color: {};'.format(colors[0], colors[1])
        palette_style['dark'] = 'color: {} !important; background-color: {};'.format(colors[1], colors[0])
        palette_style['arrow'] = 'border-top: 28px solid {} !important;'.format(colors[1])
        palette_style['light-h1'] = ''
        palette_style['dark-h1'] = ''
        return palette_style


class CampaignPalette():

    def __init__(self, palette='campaign'):
        self.INLINE_PALETTES = {'campaign': ['#1c9dd9', '#332f82']}
        self.palette = palette

    def css(self):
        colors = self.INLINE_PALETTES[self.palette]
        palette_style = {}
        palette_style['light'] = 'color: {}; background-color: {};'.format(colors[0], colors[1])
        palette_style['dark'] = 'color: {} !important; background-color: {};'.format(colors[1], colors[0])
        palette_style['arrow'] = 'border-top: 28px solid {} !important;'.format(colors[1])
        border_style = ' border-radius: unset;'
        palette_style['light-h1'] = 'color: #ffffff !important;'
        palette_style['dark-h1'] = 'color: #1c9dd9 !important;'
        palette_style['dark'] += border_style
        palette_style['light'] += border_style
        return palette_style
