import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Categoria, Produto, Pedido, ItemPedido
from .carrinho import Carrinho
from .forms import CheckoutForm, ProdutoForm
from django.contrib import messages
from .forms import CadastroComEmailForm, CheckoutForm, ProdutoForm



# -------------------------------------------------------------
# 1. NAVEGAÇÃO E CATÁLOGO
# -------------------------------------------------------------
def cardapio_view(request):
    categorias = Categoria.objects.prefetch_related('produtos').all()
    carrinho = Carrinho(request)
    return render(request, 'delivery/cardapio.html', {
        'categorias': categorias,
        'carrinho': carrinho,
    })


def produto_detalhe_view(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho = Carrinho(request)
    return render(request, 'delivery/produto_detalhe.html', {
        'produto': produto,
        'carrinho': carrinho,
    })


# -------------------------------------------------------------
# 2. CRUD DE PRODUTOS (PROTEGIDO POR LOGIN)
# -------------------------------------------------------------
@login_required
def produto_criar_view(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save()
            return redirect('produto_detalhe', produto_id=produto.id)
    else:
        form = ProdutoForm()
    return render(request, 'delivery/produto_form.html', {
        'form': form,
        'titulo': 'Adicionar Produto'
    })


@login_required
def produto_editar_view(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('produto_detalhe', produto_id=produto.id)
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'delivery/produto_form.html', {
        'form': form,
        'titulo': 'Editar Produto',
        'produto': produto
    })


@login_required
def produto_excluir_view(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    if request.method == 'POST':
        produto.delete()
        return redirect('cardapio')
    return render(request, 'delivery/produto_confirmar_exclusao.html', {
        'produto': produto
    })


# -------------------------------------------------------------
# 3. GESTÃO DO CARRINHO (SESSÕES)
# -------------------------------------------------------------
def adicionar_carrinho_view(request, produto_id):
    carrinho = Carrinho(request)
    carrinho.adicionar(produto_id=produto_id)
    if 'carrinho' in request.META.get('HTTP_REFERER', ''):
        return redirect('ver_carrinho')
    return redirect('cardapio')


def diminuir_carrinho_view(request, produto_id):
    carrinho = Carrinho(request)
    carrinho.diminuir(produto_id=produto_id)
    return redirect('ver_carrinho')


def remover_carrinho_view(request, produto_id):
    carrinho = Carrinho(request)
    carrinho.remover(produto_id=produto_id)
    return redirect('ver_carrinho')


def ver_carrinho_view(request):
    carrinho = Carrinho(request)
    return render(request, 'delivery/carrinho.html', {
        'carrinho': carrinho
    })


# -------------------------------------------------------------
# 4. FINALIZAÇÃO DO PEDIDO
# -------------------------------------------------------------
def finalizar_pedido_view(request):
    carrinho = Carrinho(request)
    if len(carrinho) == 0:
        return redirect('cardapio')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            pedido = form.save()

            for item in carrinho:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=item['produto'],
                    quantidade=item['quantidade'],
                    preco_unitario=item['preco'],
                )

            carrinho.limpar()
            return redirect('pedido_concluido', pedido_id=pedido.id)
    else:
        form = CheckoutForm()

    return render(request, 'delivery/finalizar_pedido.html', {
        'form': form,
        'carrinho': carrinho,
    })


def pedido_concluido_view(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'delivery/pedido_concluido.html', {
        'pedido': pedido
    })


# -------------------------------------------------------------
# 5. AUTENTICAÇÃO E CADASTRO
# -------------------------------------------------------------
def cadastro(request):
    # Se o usuário já estiver logado, redireciona direto para o cardápio
    if request.user.is_authenticated:
        return redirect('cardapio')

    if request.method == 'POST':
        form = CadastroComEmailForm(request.POST)
        
        if form.is_valid():
            # 1. Salva o usuário no banco de dados
            user = form.save()
            
            # --- INTEGRAÇÃO EMAILJS ---
            emailjs_url = 'https://api.emailjs.com/api/v1.0/email/send'
            
            payload = {
                'service_id': 'service_ronjmrm',
                'template_id': 'template_6rl1y0p',
                'user_id': 'VmfhGJBIJtBhqnVDe',
                'accessToken': 'Wuw3qe-53Bimd6dveQN3L',
                'template_params': {
                    'nome_usuario': user.username,
                    'email_destino': user.email
                }
            }
            
            try:
                resposta = requests.post(emailjs_url, json=payload)
                if resposta.status_code != 200:
                    print(f"Erro EmailJS: {resposta.text}")
            except Exception as e:
                print(f"Erro de conexão com EmailJS: {e}")
            # --------------------------

            # 2. Faz o login automático e redireciona para o cardápio
            login(request, user)
            return redirect('cardapio')
    else:
        form = CadastroComEmailForm()

    return render(request, 'delivery/registration/cadastro.html', {'form': form})