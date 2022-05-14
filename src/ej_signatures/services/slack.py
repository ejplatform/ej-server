from slack_sdk.webhook import WebhookClient
import os


class SlackService:
    def __init__(self):
        self.client = WebhookClient(os.environ["SLACK_WEBHOOK_URL"])

    def notify_request(self, request):
        fields = ["name", "email", "phone", "signature", "goal"]
        data = dict.fromkeys(
            fields,
        )
        for field in fields:
            data[field] = request.POST.get(field)
        data["origin_signature"] = request.user.signature
        return self.client.send(blocks=self.create_blocks(data))

    def create_blocks(self, data):
        signature_map = {
            "listen_to_community": "Listen To Community",
            "listen_to_city": "Listen To City",
            "custom": "Customized",
        }
        data["origin_signature"] = signature_map[data["origin_signature"]]
        data["signature"] = signature_map[data["signature"]]

        return [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "New EJ signature upgrade request", "emoji": True},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*From:* " + data["origin_signature"] + "\n*To* " + data["signature"],
                },
            },
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Name:* " + data["name"]}},
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Email:* " + data["email"]}},
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Goal:* " + data["goal"]}},
        ]
