from django import forms
from .models import Pedido, Produto


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'cliente_nome',
            'cliente_telefone',
            'endereco_entrega',
            'ponto_referencia',
            'forma_pagamento',
            'troco_para',
            'observacoes',
        ]
        widgets = {
            'cliente_nome': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': 'Ex: João Silva'
            }),
            'cliente_telefone': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': 'Ex: (11) 98765-4321'
            }),
            'endereco_entrega': forms.Textarea(attrs={
                'class': 'form-control rounded-3',
                'rows': 2,
                'placeholder': 'Rua, número, bairro e complemento'
            }),
            'ponto_referencia': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': 'Ex: Próximo à padaria'
            }),
            'forma_pagamento': forms.Select(attrs={
                'class': 'form-select rounded-3'
            }),
            'troco_para': forms.NumberInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': 'Ex: 50.00 (se precisar de troco)',
                'step': '0.01'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control rounded-3',
                'rows': 2,
                'placeholder': 'Ex: sem cebola, maionese à parte'
            }),
        }


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['categoria', 'nome', 'descricao', 'preco', 'imagem', 'disponivel']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select rounded-3'}),
            'nome': forms.TextInput(attrs={'class': 'form-control rounded-3'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control rounded-3', 'rows': 3}),
            'preco': forms.NumberInput(attrs={'class': 'form-control rounded-3', 'step': '0.01'}),
            'imagem': forms.FileInput(attrs={'class': 'form-control rounded-3'}),
            'disponivel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }