from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("conexion/", views.estado_conexion, name="conexion"),

    path("usuarios/", views.usuarios_lista, name="usuarios"),
    path("usuarios/nuevo/", views.usuario_form, name="usuario_nuevo"),
    path("usuarios/<str:id>/editar/", views.usuario_form, name="usuario_editar"),
    path("usuarios/<str:id>/eliminar/", views.usuario_eliminar, name="usuario_eliminar"),

    path("artistas/", views.artistas_lista, name="artistas"),
    path("artistas/nuevo/", views.artista_form, name="artista_nuevo"),
    path("artistas/<str:id>/editar/", views.artista_form, name="artista_editar"),
    path("artistas/<str:id>/eliminar/", views.artista_eliminar, name="artista_eliminar"),

    path("albumes/", views.albumes_lista, name="albumes"),
    path("albumes/nuevo/", views.album_form, name="album_nuevo"),
    path("albumes/<str:id>/editar/", views.album_form, name="album_editar"),
    path("albumes/<str:id>/eliminar/", views.album_eliminar, name="album_eliminar"),

    path("canciones/", views.canciones_lista, name="canciones"),
    path("canciones/nuevo/", views.cancion_form, name="cancion_nuevo"),
    path("canciones/<str:id>/editar/", views.cancion_form, name="cancion_editar"),
    path("canciones/<str:id>/eliminar/", views.cancion_eliminar, name="cancion_eliminar"),

    path("playlists/", views.playlists_lista, name="playlists"),
    path("reportes/", views.reportes, name="reportes"),
]
