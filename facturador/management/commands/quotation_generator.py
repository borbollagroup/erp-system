import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph , Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT , TA_LEFT
from datetime import datetime
from math import ceil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

PROJECT_DESCRIPTION = "Miscelaneous project"
AIRTABLE_PAT = "patAjmvQu5IDRy0sJ.f3ecfdc5382d48738024c5a87cb01d069f968894fa43e1e9c37896a5efac7d6f"

data = ""
#with open("/home/borbolla/borbolla_webpage/quotation_records.json", "r") as f:
#    data = json.load(f)

basedir = "/home/borbolla/borbolla_webpage/facturador/management/commands/"

# Register fonts for the document
pdfmetrics.registerFont(TTFont('Inconsolata-Regular', basedir+'Inconsolata/static/Inconsolata-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Inconsolata-Bold', basedir+'Inconsolata/static/Inconsolata-Bold.ttf'))

style_title = ParagraphStyle(name="normal", fontSize=22, fontName="Inconsolata-Bold", alignment=TA_CENTER ,)
style_normal = ParagraphStyle(name="normal", fontSize=8, fontName="Inconsolata-Regular", alignment=TA_CENTER)
style_subtotals = ParagraphStyle(name="subtotals", fontSize=10, fontName="Inconsolata-Bold", alignment=TA_CENTER)
style_bold = ParagraphStyle(name="bold", fontSize=10, fontName="Inconsolata-Bold", alignment=TA_CENTER,textColor=colors.white  )

import requests


