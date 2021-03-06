from bridges_api.models import Question, UserProfile
from bridges_api.serializers import (
    QuestionSerializer,
    UserSerializer,
    UserProfileSerializer
)
from bridges_api.permissions import MustBeSuperUserToGET

from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.parsers import JSONParser

def restrict_fields(query_dict, fields):
    """
    Filters the fields in a query_dict based on a list
    of strings
    """
    restricted_dict = {}
    for field in fields:
        if query_dict.get(field):
            restricted_dict[field] = query_dict.get(field)
    return restricted_dict

@api_view(['GET'])
def api_root(request, format=None):
    """
    The response object is dank, and takes a python dictionary and
    renders it directly, no template necessary!
    """
    return Response({
        'questions': reverse('questions-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format),
    })

class QuestionList(generics.ListAPIView):
    """
    This uses that generic API list view to return a list
    of Question models as a response to GET requests. The queryset
    variable is the list of Question Models that ultimately gets
    serialized and returned to the User
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticated,)

class QuestionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns the specific Question object with its corresponding id
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticated,)

class UserList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (MustBeSuperUserToGET,)

    def post(self, request, *args, **kwargs):
        """
        Overwritting POST request behavior so that creating a new user
        requires a unique username, a password, first name, last name,
        email address, birth date formatted as YYYY-MM-DD, disabilities, and gender
        """
        user_fields = UserSerializer().fields.keys()
        profile_fields = UserProfileSerializer().fields.keys()

        user_data = restrict_fields(request.data, user_fields)
        profile_data = restrict_fields(request.data, profile_fields)

        user_serializer = UserSerializer(data=user_data)
        profile_serializer = UserProfileSerializer(data=profile_data)

        if user_serializer.is_valid():
            if profile_serializer.is_valid():
               new_user = user_serializer.save()
               tethered_profile_serializer = UserProfileSerializer(new_user.userprofile,
                                                                   data=profile_data)
               if tethered_profile_serializer.is_valid():
                   tethered_profile_serializer.save()
                   return Response({
                        'user_id': new_user.pk
                   }, status=status.HTTP_201_CREATED)

            return Response({
                'errors': profile_serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'errors': user_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(generics.RetrieveAPIView):
    """
    Returns all the information tethered to a specific user
    Should be whichever user id is in /users/<id> when that endpoint is hit
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
