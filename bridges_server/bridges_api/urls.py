from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from bridges_api import views

urlpatterns = [
    url(r'^questions/$', views.QuestionList.as_view()),
    url(r'^questions/(?P<pk>[0-9]+)/$', views.QuestionDetail.as_view()),
    url(r'^users/', views.UserList.as_view()),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