def get_latest_folio_and_quotation_number(api_key, base_id="appwi0zWjNflrLdjM", table_id="tbljvTFH9DnvNntXb"):
    """
    Fetches the latest folio and quotation number from the specified Airtable table
    and returns the next incremented values.

    :param api_key: str - Your Airtable API key.
    :param base_id: str - The Airtable Base ID.
    :param table_id: str - The Airtable Table ID.
    :return: tuple - The next available folio number and quotation number.
    """
    url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    # Request parameters to sort by `header__folio` and `project_info__quotation_number` in descending order
    params = {
        "sort[0][field]": "header__folio",
        "sort[0][direction]": "desc",
        "sort[1][field]": "project_info__quotation_number",
        "sort[1][direction]": "desc",
        "maxRecords": 1  # Only the latest record is needed
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Retrieve the latest folio and quotation number if records exist
        if 'records' in data and data['records']:
            latest_folio = int(data['records'][0]['fields'].get("header__folio", 0))
            latest_quotation = data['records'][0]['fields'].get("project_info__quotation_number", "Q-0")
            
            # Increment the folio
            next_folio = latest_folio + 1
            
            # Increment the quotation number by extracting the number part
            latest_quotation_number = int(latest_quotation.split('-')[1])
            next_quotation = f"Q-{latest_quotation_number + 1}"
        else:
            # Default to 1 if no records exist
            next_folio = 1
            next_quotation = "Q-1"

        print(f"The next folio number is: {next_folio}")
        print(f"The next quotation number is: {next_quotation}")
        return next_folio, next_quotation

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving data from Airtable: {e}")
        if response.status_code == 422:
            print("Response JSON:", response.json())
        return None, None



# Function to get exchange rate and apply discount
def get_discounted_exchange_rate(base_currency="USD", target_currency="MXN", discount=0.1):
    # API endpoint for exchange rate (replace with your own API or a free API like ExchangeRate-API or Open Exchange Rates)
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"

    try:
        # Get exchange rate data from API
        response = requests.get(url)
        data = response.json()
        
        # Retrieve the exchange rate for the target currency
        exchange_rate = data['rates'][target_currency]
        
        # Calculate discounted rate
        discounted_rate = exchange_rate * (1 - discount)
        
        return discounted_rate
    
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None

# Usage example: Get discounted USD to MXN rate
discounted_rate = get_discounted_exchange_rate("USD", "MXN")
print(f"Discounted USD to MXN exchange rate: {discounted_rate}")


# Format numbers as floats with commas and two decimal places
def format_number(value):
    try:
        return f"{float(value):,.0f}"
    except (ValueError, TypeError):
        print("EXCEPT!",value)
        return value

# Function to check if quantity is 0 or None, return 0 as unit price if true
def check_and_format_price(qty, price):
    if qty == 0 or qty is None:
        return "0"
    else:
        return format_number(price)

# Function to safely convert to float, returning 0 if value is an empty string
# utils.py

def safe_float(value):
    # Remove commas if present to avoid conversion issues
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return 0.0


# Function to calculate totals for overhead
def calculate_overheads(labor_sum, material_sum, equipment_sum):
    management_expense = 0.05 * (labor_sum + material_sum + equipment_sum)
    safety_expense = 0.02 * (labor_sum + material_sum + equipment_sum)
    profit = 0.08 * (labor_sum + material_sum + equipment_sum)
    return management_expense, safety_expense, profit

# Function to generate the PDF with headers, personnel expenses, material costs, and overhead costs


def generate_quotation_pdf(output_file, data):
    doc = SimpleDocTemplate(output_file, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=70, bottomMargin=72)
    story = []

    # Add title (header)
    #title = Paragraph("<b>Quotation Details</b>", style_title)
    #story.append(title)
    

    # Calculate project duration in days
    start_date = datetime.strptime(data['project_info']['project_start'], "%Y-%m-%d")
    end_date = datetime.strptime(data['project_info']['project_end'], "%Y-%m-%d")
    project_duration = (end_date - start_date).days

    # Calculate totals for personnel and materials
    add_header(story , data)
    labor_sum = add_personnel_expenses(story, data, project_duration)
    material_sum = add_materials_with_remarks(story, data)
    
    # Calculate total for equipment
    equipment_sum = add_equipment_with_days_and_units(story, data)

    # Calculate and add overhead costs dynamically
    management_expense, safety_expense, profit = calculate_overheads(labor_sum, material_sum, equipment_sum)
    overhead_sum = add_overhead_costs(story, data, management_expense, safety_expense, profit)
    print("OVERHEAD : ",overhead_sum)
    # Add final totals table with total costs
    totals = add_totals(story, material_sum, labor_sum, overhead_sum,equipment_sum,data)
    print(totals)
    add_closing_table(story)

    # Build the PDF
    doc.build(story, onFirstPage=lambda canvas, doc: add_header_footer(canvas, doc, data), onLaterPages=lambda canvas, doc: add_header_footer(canvas, doc, data))

    return totals

def add_header_footer(canvas, doc, data):
    canvas.saveState()

    # Header - Draw Logo
    try:
        logo_path = "/home/borbolla/borbolla_webpage/facturador/management/commands/logo_group.jpeg"
        canvas.drawImage(logo_path, 36, letter[1] - 50, width=1.5 * inch, height=0.4 * inch)
    except Exception as e:
        print(f"Error loading logo: {e}")

    # Centered Title
    style_centered = ParagraphStyle(name="centered", alignment=TA_CENTER, fontSize=16, fontName="Inconsolata-Bold", textColor=colors.black)
    title = Paragraph("<b>QUOTATION SHEET</b>", style_centered)
    title.wrap(6 * inch, 800)
    title.drawOn(canvas, (letter[0] - 6 * inch) / 2, letter[1] - 60)

    # Folio Number on the Right
    folio_text = f"<b><font color='red'>FOLIO: {data['header']['folio']}</font></b>"
    style_right = ParagraphStyle(name="right", alignment=TA_RIGHT, fontSize=14, fontName="Inconsolata-Bold", textColor=colors.red)
    folio = Paragraph(folio_text, style_right)
    folio.wrap(2 * inch, 800)
    folio.drawOn(canvas, letter[0] - 220, letter[1] - 50)

    canvas.restoreState()
def add_header(story, data):
    style_normal2 = ParagraphStyle(name="normal", fontSize=8, fontName="Inconsolata-Regular", alignment=TA_LEFT)
    style_bold2 = ParagraphStyle(name="bold", fontSize=8, fontName="Inconsolata-Bold", alignment=TA_LEFT , textColor=colors.black)

    # Client Information
    client_info = [
        [Paragraph("<b>CUSTOMER INFORMATION</b>", style_bold2)],
        [Paragraph(f"Customer Name: {data['client_info']['client_name']}", style_normal2)],
        [Paragraph(f"Address: {data['client_info']['address']}", style_normal2)],
        [Paragraph(f"Manager: {data['client_info']['manager']}", style_normal2)],
        [Paragraph(f"Contact: {data['client_info']['contact']}", style_normal2)]
    ]

    # Project Information
    project_info = [
        [Paragraph("<b>PROJECT INFORMATION</b>", style_bold)],
        [Paragraph(f"Quotation #: {data['project_info']['quotation_number']}", style_normal)],
        [Paragraph(f"Quotation Date: {data['project_info']['quotation_date']}", style_normal)],
        [Paragraph(f"Project Name: {data['project_info']['project_name']}", style_normal)],
        [Paragraph(f"Project Start: {data['project_info']['project_start']}", style_normal)],
        [Paragraph(f"Project End: {data['project_info']['project_end']}", style_normal)]
    ]

    financial_info = [
        [Paragraph("<b>FINANCIAL INFORMATION</b>", style_bold)],
        [Paragraph(f"Currency: {data['financial_info']['currency']}", style_normal)],
        [Paragraph(f"Exchange Rate: {data['financial_info']['exchange_rate']}", style_normal)],
        [Paragraph(f"Tax Rate: {data['financial_info']['tax_rate']}", style_normal)],
        [Paragraph(f"Payment Terms: {data['financial_info'].get('payment_terms', '30 days after invoicing')}", style_normal)],
        [Paragraph(f"Validity Period: {data['financial_info'].get('validity_period', '30 days')}", style_normal)],
        [Paragraph(f"Delivery Terms: {data['financial_info'].get('delivery_terms', 'FOB')}", style_normal)],
    ]

    # QR Code and Commercial Terms
    qr_code_path = "/home/borbolla/borbolla_webpage/facturador/management/commands/qr.jpg"
    if not os.path.isfile(qr_code_path):
        raise FileNotFoundError(f"QR code image not found at: {qr_code_path}")
    # Print the path to verify in the logs
    from io import BytesIO
    from reportlab.platypus import Image

    with open(qr_code_path, "rb") as file:
        qr_data = file.read()

    qr_code_image = Image(BytesIO(qr_data), width=0.75 * inch, height=0.75 * inch)

    # Commercial Terms Column
    commercial_terms = [
        [Paragraph("<b>COMMERCIAL TERMS</b>", style_normal)],
        [Paragraph(qr_code_image,style_normal)]  # QR code image for this column
    ]

    # Create the header table with the new Commercial Terms column
    header_table_data = [
        [client_info, project_info, financial_info, commercial_terms]
    ]

    # Create the header table with the new Commercial Terms column
    header_table = Table(header_table_data, colWidths=[2 * inch, 2 * inch, 2.25 * inch, 1.75 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),   # Add left padding
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Add right padding
        ('TOPPADDING', (0, 0), (-1, -1), 5),    # Add top padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5), # Add bottom padding
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white), # Add light grey inner grid lines
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey), # Add box border with same color as inner grid
        ('SPAN', (-1, 0), (-1, -1)),  # Colspan for Commercial Terms
    ]))

    story.append(header_table)

    # Add a small greeting below the header
    greeting = Paragraph(
        "Dear valued customer, we are pleased to present you with this quotation. We encourage you to review the details carefully, and do not hesitate to contact us with any questions or clarifications.",
        style_normal
    )
    story.append(Spacer(1, 10))
    story.append(greeting)
    story.append(Spacer(1, 10))

