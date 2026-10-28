import json
import urllib.parse
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST

from .models import Restaurante, Categoria, Produto, Pedido, ItemPedido
from .carrinho import Carrinho
from .forms import CadastroComEmailForm, CheckoutForm, ProdutoForm, CategoriaForm


# -------------------------------------------------------------
# CONFIGURAÇÃO DO GATEWAY DE WHATSAPP (Z-API)
# -------------------------------------------------------------
ZAPI_INSTANCIA_ID = "3FB52DB5B70E81949D77864B3974BD33"
ZAPI_TOKEN = "AD222D0ACC6E6A3A397283E8"
ZAPI_CLIENT_TOKEN = "F2c44689be83c415aabb62327a3bdbe64S"


def disparar_notificacao_whatsapp(pedido):
    """
    Envia a notificação do pedido diretamente para o WhatsApp do restaurante
    via Z-API com autenticação via Client-Token no cabeçalho.
    """
    numero_raw = str(pedido.restaurante.whatsapp or "")
    apenas_digitos = "".join(filter(str.isdigit, numero_raw))

    if apenas_digitos.startswith("55"):
        numero_destino = apenas_digitos
    elif len(apenas_digitos) in [10, 11]:
        numero_destino = f"55{apenas_digitos}"
    else:
        numero_destino = apenas_digitos

    if not numero_destino:
        print("[WhatsApp] Restaurante sem número de WhatsApp cadastrado.")
        return

    # Formatação dos itens do pedido
    linhas_itens = []
    for item in pedido.itens.all():
        linhas_itens.append(f"• {item.quantidade}x {item.produto.nome} - R$ {item.subtotal:.2f}")
    itens_formatados = "\n".join(linhas_itens)

    # Mensagem formatada
    texto_mensagem = (
        f"🍔 *NOVO PEDIDO RECEBIDO #{pedido.id}*\n"
        f"--------------------------------\n"
        f"*Cliente:* {pedido.cliente_nome}\n"
        f"*Telefone:* {pedido.cliente_telefone}\n"
        f"*Endereço:* {pedido.endereco_entrega}\n"
    )

    if pedido.ponto_referencia:
        texto_mensagem += f"*Ponto de Ref.:* {pedido.ponto_referencia}\n"

    texto_mensagem += (
        f"--------------------------------\n"
        f"*Itens Solicitados:*\n"
        f"{itens_formatados}\n"
        f"--------------------------------\n"
        f"*Pagamento:* {pedido.get_forma_pagamento_display()}\n"
    )

    if pedido.troco_para:
        texto_mensagem += f"*Troco para:* R$ {pedido.troco_para:.2f}\n"

    if pedido.observacoes:
        texto_mensagem += f"*Observações:* {pedido.observacoes}\n"

    texto_mensagem += (
        f"--------------------------------\n"
        f"💰 *Total a Cobrar: R$ {pedido.total:.2f}*"
    )

    endpoint_url = f"https://api.z-api.io/instances/{ZAPI_INSTANCIA_ID}/token/{ZAPI_TOKEN}/send-text"
    headers = {
        "Client-Token": ZAPI_CLIENT_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "phone": numero_destino,
        "message": texto_mensagem
    }

    try:
        resposta = requests.post(endpoint_url, json=payload, headers=headers, timeout=10)
        if resposta.status_code == 200:
            print(f"[WhatsApp] Pedido #{pedido.id} enviado com sucesso para {numero_destino}!")
        else:
            print(f"[WhatsApp] Falha ao enviar pedido #{pedido.id}: {resposta.status_code} - {resposta.text}")
    except Exception as erro:
        print(f"[WhatsApp] Erro de conexão ao enviar pedido #{pedido.id}: {erro}")


# -------------------------------------------------------------
# 1. NAVEGAÇÃO E CATÁLOGO MULTI-TENANT
# -------------------------------------------------------------
def cardapio_view(request, restaurante_slug):
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, ativo=True)
    categorias = Categoria.objects.filter(restaurante=restaurante).prefetch_related('produtos')
    carrinho = Carrinho(request)
    return render(request, 'delivery/cardapio.html', {
        'restaurante': restaurante,
        'categorias': categorias,
        'carrinho': carrinho,
    })


def produto_detalhe_view(request, restaurante_slug, produto_id):
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, ativo=True)
    produto = get_object_or_404(Produto, id=produto_id, restaurante=restaurante)
    carrinho = Carrinho(request)
    return render(request, 'delivery/produto_detalhe.html', {
        'restaurante': restaurante,
        'produto': produto,
        'carrinho': carrinho,
    })


# -------------------------------------------------------------
# 2. GESTÃO DE PRODUTOS E CATEGORIAS (LOJISTA)
# -------------------------------------------------------------
@login_required
def produto_criar_view(request, restaurante_slug):
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, dono=request.user)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.restaurante = restaurante
            produto.save()
            return redirect('cardapio', restaurante_slug=restaurante.slug)
    else:
        form = ProdutoForm()
        form.fields['categoria'].queryset = Categoria.objects.filter(restaurante=restaurante)

    return render(request, 'delivery/produto_form.html', {
        'form': form,
        'restaurante': restaurante,
        'titulo': 'Novo Produto'
    })


@login_required
def produto_editar_view(request, restaurante_slug, produto_id):
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, dono=request.user)
    produto = get_object_or_404(Produto, id=produto_id, restaurante=restaurante)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('produto_detalhe', restaurante_slug=restaurante.slug, produto_id=produto.id)
    else:
        form = ProdutoForm(instance=produto)
        form.fields['categoria'].queryset = Categoria.objects.filter(restaurante=restaurante)

    return render(request, 'delivery/produto_form.html', {
        'form': form,
        'restaurante': restaurante,
        'titulo': 'Editar Produto',
        'produto': produto
    })


