from django.db import models

class Recibido(models.Model):
    fecha = models.DateTimeField()
    estado = models.CharField(max_length=100)
    fecha_cancelacion = models.DateTimeField(null=True, blank=True)
    rfc_emisor = models.CharField(max_length=20)
    razon_social_emisor = models.CharField(max_length=255)
    rfc_receptor = models.CharField(max_length=20)
    razon_social_receptor = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=15, decimal_places=2)
    proceso = models.CharField(max_length=255, null=True, blank=True)
    responsable = models.CharField(max_length=255, null=True, blank=True)
    referencia = models.CharField(max_length=255, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    uuid = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.razon_social_emisor} -> {self.razon_social_receptor} | {self.total}"

class Emitido(models.Model):
    fecha_comprobante = models.DateField()
    tipo_comprobante = models.CharField(max_length=100)
    serie = models.CharField(max_length=10, null=True, blank=True)
    folio = models.CharField(max_length=50, null=True, blank=True)
    rfc_receptor = models.CharField(max_length=20)
    nombre_receptor = models.CharField(max_length=255)
    regimen_fiscal = models.CharField(max_length=50)
    moneda = models.CharField(max_length=10)
    tipo_cambio = models.DecimalField(max_digits=10, decimal_places=4)
    total = models.DecimalField(max_digits=15, decimal_places=2)
    metodo_pago = models.CharField(max_length=50)
    estado_cancelacion = models.CharField(max_length=100, null=True, blank=True)
    fecha_cancelacion = models.DateTimeField(null=True, blank=True)
    guid = models.CharField(max_length=255, unique=True)
    tipo_documento = models.CharField(max_length=50, null=True, blank=True)
    version_comprobante = models.CharField(max_length=50)
    estatus_pagado = models.CharField(max_length=50, null=True, blank=True)
    tipo_comprobante_codigo = models.CharField(max_length=10, null=True, blank=True)
    id_pago = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre_receptor} | {self.total}"
