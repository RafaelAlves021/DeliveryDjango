from decimal import Decimal
from .models import Produto

class Carrinho:
    def __init__(self, request):
        self.session = request.session
        carrinho = self.session.get('carrinho')
        if not carrinho:
            carrinho = self.session['carrinho'] = {}
        self.carrinho = carrinho

    def adicionar(self, produto_id, quantidade=1):
        produto_id = str(produto_id)
        if produto_id not in self.carrinho:
            try:
                produto = Produto.objects.get(id=int(produto_id))
                self.carrinho[produto_id] = {
                    'quantidade': 0,
                    'preco': str(produto.preco)
                }
            except Produto.DoesNotExist:
                return

        self.carrinho[produto_id]['quantidade'] += quantidade
        self.salvar()

    def diminuir(self, produto_id):
        produto_id = str(produto_id)
        if produto_id in self.carrinho:
            self.carrinho[produto_id]['quantidade'] -= 1
            if self.carrinho[produto_id]['quantidade'] <= 0:
                del self.carrinho[produto_id]
            self.salvar()

    def remover(self, produto_id):
        produto_id = str(produto_id)
        if produto_id in self.carrinho:
            del self.carrinho[produto_id]
            self.salvar()

    def salvar(self):
        self.session.modified = True

    def __iter__(self):
        produto_ids = list(self.carrinho.keys())
        produtos = Produto.objects.filter(id__in=produto_ids)
        carrinho = self.carrinho.copy()

        for produto in produtos:
            carrinho[str(produto.id)]['produto'] = produto

        for item in carrinho.values():
            if 'produto' in item and 'preco' in item:
                item['preco'] = Decimal(str(item['preco']))
                item['total_preco'] = item['preco'] * item['quantidade']
                yield item

    def __len__(self):
        return sum(item.get('quantidade', 0) for item in self.carrinho.values())

    def get_total_preco(self):
        total = Decimal('0.00')
        for item in self.carrinho.values():
            preco = item.get('preco')
            qtd = item.get('quantidade', 0)
            if preco is not None:
                total += Decimal(str(preco)) * qtd
        return total

    def limpar(self):
        if 'carrinho' in self.session:
            del self.session['carrinho']
        self.salvar()

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