from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from loguru import logger

from .forms import CarForm, CustomerForm, SaleForm, SaleFormCreate
from .models import Car, Customer, Sales

# Create your views here.


class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["user_autenticated"] = self.request.user.is_authenticated

        return context


class CarCRUD(LoginRequiredMixin, TemplateView):
    login_url = "/admin/"
    template_name = 'car/crud.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cars"] = Car.objects.all()
        context["form"] = CarForm()
        context["update_forms"] = zip(context["cars"], [CarForm(instance=instance) for instance in context["cars"]])

        return context

    def post(self, request: http.HttpRequest, *args, **kwargs) -> http.HttpResponse:
        logger.info(f"[{self.__class__.__name__}] -> {request = } | {request.POST = } | {args = } | {kwargs = }")
        context = dict()

        # --------------------------------------------------
        if request.POST['action'] == 'delete':
            car = get_object_or_404(Car, pk=request.POST['delete_car_id'])
            car.delete()
            messages.success(request, "Car deleted!")
        # --------------------------------------------------
        elif request.POST['action'] == 'update':
            car = get_object_or_404(Car, pk=request.POST['update_car_id'])
            form = CarForm(request.POST, instance=car)
            if not form.is_valid():
                context['form_errors'] = form.errors
                messages.error(request, "Form has an error!")
            else:
                messages.success(request, "Car updated!")
                car: Car = form.save(commit=False)
                car.save(update=True)
        # --------------------------------------------------
        elif request.POST['action'] == 'create':
            form = CarForm(request.POST)
            if not form.is_valid():
                context['form_errors'] = form.errors
                messages.error(request, "Form has an error!")
            else:
                messages.success(request, "Car created!")
                form.save(commit=True)
        else:
            context['form_errors'] = "Unknow action!"
            messages.error(request, "Unknow action!")
        # --------------------------------------------------
        context.update(self.get_context_data())

        if meta := request.META.get('HTTP_REFERER'):
            return redirect(meta)
        return render(request, self.template_name, context)


class SalesCRUD(LoginRequiredMixin, TemplateView):
    login_url = "/admin/"
    template_name = 'sales/crud.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = SaleForm()
        # uses the logged user as the salesperson
        # so john cannote sell using the name of jane
        if not self.request.user.is_superuser:
            form.base_fields["salesperson"].initial = self.request.user
            form.base_fields['salesperson'].disabled = True
        else:
            form.base_fields['salesperson'].disabled = False

        # form.base_fields['car'].queryset = True

        context["sales"] = Sales.objects.all()
        context["form"] = form
        context["update_forms"] = zip(context["sales"], [SaleForm(instance=instance) for instance in context["sales"]])
        return context

    def post(self, request: http.HttpRequest, *args, **kwargs) -> http.HttpResponse:
        logger.info(f"[{self.__class__.__name__}] -> {request = } | {request.POST = } | {args = } | {kwargs = }")
        context = dict()

        # --------------------------------------------------
        if request.POST['action'] == 'delete':
            sale = get_object_or_404(Sales, pk=request.POST['delete_sale_id'])
            sale.delete()
            logger.debug(f"{request.POST['delete_sale_id']} deletado")
            messages.success(request, "Sale deleted!")
        # --------------------------------------------------
        elif request.POST['action'] == 'update':
            car = get_object_or_404(Sales, pk=request.POST['update_sale_id'])
            form = SaleForm(request.POST, instance=car)
            if not form.is_valid():
                context['form_errors'] = form.errors
                messages.error(request, "Form has an error!")
            else:
                messages.success(request, "Sale updated!")
                form.save(commit=True)
        # --------------------------------------------------
        elif request.POST['action'] == 'create':
            form = SaleFormCreate(request.POST)
            if not form.is_valid():
                context['form_errors'] = form.errors
                messages.error(request, "Form has an error!")
            else:
                messages.success(request, "Sale created!")
                form.save(commit=True)
        else:
            context['form_errors'] = "Unknow action!"
            messages.error(request, "Unknow action!")

        # --------------------------------------------------
        context.update(self.get_context_data())

        if meta := request.META.get('HTTP_REFERER'):
            return redirect(meta)
        return render(request, self.template_name, context)


class CustomerCRUD(LoginRequiredMixin, TemplateView):
    login_url = "/admin/"
    template_name = 'customer/crud.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["customers"] = Customer.objects.all()
        context["form"] = CustomerForm()
        context["update_forms"] = zip(context["customers"], [CustomerForm(instance=instance) for instance in context["customers"]])
        return context

    def post(self, request: http.HttpRequest, *args, **kwargs) -> http.HttpResponse:
        logger.info(f"[{self.__class__.__name__}] -> {request = } | {request.POST = } | {args = } | {kwargs = }")
        context = dict()

        # --------------------------------------------------
        if request.POST['action'] == 'delete':
            customer = get_object_or_404(Customer, pk=request.POST['delete_customer_id'])
            customer.delete()
            messages.success(request, "Customer deleted!")
        # --------------------------------------------------
        elif request.POST['action'] == 'update':
            customer = get_object_or_404(Customer, pk=request.POST['update_customer_id'])
            form = CustomerForm(request.POST, instance=customer)
            if not form.is_valid():
                context['form_errors'] = form.errors
                messages.error(request, "Form has an error!")
            else:
                messages.success(request, "Customer updated!")
                form.save(commit=True)
        # --------------------------------------------------
        elif request.POST['action'] == 'create':
            form = CustomerForm(request.POST)
            if not form.is_valid():
                context['form_errors'] = form.errors
                messages.error(request, "Form has an error!")
            else:
                messages.success(request, "Customer created!")
                form.save(commit=True)
        else:
            context['form_errors'] = "Unknow action!"
            messages.error(request, "Unknow action!")
        # --------------------------------------------------
        context.update(self.get_context_data())

        if request.POST.get('from_detail'):
            return redirect('customers_crud')
        if meta := request.META.get('HTTP_REFERER'):
            return redirect(meta)
        return render(request, self.template_name, context)


class CustomerDetailView(LoginRequiredMixin, TemplateView):
    login_url = "/admin/"
    template_name = 'customer/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["customer"] = get_object_or_404(Customer, pk=kwargs['pk'])
        context["form"] = CustomerForm(instance=context["customer"])
        context["cars"] = Car.objects.filter(owner=kwargs['pk'])
        return context
