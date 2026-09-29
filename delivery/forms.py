from django import forms
from .models import Pedido
from .models import Produto

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'cliente_nome',
            'cliente_telefone',
            'endereco_entrega',
            'ponto_referencia',
            'observacoes',
        ]
        widgets = {
            'cliente_nome': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-red-500 focus:outline-none text-sm',
                'placeholder': 'O teu nome completo'
            }),
            'cliente_telefone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-red-500 focus:outline-none text-sm',
                'placeholder': '(DDD) 99999-9999'
            }),
            'endereco_entrega': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-red-500 focus:outline-none text-sm',
                'rows': 2,
                'placeholder': 'Rua, número, complemento e bairro'
            }),
            'ponto_referencia': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-red-500 focus:outline-none text-sm',
                'placeholder': 'Ex: Próximo à farmácia'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-red-500 focus:outline-none text-sm',
                'rows': 2,
                'placeholder': 'Ex: Tirar cebola, campainha avariada'
            }),
        }


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['categoria', 'nome', 'descricao', 'preco', 'imagem', 'disponivel']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-300 focus:ring-2 focus:ring-red-500 focus:outline-none text-sm'}),
            'nome': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-300 focus:ring-2 focus:ring-red-500 focus:outline-none text-sm', 'placeholder': 'Nome do produto'}),
            'descricao': forms.Textarea(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-300 focus:ring-2 focus:ring-red-500 focus:outline-none text-sm', 'rows': 3, 'placeholder': 'Ingredientes e detalhes'}),
            'preco': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-300 focus:ring-2 focus:ring-red-500 focus:outline-none text-sm', 'step': '0.01'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'w-full text-sm text-zinc-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-red-50 file:text-red-700 hover:file:bg-red-100'}),
            'disponivel': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-red-600 rounded border-zinc-300 focus:ring-red-500'}),
        }