# Function to add personnel expenses table and return total labor sum
def add_personnel_expenses(story, data, project_duration):
    worker_qty = 3 * project_duration  # 3 workers per day for the entire project duration
    supervisor_qty = project_duration  # 1 supervisor per day

    worker_total_price = worker_qty * float(data['personnel'][0]["unit_price"])
    supervisor_total_price = supervisor_qty * float(data['personnel'][1]["unit_price"])
    total_sum = worker_total_price + supervisor_total_price

    table_data = [
        [Paragraph("Labor", style_bold), Paragraph("Category", style_bold), Paragraph("Item", style_bold), Paragraph("Q'ty", style_bold), Paragraph("Unit Price", style_bold), Paragraph("Total Price", style_bold), Paragraph("Remarks", style_bold)],       
    ]

    for personnel in data["personnel"]:
        if personnel["role"] == "Worker": 
            table_data.append([Paragraph("Labor", style_normal), Paragraph("Personnel Expenses", style_normal), Paragraph(personnel["role"], style_normal), Paragraph(f"{worker_qty:,}", style_normal), Paragraph(f"{personnel["unit_price"]:,}", style_normal), Paragraph(format_number(worker_total_price), style_normal), Paragraph(f"3 workers x {project_duration} days", style_normal)])
        else:

            table_data.append([Paragraph("", style_normal), Paragraph("", style_normal), Paragraph(personnel["role"], style_normal), Paragraph(f"{supervisor_qty:,}", style_normal), Paragraph(f"{personnel["unit_price"]:,}", style_normal), Paragraph(format_number(supervisor_total_price), style_normal), Paragraph(f"1 {personnel["role"]} x {project_duration} days", style_normal)])
    table_data.append([Paragraph("", style_normal), Paragraph("Sum", style_normal), Paragraph("Sum", style_normal), "", "", Paragraph(format_number(total_sum), style_subtotals), ""])

    table = Table(table_data, colWidths=[1 * inch, 0.75 * inch, 1.25 * inch, 1 * inch, 1 * inch, 1 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B5394')),
        ('SPAN', (1, 1), (1, 2)),
        ('SPAN', (1, -1), (4, -1)),
        ('SPAN', (0, 1), (0, -1)),
    ]))

    story.append(table)
    story.append(Spacer(1, 12))
    return total_sum  # Return the labor sum

