from decimal import Decimal
from .models import Produto

class Carrinho:
    def __init__(self, request):
        self.session = request.session
        carrinho = self.session.get('carrinho')
        if not carrinho:
            carrinho = self.session['carrinho'] = {}
        self.carrinho = carrinho

    def adicionar(self, produto_id):
        produto_id = str(produto_id)
        if produto_id not in self.carrinho:
            self.carrinho[produto_id] = {'quantidade': 0}
        self.carrinho[produto_id]['quantidade'] += 1
        self.salvar()

    def remover(self, produto_id):
        produto_id = str(produto_id)
        if produto_id in self.carrinho:
            del self.carrinho[produto_id]
            self.salvar()

    def salvar(self):
        self.session.modified = True

    def __iter__(self):
        produtos_ids = self.carrinho.keys()
        produtos = Produto.objects.filter(id__in=produtos_ids)
        carrinho_dict = self.carrinho.copy()

        for produto in produtos:
            carrinho_dict[str(produto.id)]['produto'] = produto

        for item in carrinho_dict.values():
            if 'produto' in item:
                item['preco'] = item['produto'].preco
                item['subtotal'] = item['preco'] * item['quantidade']
                yield item

    def get_total_preco(self):
        total = Decimal('0.00')
        for item in self:
            total += item['subtotal']
        return total

    def __len__(self):
        return sum(item['quantidade'] for item in self.carrinho.values())

    def limpar(self):
        del self.session['carrinho']
        self.salvar()