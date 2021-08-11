from django import views
from django.shortcuts import render

from .models import Artist, Album

# Create your views here.
class BaseView(views.View):

    def get(self, request, *args, **kwargs):
        return render(request, 'base.html', {})


class ArtistDetailView(views.generic.DetailView):

    model = Artist
    template_name = 'artist/artist_detail.html'
    slug_url_kwarg = 'artist_slug'
    content_object_name = 'artist'


class AlbumDetailView(views.generic.DetailView):

    model = Artist
    template_name = 'album/album_detail.html'
    slug_url_kwarg = 'album_slug'
    content_object_name = 'album'