def add_header(story, data):
    style_normal = ParagraphStyle(name="normal", fontSize=8, fontName="Inconsolata-Bold", alignment=TA_LEFT)
    style_bold = ParagraphStyle(name="bold", fontSize=8, fontName="Inconsolata-Bold", alignment=TA_LEFT)
    exchange_rate = get_discounted_exchange_rate()

    # Client Information
    client_info = [
        [Paragraph("<b>CUSTOMER INFORMATION</b>", style_bold)],
        [Paragraph(f"Customer Name: {data['client_info']['client_name']}", style_normal)],
        [Paragraph(f"Address: {data['client_info']['address']}", style_normal)],
        [Paragraph(f"Manager: {data['client_info']['manager']}", style_normal)],
        [Paragraph(f"Contact: {data['client_info']['contact']}", style_normal)]
    ]

    # Project Information
    project_info = [
        [Paragraph("<b>PROJECT INFORMATION</b>", style_bold)],
        [Paragraph(f"Quotation #: {data['project_info']['quotation_number']}", style_normal)],
        [Paragraph(f"Quotation Date: {data['project_info']['quotation_date']}", style_normal)],
        [Paragraph(f"Project Name: {data['project_info']['project_name']}", style_normal)],
        [Paragraph(f"Project Start: {data['project_info']['project_start']}", style_normal)],
        [Paragraph(f"Project End: {data['project_info']['project_end']}", style_normal)]
    ]

    # Financial Information
    financial_info = [
        [Paragraph("<b>FINANCIAL INFORMATION</b>", style_bold)],
        [Paragraph(f"Currency: {data['financial_info']['currency']}", style_normal)],
        [Paragraph(f"Exchange Rate: {exchange_rate:.2f}", style_normal)],
        [Paragraph(f"Tax Rate: {data['financial_info']['tax_rate']}", style_normal)],
        [Paragraph(f"Payment Terms: {data['financial_info'].get('payment_terms', '30 days after invoicing')}", style_normal)],
        [Paragraph(f"Validity Period: {data['financial_info'].get('validity_period', '30 days')}", style_normal)],
        [Paragraph(f"Delivery Terms: {data['financial_info'].get('delivery_terms', 'FOB')}", style_normal)],
    ]

    # QR Code and Commercial Terms
    #qr_code_path = "qr.jpg"
    qr_code_path = "/home/borbolla/borbolla_webpage/facturador/management/commands/qr.jpg"
    qr_code_image = Image(qr_code_path, width=0.75 * inch, height=0.75 * inch)

    # Commercial Terms Column
    commercial_terms = [
        [Paragraph("<b>COMMERCIAL TERMS</b>", style_bold)],
        [qr_code_image]  # QR code image for this column
    ]

    # Create the header table with the new Commercial Terms column
    header_table_data = [
        [client_info, project_info, financial_info, commercial_terms]
    ]

    # Create the header table with the new Commercial Terms column
    header_table = Table(header_table_data, colWidths=[2 * inch, 2 * inch, 2.5 * inch, 1.5 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),   # Add left padding
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Add right padding
        ('TOPPADDING', (0, 0), (-1, -1), 5),    # Add top padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5), # Add bottom padding
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white), # Add light grey inner grid lines
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey), # Add box border with same color as inner grid
        ('SPAN', (-1, 0), (-1, -1)),  # Colspan for Commercial Terms
    ]))

    story.append(header_table)

    # Add a small greeting below the header
    greeting = Paragraph(
        "Dear valued customer, we are pleased to present you with this quotation. We encourage you to review the details carefully, and do not hesitate to contact us with any questions or clarifications.",
        style_normal
    )
    story.append(Spacer(1, 10))
    story.append(greeting)
    story.append(Spacer(1, 10))

