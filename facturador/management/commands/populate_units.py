from django.core.management.base import BaseCommand
from facturador.models import Unit

class Command(BaseCommand):
    help = 'Popula la base de datos con unidades predeterminadas'

    def handle(self, *args, **kwargs):
        unit_data = [
            {'key': 'H87', 'name': 'Pieza', '_type': 'Unidad de Medida'},
            {'key': 'EA', 'name': 'Elemento', '_type': 'Unidad de Medida'},
            {'key': 'E48', 'name': 'Unidad de Servicio', '_type': 'Unidad de Servicio'},
            {'key': 'ACT', 'name': 'Actividad', '_type': 'Tipo de Actividad'},
            {'key': 'KGM', 'name': 'Kilogramo', '_type': 'Peso'},
            {'key': 'E51', 'name': 'Trabajo', '_type': 'Tipo de Actividad'},
            {'key': 'A9', 'name': 'Tarifa', '_type': 'Unidad de Medida'},
            {'key': 'MTR', 'name': 'Metro', '_type': 'Longitud'},
            {'key': 'AB', 'name': 'Paquete a granel', '_type': 'Empaque'},
            {'key': 'BB', 'name': 'Caja base', '_type': 'Empaque'},
            {'key': 'KT', 'name': 'Kit', '_type': 'Conjunto'},
            {'key': 'SET', 'name': 'Conjunto', '_type': 'Conjunto'},
            {'key': 'LTR', 'name': 'Litro', '_type': 'Volumen'},
            {'key': 'XBX', 'name': 'Caja', '_type': 'Empaque'},
            {'key': 'MON', 'name': 'Mes', '_type': 'Tiempo'},
            {'key': 'HUR', 'name': 'Hora', '_type': 'Tiempo'},
            {'key': 'MTK', 'name': 'Metro cuadrado', '_type': 'Área'},
            {'key': '11', 'name': 'Equipos', '_type': 'Conjunto'},
            {'key': 'MGM', 'name': 'Miligramo', '_type': 'Peso'},
            {'key': 'XPK', 'name': 'Paquete', '_type': 'Empaque'},
            {'key': 'XKI', 'name': 'Kit (Conjunto de piezas)', '_type': 'Conjunto'},
            {'key': 'AS', 'name': 'Variedad', '_type': 'Tipo'},
            {'key': 'GRM', 'name': 'Gramo', '_type': 'Peso'},
            {'key': 'PR', 'name': 'Par', '_type': 'Unidad de Medida'},
            {'key': 'DPC', 'name': 'Docenas de piezas', '_type': 'Cantidad'},
            {'key': 'xun', 'name': 'Unidad', '_type': 'Unidad de Medida'},
            {'key': 'DAY', 'name': 'Día', '_type': 'Tiempo'},
            {'key': 'XLT', 'name': 'Lote', '_type': 'Cantidad'},
            {'key': '10', 'name': 'Grupos', '_type': 'Conjunto'},
            {'key': 'MLT', 'name': 'Mililitro', '_type': 'Volumen'},
            {'key': 'E54', 'name': 'Viaje', '_type': 'Unidad de Servicio'},
        ]

        for unit in unit_data:
            obj, created = Unit.objects.get_or_create(
                key=unit['key'],
                defaults={
                    'name': unit['name'],
                    '_type': unit['_type'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Unidad '{unit['key']}' creada."))
            else:
                self.stdout.write(f"Unidad '{unit['key']}' ya existe.")
