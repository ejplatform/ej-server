from boogie.router import Router

app_name = "ej_gamification"
urlpatterns = Router(template="ej_gamification/leaderboard/{name}.jinja2", login=True)


# @urlpatterns.route('')
# def index(request):
#     user = request.user
#     return {
#         'user': user,
#     }