# Function to add materials table with rounded quantity for pipes and return material sum
def add_materials_with_remarks(story, data):
    materials_data = [
        [Paragraph("", style_bold), Paragraph("Material", style_bold), Paragraph("SQ/AWG", style_bold), Paragraph("Q'ty", style_bold), Paragraph("Unit Price", style_bold), Paragraph("Total Price", style_bold), Paragraph("Remarks", style_bold)]
    ]

    total_material_sum = 0.0
    pipe_lenght_sum = 0.0
    for material in data['material']:
        remark = ""
        qty = safe_float(material["quantity"])
        #print("Qty :",qty)
        pipe_lenght_sum += qty
        unit_price = check_and_format_price(qty, material["unit_price"])
        total_price = qty * safe_float(material["unit_price"]) if qty > 0 else 0
        total_material_sum += total_price
        
        
            
        if material["category"] == "Tubo":
            if qty >0:
                qty = int(ceil(qty/6)*6)
                #print(qty)
            
            
                remark = f"{qty} mts ({qty //  6} pipes)"
            else:
                remark = material["remarks"]
        #print(material[5])        
        

        materials_data.append([
            Paragraph("Material", style_normal),
            Paragraph(material["category"], style_normal),
            Paragraph(material["specification"], style_normal),
            Paragraph(format_number(qty), style_normal),
            Paragraph(unit_price, style_normal),
            Paragraph(format_number(total_price), style_normal),
            Paragraph(remark, style_normal),
        ])
    print("Pipe :",pipe_lenght_sum*8)
    materials_data.append([
       Paragraph("", style_normal), Paragraph("Pipe & etc", style_normal), "", "", "",Paragraph(format_number(pipe_lenght_sum*10),style_normal),""
    ])
    total_material_sum += pipe_lenght_sum*10
    materials_data.append([
        Paragraph("", style_normal), Paragraph("Total Materials", style_normal), "", "", "",Paragraph(format_number(total_material_sum),style_subtotals), ""
    ])

    table = Table(materials_data, colWidths=[1 * inch, 0.75 * inch, 1.25 * inch, 1 * inch, 1 * inch, 1 * inch, 2 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B5394')),
        #('SPAN', (1, 1), (1, 5)),
        ('SPAN', (1, 1), (1, 5)),  # Span "Interruptor" rows
        ('SPAN', (1, 6), (1, 10)),
        ('SPAN', (1, 11), (1, 15)),  # Span "Interruptor" rows
        ('SPAN', (1, 16), (1, 20)),
        ('SPAN', (1, 21), (1, 34)),
        ('SPAN', (0, 1), (0, 20)),
        ('SPAN', (0, 21), (0, 35)),
        ('SPAN', (1, -1), (-3, -1)),
        ('SPAN', (1, -2), (4, -2)),
        ('SPAN', (1, -3), (2, -3)),
    ]))

    story.append(table)
    story.append(Spacer(1, 12))
    print("Pipe lenght : ",pipe_lenght_sum)
    return total_material_sum  # Return the material sum

