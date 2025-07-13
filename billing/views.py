# billing/views.py

from decimal import Decimal
import logging

from django.utils import timezone
from django.shortcuts   import redirect,get_object_or_404
from django.urls        import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.forms       import inlineformset_factory
from django.http        import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from .models            import Quotation, QuotationItem
from .forms import QuotationForm
from reportes.models.data import Project, Contact

from collections import OrderedDict
import itertools

from django.conf import settings

from django.contrib import messages
from reportes.utils.send_mail import gas

from django.core.mail import EmailMultiAlternatives
import io
import base64
from decimal import Decimal

import qrcode



logger = logging.getLogger(__name__)

# ─── inline formset for line items ──────────────────────────
QuotationItemFormSet = inlineformset_factory(
    Quotation,
    QuotationItem,
    fields=['category', 'description', 'qty', 'days', 'unit_price', 'remarks'],
    extra=1,
    can_delete=True
)

import io, base64, math
from datetime import timedelta
from decimal import Decimal
import qrcode
from django.shortcuts import get_object_or_404, render

def make_qr_data_uri(content, box_size=6, border=2):
    """Generate a base64-data-URI PNG QR for the given content."""
    qr = qrcode.QRCode(box_size=box_size, border=border)
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    data = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{data}"

def quotation_public(request, token):
    qt = get_object_or_404(Quotation, access_token=token)

    # 1) Collect line‐items by category
    labor_items     = qt.items.filter(category='labor')
    material_items  = qt.items.filter(category='material')
    equipment_items = qt.items.filter(category='equipment')
    overhead_items  = qt.items.filter(category='overhead')

    drawings = qt.project.drawings.all()

    # 2) Sum helper
    def sum_cat(qs):
        return sum(i.qty * i.days * i.unit_price for i in qs)

    sum_labor    = sum_cat(labor_items)
    sum_material = sum_cat(material_items)
    sum_equip    = sum_cat(equipment_items)
    sum_extra    = sum_cat(overhead_items)
    grand_total  = sum_labor + sum_material + sum_equip + sum_extra

    # 3) Deposit (30%)
    deposit_amount = (grand_total * Decimal('0.30')).quantize(Decimal('1'))

    # 4) Build absolute URLs for QR
    online_url     = request.build_absolute_uri(qt.get_secure_url())
    commercial_pdf = request.build_absolute_uri('/media/commercial.pdf')

    # 5) Generate QR codes
    qr_online     = make_qr_data_uri(online_url)
    qr_commercial = make_qr_data_uri(commercial_pdf)

    # 6) Default payment milestones (use Decimal for percentages)
    payment_rows = [
        {
          "label": "60% Advance Payment",
          "pct": 60,
          "amount": math.ceil((grand_total * Decimal('0.60')).quantize(Decimal('1')))
        },
        {
          "label": "30% Running Bill",
          "pct": 30,
          "amount": math.ceil((grand_total * Decimal('0.30')).quantize(Decimal('1')))
        },
        {
          "label": "10% After Work Finish",
          "pct": 10,
          "amount": math.ceil((grand_total * Decimal('0.10')).quantize(Decimal('1')))
        },
    ]

    # 7) Project Timeline from the related Project model
    proj = qt.project
    start = proj.start_date or qt.date_issued
    end   = proj.end_date   or qt.valid_until
    total_days = max((end - start).days, 1)

    prelim_days   = math.ceil(total_days * 0.15)
    main_days     = math.ceil(total_days * 0.80)
    delivery_days = total_days - (prelim_days + main_days)

    t1_start = start
    t1_end   = start + timedelta(days=prelim_days - 1)
    t2_start = t1_end + timedelta(days=1)
    t2_end   = t2_start + timedelta(days=main_days - 1)
    t3_start = t2_end + timedelta(days=1)
    t3_end   = end

    timeline_rows = [
        {"label": "Preliminaries (~15%)", "start": t1_start, "end": t1_end},
        {"label": "Main Project (~80%)",  "start": t2_start, "end": t2_end},
        {"label": "Delivery (~5%)",       "start": t3_start, "end": t3_end},
    ]

    # 8) Render
    return render(request, 'billing/quotation_public.html', {
        'quotation':       qt,
        'labor_items':     labor_items,
        'material_items':  material_items,
        'equipment_items': equipment_items,
        'overhead_items':  overhead_items,
        'sum_labor':       sum_labor,
        'sum_material':    sum_material,
        'sum_equip':       sum_equip,
        'sum_extra':       sum_extra,
        'grand_total':     grand_total,
        'deposit_amount':  deposit_amount,
        'qr_online':       qr_online,
        'qr_commercial':   qr_commercial,
        'payment_rows':    payment_rows,
        'timeline_rows':   timeline_rows,
        'drawings':        drawings, 
    })

