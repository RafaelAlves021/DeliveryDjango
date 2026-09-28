from django.contrib import admin
from .models import Categoria, Produto, Pedido, ItemPedido

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem')
    ordering = ('ordem',)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco', 'disponivel')
    list_filter = ('categoria', 'disponivel')
    search_fields = ('nome', 'descricao')
    list_editable = ('preco', 'disponivel')

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('produto', 'quantidade', 'preco_unitario', 'subtotal')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nome', 'cliente_telefone', 'forma_pagamento', 'status', 'total', 'criado_em')
    list_filter = ('status', 'forma_pagamento', 'criado_em')
    search_fields = ('cliente_nome', 'cliente_telefone', 'endereco_entrega')
    list_editable = ('status',)
    inlines = [ItemPedidoInline]