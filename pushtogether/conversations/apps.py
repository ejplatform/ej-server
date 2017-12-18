from django.apps import AppConfig


class ConversationsConfig(AppConfig):
    name = 'pushtogether.conversations'
    verbose_name = "Conversations"

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Conversation'))
        registry.register(self.get_model('Comment'))
        registry.register(self.get_model('Vote'))

        import pushtogether.conversations.signals
