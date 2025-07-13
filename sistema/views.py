from django.shortcuts import render

def redirect_to_airtable_js(request):
    airtable_url = "https://airtable.com/appwi0zWjNflrLdjM/pagkGS7WyAvxWTN36"
    return render(request, "sistema/redirect.html", {"airtable_url": airtable_url})
