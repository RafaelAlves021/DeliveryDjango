from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Restaurante(models.Model):
    dono = models.ForeignKey(User, on_delete=models.CASCADE, related_name="restaurantes")
    nome = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True, help_text="Identificador único na URL (ex: burguer-co)")
    whatsapp = models.CharField(max_length=20, help_text="WhatsApp do restaurante com DDD (ex: 5511999999999)")
    endereco = models.CharField(max_length=255, blank=True, help_text="Endereço físico do estabelecimento")
    logo = models.ImageField(upload_to="restaurantes/logos/", blank=True, null=True)
    ativo = models.BooleanField(default=True, help_text="Define se o cardápio está visível para clientes")
    criado_em = models.DateTimeField(auto_now_add=True)

    # Campos comerciais dinâmicos (liga/desliga e estimativas)
    aberto_manual = models.BooleanField(
        default=True, 
        verbose_name="Recebendo Pedidos Agora"
    )
    tempo_estimado = models.CharField(
        max_length=50, 
        default="30-50 min", 
        verbose_name="Tempo Estimado de Entrega"
    )
    area_entrega = models.CharField(
        max_length=120, 
        default="Entrega para toda a região", 
        verbose_name="Texto de Entrega/Frete"
    )

    class Meta:
        verbose_name = "Restaurante"
        verbose_name_plural = "Restaurantes"
        ordering = ['nome']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    @property
    def esta_aberto(self):
        return self.aberto_manual and self.ativo

    def __str__(self):
        return self.nome


class Categoria(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name="categorias")
    nome = models.CharField(max_length=100)
    ordem = models.PositiveIntegerField(default=0, help_text="Ordem de exibição no cardápio")

    class Meta:
        verbose_name_plural = "Categorias"
        ordering = ['ordem', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.restaurante.nome})"


class Produto(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name="produtos")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="produtos")
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True, help_text="Ingredientes e detalhes")
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    imagem = models.ImageField(upload_to="produtos/", blank=True, null=True)
    disponivel = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Produtos"

    def __str__(self):
        return f"{self.nome} - {self.restaurante.nome}"


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('RECEBIDO', 'Recebido'),
        ('PREPARO', 'Em Preparo'),
        ('ENTREGA', 'Saiu para Entrega'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]

    PAGAMENTO_CHOICES = [
        ('DINHEIRO', 'Dinheiro na Entrega'),
        ('CARTAO', 'Cartão na Entrega'),
        ('PIX', 'Pix na Entrega'),
    ]

    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name="pedidos")
    cliente_nome = models.CharField(max_length=100)
    cliente_telefone = models.CharField(max_length=20, help_text="WhatsApp do cliente")
    endereco_entrega = models.TextField(help_text="Rua, número, bairro e complemento")
    ponto_referencia = models.CharField(max_length=150, blank=True)
    
    forma_pagamento = models.CharField(max_length=20, choices=PAGAMENTO_CHOICES, default='PIX')
    troco_para = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RECEBIDO')
    observacoes = models.TextField(blank=True, help_text="Ex: tirar cebola, maionese à parte")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.id} - {self.restaurante.nome} ({self.cliente_nome})"

    @property
    def total(self):
        return sum(item.subtotal for item in self.itens.all())


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name_plural = "Itens dos Pedidos"

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"