# Function to add equipment costs with calculated days and units, and return equipment sum
def add_equipment_with_days_and_units(story, data):
    equipment_data = [
        [Paragraph("", style_normal), Paragraph("Category", style_normal), Paragraph("Description", style_normal), Paragraph("Q'ty", style_normal), Paragraph("Unit Price", style_normal), Paragraph("Total Price", style_normal), Paragraph("Remarks", style_normal)]
    ]

    total_equipment_sum = 0.0
    for equipment in data['overhead']:
        if equipment["category"] == "Equipment":
            num_equipments = safe_float(equipment["quantity"])
            days_used = safe_float(equipment["days_used"])
            qty = int(num_equipments * days_used + num_equipments)
            # print(qty)
            unit_price = check_and_format_price(qty, equipment["unit_price"])
            #print("hdhshdsjhd",safe_float(equipment[3]))
            total_price = qty * safe_float(equipment["unit_price"]) if qty > 0 else 0
            print(total_price,"AAAAAASSSSSSS")
            total_equipment_sum += total_price
            remark = ""
            if qty > 0:
                remark = f"{int(num_equipments)} equipment * {int(days_used)} days + {int(num_equipments)} freight."
            
            
            equipment_data.append([
                Paragraph("Overhead", style_normal),
                Paragraph(equipment["category"], style_normal),
                Paragraph(equipment["description"], style_normal),
                Paragraph(format_number(qty), style_normal),
                Paragraph(unit_price, style_normal),
                Paragraph(format_number(total_price), style_normal),
                Paragraph(remark, style_normal),
            ])

    table = Table(equipment_data, colWidths=[1 * inch, 0.75 * inch, 1.25 * inch, 1 * inch, 1 * inch, 1 * inch, 2 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B5394')),
        ('SPAN', (1, 1), (1, 5)),
        ('SPAN', (1, 1), (1, 5)),  # Span "Interruptor" rows
        ('SPAN', (1, 6), (1, 10)),
        ('SPAN', (1, 11), (1, 15)),  # Span "Interruptor" rows
        ('SPAN', (1, 16), (1, 20)),
        ('SPAN', (1, 21), (1, 30)),
        ('SPAN', (0, 0), (0, 20)),
        ('SPAN', (0, 21), (0, 31)),
        ('SPAN', (1, -1), (-3, -1)),
    ]))

    #story.append(table)
    #story.append(Spacer(1, 12))
    return total_equipment_sum  # Return the equipment sum

# Function to add overhead costs and return the sum
def add_overhead_costs(story, data, management_expense, safety_expense, profit):
    overhead_data = [
        [Paragraph("", style_bold), Paragraph("Category", style_bold), Paragraph("Description", style_bold), Paragraph("Q'ty", style_bold), Paragraph("Unit Price", style_bold), Paragraph("Total Price", style_bold), Paragraph("Remarks", style_bold)]
    ]

    total_overhead_sum = management_expense + safety_expense + profit
    for overhead in data['overhead']:
        if overhead["category"] == "Equipment":
            equipment = safe_float(overhead["quantity"])
            days = safe_float(overhead["days_used"])
            qty = int(equipment * days + equipment)

            # Convert unit price to float after removing commas
            unit_price = safe_float(overhead["unit_price"]) if qty > 0 else 0

            # Calculate the total price
            total_price = qty * unit_price if qty > 0 else 0
            total_overhead_sum += total_price

            # Prepare remark
            remark = f"{int(equipment)} equipment * {int(days)} days + {int(equipment)} freight." if qty > 0 else ""

            # Debug print statements
            print(f"Qty: {qty} | Unit price: {unit_price} | Total price: {total_price}")

            overhead_data.append([
                Paragraph("Overhead", style_normal),
                Paragraph(overhead["category"], style_normal),
                Paragraph(overhead["description"], style_normal),
                Paragraph(format_number(qty), style_normal),
                Paragraph(format_number(unit_price), style_normal),
                Paragraph(format_number(total_price), style_normal),
                Paragraph(remark, style_normal),
            ])

    # Append management, safety, and profit expenses to the table
    overhead_data.append([Paragraph("Overhead", style_normal), Paragraph("Management Expense", style_normal), "", "", "", Paragraph(format_number(management_expense), style_normal), ""])
    overhead_data.append([Paragraph("Overhead", style_normal), Paragraph("Safety Expense", style_normal), "", "", "", Paragraph(format_number(safety_expense), style_normal), ""])
    overhead_data.append([Paragraph("Overhead", style_normal), Paragraph("Profit", style_normal), "", "", "", Paragraph(format_number(profit), style_normal), ""])
    overhead_data.append([Paragraph("Overhead", style_normal), Paragraph("Total Overhead", style_normal), "", "", "", Paragraph(format_number(total_overhead_sum), style_subtotals), ""])

    table = Table(overhead_data, colWidths=[1 * inch, 0.75 * inch, 1.25 * inch, 1 * inch, 1 * inch, 1 * inch, 2 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B5394')),
        ('SPAN', (0, 1), (0, -1)),
        ('SPAN', (1, 1), (1, 4)),
        ('SPAN', (1, -1), (4, -1)),
        ('SPAN', (1, -2), (4, -2)),
        ('SPAN', (1, -3), (4, -3)),
        ('SPAN', (1, -4), (4, -4)),
    ]))

    story.append(table)
    story.append(Spacer(1, 12))
    return total_overhead_sum  # Return the overhead sum