def quotation_send(request, pk):
    qt = get_object_or_404(Quotation, pk=pk)

    # Re‐compute totals so we can include them in the email
    labor_items     = qt.items.filter(category='labor')
    material_items  = qt.items.filter(category='material')
    equipment_items = qt.items.filter(category='equipment')
    overhead_items  = qt.items.filter(category='overhead')

    def sum_cat(qs):
        return sum(i.qty * i.days * i.unit_price for i in qs)

    sum_labor    = sum_cat(labor_items)
    sum_material = sum_cat(material_items)
    sum_equip    = sum_cat(equipment_items)
    sum_extra    = sum_cat(overhead_items)
    grand_total  = int(sum_labor + sum_material + sum_equip + sum_extra)

    # Build the view link and QR if desired
    link = request.build_absolute_uri(qt.get_secure_url())

    # Render the HTML email
    html_body = render_to_string('billing/email/quotation_email.html', {
        'quotation':   qt,
        'grand_total': grand_total,
        'link':        link,
    })

    subject = f"Quotation {qt.number}"
    msg = EmailMultiAlternatives(subject, html_body, to=[qt.client.email])
    msg.attach_alternative(html_body, "text/html")
    msg.send()

    # Redirect or inform the user
    return redirect('billing:quotation_list')
class QuotationListView(ListView):
    model = Quotation
    template_name = 'billing/quotation_list.html'
    context_object_name = 'quotations'  # we’ll override in get_context_data
    paginate_by = 20

    def get_queryset(self):
        today = timezone.localdate()
        # only active, order by client then newest first
        return (
            Quotation.objects
            .filter(valid_until__gte=today)
            .select_related('client','project')
            .order_by('client__legal_name', '-pk')
        )

    def get_context_data(self, **kwargs):
        qs = list(self.get_queryset())
        # group by client
        groups = []
        for client, items in itertools.groupby(qs, key=lambda q: q.client):
            lst = list(items)
            subtotal = sum(q.total_amount for q in lst)
            groups.append({
                'client':   client,
                'quotations': lst,
                'subtotal': subtotal,
            })

        ctx = super().get_context_data(**kwargs)
        ctx['clients_list'] = groups
        return ctx
    
    

class QuotationDetailView(DetailView):
    model = Quotation
    template_name = 'billing/quotation_detail.html'
    context_object_name = 'quotation'

    def get_queryset(self):
        return super().get_queryset()\
                    .select_related('client','project')\
                    .prefetch_related('notify_contacts')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.object

        # categorize your items
        ctx['labor_items']     = q.items.filter(category='labor')
        ctx['material_items']  = q.items.filter(category='material')
        ctx['equipment_items'] = q.items.filter(category='equipment')
        ctx['overhead_items']  = q.items.filter(category='overhead')

        # compute sums
        def sum_cat(qs):
            return sum(i.qty * i.days * i.unit_price for i in qs)
        ctx['sum_labor']     = sum_cat(ctx['labor_items'])
        ctx['sum_material']  = sum_cat(ctx['material_items'])
        ctx['sum_equip']     = sum_cat(ctx['equipment_items'])
        ctx['sum_extra']     = sum_cat(ctx['overhead_items'])
        ctx['grand_total']   = (
            ctx['sum_labor']
            + ctx['sum_material']
            + ctx['sum_equip']
            + ctx['sum_extra']
        )

        # your unit dropdown options
        ctx['standard_units'] = ["pcs","m","m²","m³","kg","L","h"]
        ctx['drawings'] = q.project.drawings.all()

        return ctx

class QuotationDeleteView(DeleteView):
    model = Quotation
    template_name = 'billing/quotation_confirm_delete.html'
    success_url = reverse_lazy('billing:quotation_list')


# ─── Create / Update ────────────────────────────────────────
class QuotationCreateView(CreateView):
    model = Quotation
    form_class = QuotationForm

    template_name = 'billing/quotation_form.html'
    success_url = reverse_lazy('billing:quotation_list')

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        # no projects until client chosen
        form.fields['project'].queryset = Project.objects.none()
        cid = self.request.POST.get('client') or self.request.GET.get('client')
        if cid:
            form.fields['project'].queryset = Project.objects.filter(client_id=cid)
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['item_formset'] = QuotationItemFormSet(self.request.POST or None)
        return ctx

    def form_valid(self, form):
        # 1) Save the main Quotation with a placeholder total
        self.object = form.save(commit=False)
        self.object.total_amount = Decimal('0.00')
        self.object.save()
        form.save_m2m()

        # 2) Save all your user‐entered line‐items
        formset = QuotationItemFormSet(self.request.POST, instance=self.object)
        if not formset.is_valid():
            return self.form_invalid(form)
        formset.save()

        # 3) Recompute the “base” sum across *all* labor/material/equipment rows
        base_qs = self.object.items.filter(
            category__in=['labor','material','equipment']
        )
        base = sum(
            item.qty * item.days * item.unit_price
            for item in base_qs
        )

        # 4) Append your three overhead items
        overhead_specs = [
            ("Management expenses", Decimal('0.06')),
            ("Safety Expenses",       Decimal('0.02')),
            ("Profit",                Decimal('0.08')),
        ]
        for desc, pct in overhead_specs:
            QuotationItem.objects.create(
                quotation   = self.object,
                category    = 'overhead',
                description = desc,
                qty         = pct,
                days        = Decimal('1.00'),
                unit_price  = base
            )

        # 5) Recompute grand total including overhead
        all_items = self.object.items.all()
        grand_total = sum(
            itm.qty * itm.days * itm.unit_price
            for itm in all_items
        )
        self.object.total_amount = grand_total
        self.object.save(update_fields=['total_amount'])

        return redirect(self.get_success_url())

