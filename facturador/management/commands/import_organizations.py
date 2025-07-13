import json
from django.core.management.base import BaseCommand
from facturador.models import Organization
from datetime import datetime

class Command(BaseCommand):
    help = 'Imports organizations from a JSON string'

    def handle(self, *args, **kwargs):
        # JSON data containing the organizations
        json_data = '''{
            "page": 1,
            "total_pages": 1,
            "total_results": 6,
            "data": [
                {
                    "id": "65556b1c2314cc3933ebea0a",
                    "created_at": "2023-11-16T01:06:36.647Z",
                    "is_production_ready": false,
                    "pending_steps": [
                        {"type": "legal", "description": "Introduce tus datos fiscales"},
                        {"type": "certificate", "description": "Sube tu Certificado de Sello Digital (CSD)"}
                    ],
                    "logo_url": "https://storage.googleapis.com/cdn.facturapi.io/organization/ee3b01c7458f001840e1680ca65ba85635661334/logo.jpg",
                    "timezone": "America_Mexico_City",
                    "legal": {
                        "name": "Borbolla Group",
                        "legal_name": "BORBOLLA GROUP",
                        "tax_id": "XIA190128J61",
                        "tax_system": "601",
                        "address": {
                            "street": "",
                            "exterior": "",
                            "interior": "",
                            "neighborhood": "",
                            "city": "",
                            "municipality": "",
                            "state": "",
                            "country": "MEX",
                            "zip": "06010"
                        }
                    },
                    "customization": {
                        "color": "75A4FF",
                        "next_folio_number": 1,
                        "next_folio_number_test": 1,
                        "has_logo": true
                    },
                    "certificate": {
                        "has_certificate": false,
                        "updated_at": null,
                        "expires_at": null
                    }
                },
                {
                    "id": "64abb04657124fc31ed8e2eb",
                    "created_at": "2023-07-10T07:16:22.592Z",
                    "is_production_ready": true,
                    "pending_steps": [],
                    "logo_url": "https://storage.googleapis.com/cdn.facturapi.io/organization/cf0ba927e0b4ad45721bd447958d0613a3a5c805/logo.jpg",
                    "domain": "boxcontainerpark",
                    "timezone": "America_Mexico_City",
                    "legal": {
                        "name": "OMICRON INGENIERIA Y EQUIPOS",
                        "legal_name": "OMICRON INGENIERIA Y EQUIPOS",
                        "tax_id": "OIE2011131K0",
                        "tax_system": "601",
                        "address": {
                            "street": "PEREZ TREVIÑO",
                            "exterior": "142",
                            "interior": "A",
                            "neighborhood": "CENTRO",
                            "city": "SALTILLO",
                            "municipality": "SALTILLO",
                            "state": "Coahuila de Zaragoza",
                            "country": "MEX",
                            "zip": "25000"
                        }
                    },
                    "customization": {
                        "color": "F7971E",
                        "next_folio_number": 66513,
                        "next_folio_number_test": 59,
                        "has_logo": true
                    },
                    "certificate": {
                        "has_certificate": true,
                        "updated_at": "2023-07-10T15:27:38.783Z",
                        "expires_at": "2025-01-27T05:07:32.000Z",
                        "serial_number": "00001000000506262169"
                    }
                },
                {
                    "id": "64357ebb84d0212f1fb2076c",
                    "created_at": "2023-04-11T15:37:31.065Z",
                    "is_production_ready": true,
                    "pending_steps": [],
                    "logo_url": "https://storage.googleapis.com/cdn.facturapi.io/organization/d4575890de0c1cb6b3189acdd8a5d05febef35fe/logo.jpg",
                    "domain": "bode",
                    "timezone": "America_Mexico_City",
                    "legal": {
                        "name": "PROYECTOS BODE",
                        "legal_name": "PROYECTOS BODE",
                        "tax_id": "PBO180817PQ2",
                        "tax_system": "601",
                        "address": {
                            "street": "FERMIN ESPINOZA ARMILLITA",
                            "exterior": "1000",
                            "interior": "",
                            "neighborhood": "TOPO CHICO",
                            "city": "SALTILLO",
                            "municipality": "SALTILLO",
                            "state": "Coahuila de Zaragoza",
                            "country": "MEX",
                            "zip": "25248"
                        }
                    },
                    "customization": {
                        "color": "75A4FF",
                        "next_folio_number": 759091,
                        "next_folio_number_test": 2,
                        "has_logo": true
                    },
                    "certificate": {
                        "has_certificate": true,
                        "updated_at": "2023-04-11T15:58:36.524Z",
                        "expires_at": "2026-08-24T22:31:27.000Z",
                        "serial_number": "00001000000514729780"
                    }
                },
                {
                    "id": "604408b654911d002d4f063d",
                    "created_at": "2021-03-06T22:56:54.411Z",
                    "is_production_ready": true,
                    "pending_steps": [],
                    "logo_url": "https://storage.googleapis.com/cdn.facturapi.io/organization/3bcd312e1f7db0599fcea9dcb02ee72bd4cf6b26/logo.jpg",
                    "timezone": "America_Mexico_City",
                    "legal": {
                        "name": "OMICRON",
                        "legal_name": "OMICRON INGENIERIA Y EQUIPOS SAPI DE CV",
                        "tax_id": "OIE2011131K0",
                        "tax_system": "601",
                        "address": {
                            "street": "Perez Trevino",
                            "exterior": "142-a",
                            "interior": "",
                            "neighborhood": "centro",
                            "city": "Saltillo",
                            "municipality": "Saltillo",
                            "state": "Coahuila de Zaragoza",
                            "country": "MEX",
                            "zip": "25000"
                        }
                    },
                    "customization": {
                        "color": "F99320",
                        "next_folio_number": 7683,
                        "next_folio_number_test": 1,
                        "has_logo": true
                    },
                    "certificate": {
                        "has_certificate": true,
                        "updated_at": "2021-03-06T23:12:18.131Z",
                        "expires_at": "2025-01-27T05:07:32.000Z",
                        "serial_number": "00001000000506262169"
                    }
                },
                {
                    "id": "5e73bb8833fb370029a233f9",
                    "created_at": "2020-03-19T18:35:52.073Z",
                    "is_production_ready": true,
                    "pending_steps": [],
                    "logo_url": "https://storage.googleapis.com/cdn.facturapi.io/organization/d61da980dfc9175290fd9db78d37d2ed745b38d8/logo.jpg",
                    "timezone": "America_Mexico_City",
                    "legal": {
                        "name": "BORBOLLA METROLOGY",
                        "legal_name": "BORBOLLA METROLOGY S.A. DE C.V.",
                        "tax_id": "BME030613553",
                        "tax_system": "601",
                        "address": {
                            "street": "HIDALGO NORTE",
                            "exterior": "448",
                            "interior": "",
                            "neighborhood": "Zona Centro",
                            "city": "Saltillo",
                            "municipality": "Saltillo",
                            "state": "Coahuila de Zaragoza",
                            "country": "MEX",
                            "zip": "25000"
                        }
                    },
                    "customization": {
                        "color": "FB863F",
                        "next_folio_number": 10165,
                        "next_folio_number_test": 55088,
                        "has_logo": true
                    },
                    "certificate": {
                        "has_certificate": true,
                        "updated_at": "2020-12-08T23:27:47.708Z",
                        "expires_at": "2024-12-04T17:11:55.000Z",
                        "serial_number": "00001000000505921318"
                    }
                },
                {
                    "id": "5e5f1f0c4aee605ab94d17b1",
                    "created_at": "2020-03-04T03:22:52.182Z",
                    "is_production_ready": true,
                    "pending_steps": [],
                    "logo_url": "https://storage.googleapis.com/cdn.facturapi.io/organization/121649b2dbf47b6e2901baa655d169b7a0c68094/logo.jpg",
                    "domain": "borbolla",
                    "timezone": "America_Mexico_City",
                    "legal": {
                        "name": "Borbolla Automation Inc",
                        "legal_name": "PROYECTOS BODE",
                        "tax_id": "PBO180817PQ2",
                        "tax_system": "601",
                        "address": {
                            "street": "FERMIN ESPINOZA ARMILLITA",
                            "exterior": "1000",
                            "interior": "",
                            "neighborhood": "TOPO CHICO",
                            "city": "Saltillo",
                            "municipality": "Saltillo",
                            "state": "Coahuila de Zaragoza",
                            "country": "MEX",
                            "zip": "25284"
                        }
                    },
                    "customization": {
                        "color": "818899",
                        "next_folio_number": 11429,
                        "next_folio_number_test": 121,
                        "has_logo": true
                    },
                    "certificate": {
                        "has_certificate": true,
                        "updated_at": "2022-08-26T17:25:41.344Z",
                        "expires_at": "2026-08-24T22:31:27.000Z",
                        "serial_number": "00001000000514729780"
                    }
                }
            ]
        }'''

        # Load the JSON data
        data = json.loads(json_data)

        # Loop through the organizations and create or update the records
        for org_data in data['data']:
            legal_data = org_data['legal']
            address_data = legal_data['address']

            # Parse dates if they exist
            created_at = datetime.fromisoformat(org_data['created_at'].replace('Z', '+00:00'))
            certificate_expires_at = datetime.fromisoformat(org_data['certificate']['expires_at'].replace('Z', '+00:00')) if org_data['certificate']['expires_at'] else None
            certificate_updated_at = datetime.fromisoformat(org_data['certificate']['updated_at'].replace('Z', '+00:00')) if org_data['certificate']['updated_at'] else None

            organization, created = Organization.objects.update_or_create(
                organization_id=org_data['id'],
                defaults={
                    'name': legal_data['name'],
                    'legal_name': legal_data['legal_name'],
                    'tax_id': legal_data['tax_id'],
                    'tax_system': legal_data['tax_system'],
                    'website': legal_data.get('website', ''),
                    'phone': legal_data.get('phone', ''),
                    'street': address_data.get('street', ''),
                    'exterior': address_data.get('exterior', ''),
                    'interior': address_data.get('interior', ''),
                    'neighborhood': address_data.get('neighborhood', ''),
                    'city': address_data.get('city', ''),
                    'municipality': address_data.get('municipality', ''),
                    'state': address_data.get('state', ''),
                    'country': address_data.get('country', ''),
                    'zip_code': address_data.get('zip', ''),
                    'is_production_ready': org_data['is_production_ready'],
                    'pending_steps': org_data.get('pending_steps', []),
                    'has_logo': org_data['customization'].get('has_logo', False),
                    'color': org_data['customization'].get('color', ''),
                    'next_folio_number': org_data['customization'].get('next_folio_number', 1),
                    'next_folio_number_test': org_data['customization'].get('next_folio_number_test', 1),
                    'certificate_expires_at': certificate_expires_at,
                    'certificate_updated_at': certificate_updated_at,
                    'created_at': created_at,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Organization {organization.legal_name} created successfully.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Organization {organization.legal_name} updated successfully.'))
