from django.http import Http404
from rest_framework import status, permissions
from rest_framework.decorators import detail_route, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ej.users.models import User
from ej.users.permissions import IsCurrentUserOrAdmin
from ej.users.serializers import UserSerializer


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @detail_route(methods=['POST'])
    @parser_classes((FormParser, MultiPartParser))
    def image(self, request, *args, **kwargs):
        if 'image' in request.data:
            user_profile = self.get_object()
            user_profile.image.delete()
            upload = request.data['image']
            user_profile.image.save(upload.name, upload)
            serializer = UserSerializer(user_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, *args, **kwargs):
        # Using the /users/me endpoint
        if pk == 'me':
            #for future login verification
            #if self.request.user.has_real_login():
            instance = request.user
            #else:
                #raise Http404
        else:
            instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [permissions.IsAdminUser, ]
        elif self.action == 'retrieve':
            self.permission_classes = [IsCurrentUserOrAdmin]
        else:
            raise ValueError("Viewset action is not set")
        return super(self.__class__, self).get_permissions()
