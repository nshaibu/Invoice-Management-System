from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from ..forms import ItemFormset

# Add invoiceitem to invoice
from invoice.models.inv import Invoice
from invoice.models.invoice_item import InvoiceItem
from invoice.models.customer import Customer


@login_required(login_url='users:login')
def add_item(request, invoice_id):
	invoice = get_object_or_404(Invoice, pk=invoice_id)
	items_added = 0
	
	try:
		if request.method == 'POST':
			itemformset = ItemFormset(request.POST)
			
			if itemformset.is_valid():
				for form in itemformset:
					
					item_name = form.cleaned_data.get('item')
					item_description = form.cleaned_data.get('description')
					item_cost = form.cleaned_data.get('cost')
					item_qty = form.cleaned_data.get('qty')

					if item_name is None or item_cost is None or item_qty is None:
						return HttpResponseRedirect(reverse('invoice:invoice', args=(invoice.id,)))

					i = invoice.invoiceitem_set.create(name=item_name, description=item_description, cost=item_cost, qty=item_qty)
					i.save()

					items_added += 1
					del i
				
				if items_added > 0:
					messages.success(request, '%d items added successfully to invoice !' % items_added)
	
	except (KeyError, Invoice.DoesNotExist):
		return render(request, 'invoice/view_invoice.html', {
			'invoice': invoice,
			'error_message': 'Not all fields were completed.',
		})
	else:
		return HttpResponseRedirect(reverse('invoice:invoice', args=(invoice.id,)))



# Delete invoiceitem from invoice
@login_required(login_url='users:login')
def delete_item(request, invoiceitem_id, invoice_id):

    item = get_object_or_404(InvoiceItem, pk=invoiceitem_id)
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    try:
        item.delete()
        messages.warning(request, 'Item deleted successfully from invoice! ')
    except (KeyError, InvoiceItem.DoesNotExist):
        return render(request, 'invoice/view_invoice.html', {
            'invoice': invoice,
            'error_message': 'Item does not exist.',
        })
    else:
        return HttpResponseRedirect(reverse('invoice:invoice', args=(invoice.id,)))