# Function to add final summary table with total costs
def add_totals(story, material_sum, labor_sum, overhead_sum,equipment_sum , data):
    print("INSIDE TOTAL COSTS : ",material_sum , labor_sum , overhead_sum)
    total_cost = material_sum + labor_sum + overhead_sum
    print("INSIDE TOTAL COSTS : ",total_cost)

    summary_data = [
        [Paragraph("Description", style_bold), Paragraph("Materials", style_bold), Paragraph("Labor", style_bold),Paragraph("Machinery", style_bold),Paragraph("Overhead", style_bold),Paragraph("Total", style_bold)],
        [Paragraph(data['project_info']['project_name'], style_normal), Paragraph(format_number(material_sum),style_normal), Paragraph(format_number(labor_sum), style_normal), Paragraph(format_number(equipment_sum), style_normal),Paragraph(format_number(overhead_sum-equipment_sum), style_normal),Paragraph(format_number(total_cost), style_subtotals)],
        [Paragraph("SubTotal", style_subtotals), "", "","","",Paragraph(format_number(total_cost), style_subtotals)],
    ]

    table = Table(summary_data, colWidths=[3 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 16),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B5394')),
        ('SPAN', (0, -1), (4, -1)),
        ('SPAN', (-1, 1), (-1, -1)),
    ]))

    
    story.append(table)
    story.append(Spacer(1, 12))

    totals_dict = {
        "materials" : format_number(material_sum) , 
        "labor" : format_number(labor_sum) , 
        "equipment" : format_number(equipment_sum) , 
        "overhead" : format_number(overhead_sum-equipment_sum) , 
        "total" : format_number(total_cost) , 
        "total_incl_iva" : format_number(total_cost*1.16)
    }

    return totals_dict

def add_closing_table(story):
    style_normal = ParagraphStyle(name="normal", fontSize=8, fontName="Inconsolata-Regular", alignment=TA_LEFT)
    style_bold = ParagraphStyle(name="bold", fontSize=8, fontName="Inconsolata-Bold", alignment=TA_LEFT)

    closing_data = [
        [Paragraph("<b>BANK INFORMATION</b>", style_bold), Paragraph("<b>CEO Approval Signature</b>", style_bold), Paragraph("<b>SIGNATURE</b>", style_bold)],
        [Paragraph("Account in USD (SPID): 112180000030697628", style_normal), Paragraph("Luis Borbolla", style_normal), Paragraph("Authorized Signature", style_normal)],
        [Paragraph("Account in Pesos (SPEI): 112962000030697626", style_normal), "", ""],
        [Paragraph("TAX ID (RFC) : PBO180817PQ2", style_normal), "", ""],
        [Paragraph("Bank Name: Grupo Financiero Monex (Bmonex)", style_normal), "", ""]
    ]

    closing_table = Table(closing_data, colWidths=[3 * inch, 3 * inch, 2 * inch])
    closing_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    story.append(closing_table)

from jinja2 import Environment, FileSystemLoader
import os

def load_email_template(template_path, context):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(current_dir), autoescape=True)
    template = env.get_template(template_path)
    html_content = template.render(context)
    return html_content

import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
from math import ceil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import os
import requests
from jinja2 import Environment, FileSystemLoader

# Constants
basedir = "/home/borbolla/borbolla_webpage/facturador/management/commands/"
PROJECT_DESCRIPTION = "Miscelaneous project"
AIRTABLE_PAT = "patAjmvQu5IDRy0sJ.f3ecfdc5382d48738024c5a87cb01d069f968894fa43e1e9c37896a5efac7d6f"

# Register fonts for PDF
pdfmetrics.registerFont(TTFont('Inconsolata-Regular', basedir + 'Inconsolata/static/Inconsolata-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Inconsolata-Bold', basedir + 'Inconsolata/static/Inconsolata-Bold.ttf'))

# Define styles for PDF
style_title = ParagraphStyle(name="title", fontSize=22, fontName="Inconsolata-Bold", alignment=TA_CENTER)
style_normal = ParagraphStyle(name="normal", fontSize=8, fontName="Inconsolata-Regular", alignment=TA_CENTER)
style_subtotals = ParagraphStyle(name="subtotals", fontSize=10, fontName="Inconsolata-Bold", alignment=TA_CENTER)
style_bold = ParagraphStyle(name="bold", fontSize=10, fontName="Inconsolata-Bold", alignment=TA_CENTER, textColor=colors.white)

# Utility functions
def get_latest_folio_and_quotation_number(api_key, base_id="appwi0zWjNflrLdjM", table_id="tbljvTFH9DnvNntXb"):
    url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "sort[0][field]": "header__folio",
        "sort[0][direction]": "desc",
        "sort[1][field]": "project_info__quotation_number",
        "sort[1][direction]": "desc",
        "maxRecords": 1
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if 'records' in data and data['records']:
            latest_folio = int(data['records'][0]['fields'].get("header__folio", 0))
            latest_quotation = data['records'][0]['fields'].get("project_info__quotation_number", "Q-0")
            next_folio = latest_folio + 1
            latest_quotation_number = int(latest_quotation.split('-')[1])
            next_quotation = f"Q-{latest_quotation_number + 1}"
        else:
            next_folio = 1
            next_quotation = "Q-1"
        return next_folio, next_quotation
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving data from Airtable: {e}")
        return None, None

def get_discounted_exchange_rate(base_currency="USD", target_currency="MXN", discount=0.1):
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    try:
        response = requests.get(url)
        data = response.json()
        exchange_rate = data['rates'][target_currency]
        return exchange_rate * (1 - discount)
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None

def format_number(value):
    try:
        return f"{float(value):,.0f}"
    except (ValueError, TypeError):
        return value

# PDF Generation functions
def generate_quotation_pdf(output_file, data):
    doc = SimpleDocTemplate(output_file, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=70, bottomMargin=72)
    story = []
    add_header(story, data)
    labor_sum = add_personnel_expenses(story, data)
    material_sum = add_materials_with_remarks(story, data)
    equipment_sum = add_equipment_with_days_and_units(story, data)
    management_expense, safety_expense, profit = calculate_overheads(labor_sum, material_sum, equipment_sum)
    overhead_sum = add_overhead_costs(story, data, management_expense, safety_expense, profit)
    totals = add_totals(story, material_sum, labor_sum, overhead_sum, equipment_sum, data)
    add_closing_table(story)
    doc.build(story, onFirstPage=lambda canvas, doc: add_header_footer(canvas, doc, data),
              onLaterPages=lambda canvas, doc: add_header_footer(canvas, doc, data))
    return totals

# Email functions
def load_email_template(template_path, context):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(current_dir), autoescape=True)
    template = env.get_template(template_path)
    return template.render(context)

def send_email_with_html_template(pdf_path, recipient, cc_recipients, subject="Quotation Sheet", template_path="email_template.html", context={}):
    email_user = "direccion@borbollagroup.com"
    app_password = "zuvr vvsz begg mopf"
    message = MIMEMultipart()
    message['From'] = email_user
    message['To'] = recipient
    message['Cc'] = ", ".join(cc_recipients)
    message['Subject'] = subject
    html_content = load_email_template(template_path, context)
    message.attach(MIMEText(html_content, 'html'))
    logo_path = os.path.join(os.path.dirname(__file__), 'logo_white.png')
    with open(logo_path, 'rb') as logo_file:
        logo = MIMEImage(logo_file.read())
        logo.add_header('Content-ID', '<logo_cid>')
        message.attach(logo)
    with open(pdf_path, "rb") as file:
        pdf_attachment = MIMEApplication(file.read(), _subtype="pdf")
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_path)
        message.attach(pdf_attachment)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_user, app_password)
            server.sendmail(email_user, [recipient] + cc_recipients, message.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Main function
def main_q():
    url = "https://hooks.airtable.com/workflows/v1/genericWebhook/appwi0zWjNflrLdjM/wflaJILadTHfhpxGy/wtrqQ06f4FMQ1c62k"
    next_folio_number, next_quotation_number = get_latest_folio_and_quotation_number(AIRTABLE_PAT)
    if next_folio_number and next_quotation_number:
        data["header"]["folio"] = next_folio_number
        data["project_info"]["quotation_number"] = next_quotation_number
        quotation_totals = generate_quotation_pdf(f"{data['project_info']['quotation_number']}-DETAILS.pdf", data)
        data['financial_info'].update(quotation_totals)
        send_email_with_html_template(
            pdf_path=f"{data['project_info']['quotation_number']}-DETAILS.pdf",
            recipient=data["client_info"]["contact"],
            cc_recipients=["direccion@borbollagroup.com"],
            subject=f"{data['project_info']['quotation_number']} | {data['project_info']['project_name']} | Quotation Sheet",
            template_path="email_template.html",
            context=data
        )
        response = requests.post(url, json=data)
        print("Response from Airtable:", response.status_code, response.text)
