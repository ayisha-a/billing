from django.shortcuts import render,redirect
from .forms import OrderCreateForm,OrderLinesForm,RegistrationForm,LoginForm
from django.views.generic import TemplateView
from .models import Order,OrderLines,Purchase,Product
from django.db.models import Sum
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
# Create your views here.
class ProductsList(TemplateView):
    model=Product
    template_name = "billing/product_list.html"
    context={}
    def get(self, request, *args, **kwargs):
        products=self.model.objects.all
        self.context["products"]=products
        return render(request,self.template_name,self.context)


class OrderCreate(TemplateView):
    model=Order
    form_class=OrderCreateForm
    template_name ="billing/ordercreate.html"
    context={}
    def get(self, request, *args, **kwargs):
        order=self.model.objects.last() #orm for fetching last  rec
        if order:
            last_billnum=order.billnumber
            last=int(last_billnum.split("-")[1])+1
            billnumber="klyn-"+str(last)
        else:
            billnumber="klyn-1000"
        form=self.form_class(initial={"billnumber":billnumber})
        self.context["form"]=form
        return render(request,self.template_name,self.context)
    def post(self,request, *args, **kwargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            billnumber=form.cleaned_data.get("billnumber")
            form.save()
            return redirect("orderline",billnumber=billnumber)




class OrderLine(TemplateView):
    model=OrderLines
    form_class=OrderLinesForm
    template_name = "billing/orderlines.html"
    context={}
    def get(self, request, *args, **kwargs):
        billnum=kwargs.get("billnumber")
        form=self.form_class(initial={"bill_number":billnum})
        self.context["form"]=form
        self.context['items'] = self.model.objects.filter(bill_number__billnumber=billnum)
        total = OrderLines.objects.filter(bill_number__billnumber=billnum).aggregate(Sum('amount'))
        self.context['total']=total['amount__sum']
        self.context["billnum"]=billnum
        return render(request,self.template_name,self.context)

    def post(self,request,*args,**kwargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            bill_number=form.cleaned_data.get("bill_number")
            p_qty=form.cleaned_data.get("product_quantity")
            product_name=form.cleaned_data.get("product_name")
            order=Order.objects.get(billnumber=bill_number)
            product=Purchase.objects.get(product__product_name=product_name)
            prdct=Product.objects.get(product_name=product_name)
            amount=p_qty*product.selling_price
            orderline=self.model(bill_number=order,product_name=prdct,product_qty=p_qty,amount=amount)
            
            orderline.save()
            return redirect("orderline",billnumber=bill_number)


class BillTotal(TemplateView):
    model=Order

    def get(self,request,*args,**kwargs):
        billnum=kwargs.get("billnumber")
        order=self.model.objects.get(billnumber=billnum)
        total = OrderLines.objects.filter(bill_number__billnumber=billnum).aggregate(Sum('amount'))
        total = total['amount__sum']
        order.bill_total=total
        order.save()
        print("billsaved")
        return redirect("order")

class Registration(TemplateView):
    form_class=RegistrationForm
    model=User
    template_name = "billing/registration.html"
    context={}
    def get(self,request,*args,**kwargs):
        form=self.form_class()
        self.context["form"]=form
        return render(request,self.template_name,self.context)

    def post(self,request,*args,**kwargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return render(request,"billing/login.html")
        else:
            form = self.form_class(request.POST)
            self.context["form"]=form
            return render(request, self.template_name, self.context)

class LoginView(TemplateView):
    template_name = "billing/login.html"
    form_class=LoginForm
    context={}
    def get(self, request, *args, **kwargs):
        form=self.form_class()
        self.context["form"]=form
        return render(request,self.template_name,self.context)
    def post(self, request, *args, **kwargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            uname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            user=authenticate(username=uname,password=pwd)
            if user!=None:
                login(request,user)
                return redirect("order")
            else:
                self.context["form"]=self.form_class(request.POST)
                return render(request,self.template_name,self.context)

class GenerateBill(TemplateView):
    model = OrderLines
    # model=Order
    template_name = "billing/bill.html"
    context = {}
    def get(self, request, *args, **kwargs):
        billnum = kwargs.get("billnumber")
        self.context['items'] = self.model.objects.filter(bill_number__billnumber=billnum)
        total = OrderLines.objects.filter(bill_number__billnumber=billnum).aggregate(Sum('amount'))
        self.context['total'] = total['amount__sum']
        return render(request, self.template_name, self.context)
