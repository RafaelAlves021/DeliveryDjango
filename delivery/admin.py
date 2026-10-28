from django.contrib import admin
from .models import Categoria, ItemPedido, Pedido, Produto, Restaurante


@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
  list_display = ('nome', 'slug', 'dono', 'whatsapp', 'ativo')
  prepopulated_fields = {'slug': ('nome',)}
  search_fields = ('nome', 'slug', 'dono__username')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
  list_display = ('nome', 'restaurante', 'ordem')
  list_filter = ('restaurante',)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
  list_display = (
      'nome',
      'restaurante',
      'categoria',
      'preco',
      'disponivel',
  )
  list_filter = ('restaurante', 'categoria', 'disponivel')
  search_fields = ('nome', 'descricao')


class ItemPedidoInline(admin.TabularInline):
  model = ItemPedido
  extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
  list_display = (
      'id',
      'restaurante',
      'cliente_nome',
      'status',
      'forma_pagamento',
      'criado_em',
  )
  list_filter = ('restaurante', 'status', 'forma_pagamento')
  inlines = [ItemPedidoInline]