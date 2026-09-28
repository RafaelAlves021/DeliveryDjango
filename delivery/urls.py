from django.urls import path
from . import views

urlpatterns = [
    path('', views.cardapio_view, name='cardapio'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_carrinho_view, name='adicionar_carrinho'),
    path('carrinho/', views.ver_carrinho_view, name='ver_carrinho'),
    path('carrinho/remover/<int:produto_id>/', views.remover_carrinho_view, name='remover_carrinho'),
]