@login_required
def produto_excluir_view(request, restaurante_slug, produto_id):
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, dono=request.user)
    produto = get_object_or_404(Produto, id=produto_id, restaurante=restaurante)
    if request.method == 'POST':
        produto.delete()
        return redirect('cardapio', restaurante_slug=restaurante.slug)
    return render(request, 'delivery/produto_confirmar_exclusao.html', {
        'restaurante': restaurante,
        'produto': produto
    })


@login_required
@require_POST
def categoria_criar_api(request, restaurante_slug):
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, dono=request.user)
    try:
        dados = json.loads(request.body)
        nome = dados.get('nome', '').strip()
        ordem = dados.get('ordem', 0)
        
        if not nome:
            return JsonResponse({'sucesso': False, 'erro': 'O nome da categoria é obrigatório.'}, status=400)

        categoria = Categoria.objects.create(
            restaurante=restaurante,
            nome=nome,
            ordem=ordem if ordem else 0
        )
        return JsonResponse({
            'sucesso': True,
            'id': categoria.id,
            'nome': categoria.nome
        })
    except Exception as e:
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=500)


# -------------------------------------------------------------
# 3. GESTÃO DO CARRINHO
# -------------------------------------------------------------
def adicionar_carrinho_view(request, restaurante_slug, produto_id):
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, ativo=True)
    if not restaurante.esta_aberto:
        return redirect('cardapio', restaurante_slug=restaurante.slug)

    get_object_or_404(Produto, id=produto_id, restaurante=restaurante)
    carrinho = Carrinho(request)
    carrinho.adicionar(produto_id=produto_id)
    if 'carrinho' in request.META.get('HTTP_REFERER', ''):
        return redirect('ver_carrinho', restaurante_slug=restaurante.slug)
    return redirect('cardapio', restaurante_slug=restaurante.slug)


def diminuir_carrinho_view(request, restaurante_slug, produto_id):
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, ativo=True)
    carrinho = Carrinho(request)
    carrinho.diminuir(produto_id=produto_id)
    return redirect('ver_carrinho', restaurante_slug=restaurante.slug)


def remover_carrinho_view(request, restaurante_slug, produto_id):
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, ativo=True)
    carrinho = Carrinho(request)
    carrinho.remover(produto_id=produto_id)
    return redirect('ver_carrinho', restaurante_slug=restaurante.slug)


def ver_carrinho_view(request, restaurante_slug):
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, ativo=True)
    carrinho = Carrinho(request)
    return render(request, 'delivery/carrinho.html', {
        'restaurante': restaurante,
        'carrinho': carrinho
    })


# -------------------------------------------------------------
# 4. FINALIZAÇÃO DO PEDIDO
# -------------------------------------------------------------
def finalizar_pedido_view(request, restaurante_slug):
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, ativo=True)
    if not restaurante.esta_aberto:
        return redirect('cardapio', restaurante_slug=restaurante.slug)

    carrinho = Carrinho(request)
    if len(carrinho) == 0:
        return redirect('cardapio', restaurante_slug=restaurante.slug)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.restaurante = restaurante
            pedido.save()

            for item in carrinho:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=item['produto'],
                    quantidade=item['quantidade'],
                    preco_unitario=item['preco'],
                )

            carrinho.limpar()

            # Disparo automático via Z-API com Client-Token configurado
            disparar_notificacao_whatsapp(pedido)

            return redirect('pedido_concluido', restaurante_slug=restaurante.slug, pedido_id=pedido.id)
    else:
        form = CheckoutForm()

    return render(request, 'delivery/finalizar_pedido.html', {
        'restaurante': restaurante,
        'form': form,
        'carrinho': carrinho,
    })


def pedido_concluido_view(request, restaurante_slug, pedido_id):
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, ativo=True)
    pedido = get_object_or_404(Pedido, id=pedido_id, restaurante=restaurante)

    return render(request, 'delivery/pedido_concluido.html', {
        'restaurante': restaurante,
        'pedido': pedido,
    })


# -------------------------------------------------------------
# 5. AUTENTICAÇÃO E CADASTRO
# -------------------------------------------------------------
def cadastro(request):
    if request.user.is_authenticated:
        return redirect('admin:index')

    if request.method == 'POST':
        form = CadastroComEmailForm(request.POST)
        if form.is_valid():
            user = form.save()

            emailjs_url = 'https://api.emailjs.com/api/v1.0/email/send'
            payload = {
                'service_id': 'SEU_SERVICE_ID',
                'template_id': 'SEU_TEMPLATE_ID',
                'user_id': 'SUA_PUBLIC_KEY',
                'accessToken': 'SUA_PRIVATE_KEY',
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

            login(request, user)
            return redirect('admin:index')
    else:
        form = CadastroComEmailForm()

    return render(request, 'delivery/registration/cadastro.html', {'form': form})


# -------------------------------------------------------------
# 6. OPERACIONAL DA LOJA (LIGA/DESLIGA)
# -------------------------------------------------------------
@login_required
@require_POST
def alternar_status_loja(request, restaurante_slug):
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug, dono=request.user)
    restaurante.aberto_manual = not restaurante.aberto_manual
    restaurante.save()
    return redirect('cardapio', restaurante_slug=restaurante.slug)