class QuotationUpdateView(UpdateView):
    model = Quotation
    form_class = QuotationForm

    template_name = 'billing/quotation_form.html'
    success_url = reverse_lazy('billing:quotation_list')

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        # limit project dropdown to the chosen client
        client_id = self.request.POST.get('client') or self.object.client_id
        form.fields['project'].queryset = (
            Project.objects.filter(client_id=client_id)
            if client_id else Project.objects.none()
        )
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['item_formset'] = QuotationItemFormSet(
            self.request.POST or None,
            instance=self.object
        )
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form    = self.get_form()
        formset = QuotationItemFormSet(request.POST, instance=self.object)

        if not form.is_valid() or not formset.is_valid():
            import logging
            logger = logging.getLogger(__name__)
            logger.debug("Main form errors: %s", form.errors)
            logger.debug("Formset errors: %s", formset.errors)
            return self.form_invalid(form, formset)

        return self.form_valid(form, formset)

    def form_valid(self, form, formset):
        # save the quotation
        quotation = form.save(commit=False)
        quotation.save()
        form.save_m2m()

        # save upsert of all line‐items
        formset.save()

        # recompute total_amount
        total = sum(
            itm.qty * itm.days * itm.unit_price
            for itm in quotation.items.all()
        )
        quotation.total_amount = total
        quotation.save(update_fields=['total_amount'])

        return redirect(self.success_url)

    def form_invalid(self, form, formset=None):
        logger.error("=== QUOTATION UPDATE INVALID ===")
        logger.error("Main form valid? %s", form.is_valid())
        logger.error("Main form errors: %r", form.errors)
        if formset is not None:
            logger.error("Formset valid? %s", formset.is_valid())
            # formset.errors is a list of dicts—one per row
            logger.error("Formset errors: %r", formset.errors)
        ctx = self.get_context_data(form=form, item_formset=formset)
        return render(self.request, self.template_name, ctx)

# ─── JSON API for AJAX project filtering ────────────────────
@require_GET
def client_contacts_json(request):
    client_id = request.GET.get('client')
    qs = Contact.objects.filter(client_id=client_id) if client_id else Contact.objects.none()
    data = [
        {'id': c.pk, 'name': c.name, 'email': c.email}
        for c in qs
    ]
    return JsonResponse(data, safe=False)

@require_GET
def project_list_json(request):
    client_id = request.GET.get('client')
    qs = Project.objects.filter(client_id=client_id) if client_id else Project.objects.none()
    data = list(qs.values('id', 'name', 'contract_number'))
    return JsonResponse(data, safe=False)

@require_POST
def quotation_send(request, pk):
    qt = get_object_or_404(Quotation, pk=pk)
    contacts = qt.notify_contacts.all()
    if not contacts:
        messages.warning(request, "No contacts have been selected on this quotation.")
        return redirect('billing:quotation_list')

    # build secure, tokenized link
    link = request.build_absolute_uri(qt.get_secure_url())

    # plain-text body
    body_text = render_to_string('billing/email/quotation_email.txt', {
      'quotation': qt,
      'link':       link,
    })

    # HTML body (uses Bootstrap via your base template)
    html_body = render_to_string('billing/email/quotation_email.html', {
      'quotation': qt,
      'link':       link,
    })

    to_addrs = [c.email for c in contacts]
    support_email = "customer-support@borbollagroup.com"
    if support_email not in to_addrs:
        to_addrs.append(support_email)
    subject = f"Your Quotation #{qt.number} from {settings.COMPANY_NAME}"

    try:
        gas(
          to=to_addrs,
          subject=subject,
          body=body_text,
          html_body=html_body,
        )
    except Exception:
        messages.error(request, "Failed to send quotation — please check your mail gateway.")
    else:
        qt.email_sent = True
        qt.save(update_fields=['email_sent'])
        messages.success(request, f"Quotation sent to {len(to_addrs)} contact(s).")

    return redirect('billing:quotation_list')