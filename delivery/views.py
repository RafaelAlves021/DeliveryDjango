from django.shortcuts import render, redirect, get_object_or_404
from .models import Categoria, Produto
from .carrinho import Carrinho

def cardapio_view(request):
    categorias = Categoria.objects.prefetch_related('produtos').all()
    carrinho = Carrinho(request)
    return render(request, 'delivery/cardapio.html', {
        'categorias': categorias,
        'carrinho': carrinho,
    })

def adicionar_carrinho_view(request, produto_id):
    carrinho = Carrinho(request)
    carrinho.adicionar(produto_id=produto_id)
    return redirect('cardapio')

def ver_carrinho_view(request):
    carrinho = Carrinho(request)
    return render(request, 'delivery/carrinho.html', {'carrinho': carrinho})

def remover_carrinho_view(request, produto_id):
    carrinho = Carrinho(request)
    carrinho.remover(produto_id=produto_id)
    return redirect('ver_carrinho')
