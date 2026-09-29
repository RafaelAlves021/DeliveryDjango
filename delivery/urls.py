from django.urls import path
from . import views

urlpatterns = [
    path('', views.cardapio_view, name='cardapio'),
    path('produto/novo/', views.produto_criar_view, name='produto_criar'),
    path('produto/<int:produto_id>/', views.produto_detalhe_view, name='produto_detalhe'),
    path('produto/<int:produto_id>/editar/', views.produto_editar_view, name='produto_editar'),
    path('produto/<int:produto_id>/excluir/', views.produto_excluir_view, name='produto_excluir'),
    path('carrinho/', views.ver_carrinho_view, name='ver_carrinho'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_carrinho_view, name='adicionar_carrinho'),
    path('carrinho/diminuir/<int:produto_id>/', views.diminuir_carrinho_view, name='diminuir_carrinho'),
    path('carrinho/remover/<int:produto_id>/', views.remover_carrinho_view, name='remover_carrinho'),
    path('finalizar/', views.finalizar_pedido_view, name='finalizar_pedido'),
    path('pedido/<int:pedido_id>/sucesso/', views.pedido_concluido_view, name='pedido_concluido'),
]