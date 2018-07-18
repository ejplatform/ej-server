from ej_trophies.models.user_trophy import UserTrophy

class MissionMixin(object):

    def get_blocked(self, obj, user=None):

        if (user):
            user_id = user.id
        else:
            user_id = self.context['uid']

        def filter_trophies(user_trophy):
            return (user_trophy.trophy.key == req.key and\
                user_trophy.percentage == 100)

        required_trophies = obj.trophy.required_trophies.all()
        user_trophies = UserTrophy.objects.filter(percentage=100,
                                                  user_id= user_id)
        if (len(required_trophies) == 0):
            return False

        filtered_trophies = []
        for req in required_trophies:
            filtered = list(filter(filter_trophies, list(user_trophies)))
            if len(filtered) > 0:
                filtered_trophies.append(filtered)
        if (len(filtered_trophies) == len(required_trophies)):
            return False

        return True
