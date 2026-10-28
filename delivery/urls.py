from django.urls import path
from . import views

urlpatterns = [
    # Cadastro da plataforma
    path('cadastro/', views.cadastro, name='cadastro'),

    # Rotas específicas de cada Restaurante/Loja (via Slug)
    path('<slug:restaurante_slug>/', views.cardapio_view, name='cardapio'),
    path('<slug:restaurante_slug>/produto/<int:produto_id>/', views.produto_detalhe_view, name='produto_detalhe'),
    
    # Gestão de Produtos pelo Lojista
    path('<slug:restaurante_slug>/produto/novo/', views.produto_criar_view, name='produto_criar'),
    path('<slug:restaurante_slug>/produto/<int:produto_id>/editar/', views.produto_editar_view, name='produto_editar'),
    path('<slug:restaurante_slug>/produto/<int:produto_id>/excluir/', views.produto_excluir_view, name='produto_excluir'),

    # API para criação rápida de Categoria via Modal
    path('<slug:restaurante_slug>/api/categoria/nova/', views.categoria_criar_api, name='api_categoria_criar'),

    # Carrinho e Pedidos isolados por Restaurante
    path('<slug:restaurante_slug>/carrinho/', views.ver_carrinho_view, name='ver_carrinho'),
    path('<slug:restaurante_slug>/carrinho/adicionar/<int:produto_id>/', views.adicionar_carrinho_view, name='adicionar_carrinho'),
    path('<slug:restaurante_slug>/carrinho/diminuir/<int:produto_id>/', views.diminuir_carrinho_view, name='diminuir_carrinho'),
    path('<slug:restaurante_slug>/carrinho/remover/<int:produto_id>/', views.remover_carrinho_view, name='remover_carrinho'),
    path('<slug:restaurante_slug>/finalizar/', views.finalizar_pedido_view, name='finalizar_pedido'),
    path('<slug:restaurante_slug>/pedido/<int:pedido_id>/sucesso/', views.pedido_concluido_view, name='pedido_concluido'),
    path('<slug:restaurante_slug>/status/alternar/', views.alternar_status_loja, name='alternar_status_loja'),

]