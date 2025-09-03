from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm, ProductImagesForm, ProductCategoryForm, CreatColorForm, ProductColor,ProductBrandForm
from .models import Category
from django.views import View
from django.http import  HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product, ProductImage
from .filters import ProductFilter, CategoryFilter
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from view_breadcrumbs import DetailBreadcrumbMixin
from django.utils.translation import gettext_lazy as _
from django.db.models import Max,Avg
from .models import Brand

# Create your views here.


def check_permission(**kwargs):
    request = kwargs.get('request')
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")


# Product Views
@method_decorator(never_cache, name='dispatch')
class CreateProudctView(LoginRequiredMixin, View):
    login_url = "login_admin_url"
    template_name = "products/create_product.html"

    def get(self, request):
        premission = check_permission(request=request)
        if premission:
            return premission

        form = ProductForm()

        product_images = ProductImagesForm()

        return render(request, self.template_name, {"form": form, "product_images_form": product_images})
    
    def post(self, request):
        form = ProductForm(request.POST)
        product_images_form = ProductImagesForm(request.POST, request.FILES)
        if product_images_form.is_valid() and form.is_valid():
            product = form.save()
            product.colors.set(form.cleaned_data['colors'])
            images = product_images_form.cleaned_data.get('images', [])
            if images:
                for index, image in enumerate(images):
                    product_image = ProductImage(
                        product=product,
                        image=image,
                        is_primary=(index == 0),
                    )
                    product_image.save()
            return redirect("list_products_url")
        print("Form errors:", product_images_form.errors)
        return render(request, self.template_name, {"form": form, "product_images_form": product_images_form})


@method_decorator(never_cache, name='dispatch')
class ListProductView(LoginRequiredMixin, View):
    login_url = "login_admin_url"

    template_name = "products/list_products.html"

    def get(self, request):
        premission = check_permission(request=request)
        if premission:
            return premission
        products = Product.objects.all()
        filter = ProductFilter(request.GET, queryset=products)
        # Use 'page' as the query parameter
        page_number = request.GET.get('page')
        paginator = Paginator(filter.qs, per_page=3)
        page_obj = paginator.get_page(page_number)  # Get the page object

        return render(request, self.template_name, {'products': filter.qs, "myFilter": filter, "pages": page_obj})


@method_decorator(never_cache, name='dispatch')
class EditProductView(LoginRequiredMixin, View):
    login_url = "login_admin_url"
  
    template_name = "products/edit_product.html"

    def get(self, request, product_id):
        # Check permissions
        permission = check_permission(request=request)
        if permission:
            return permission

        # Get the existing product
        product = get_object_or_404(Product, id=product_id)
        # Populate forms with existing data
        form = ProductForm(instance=product)

        product_images_form = ProductImagesForm()
     

        existing_images = Product.objects.prefetch_related(
            "images").filter(id=product_id)
        return render(request, self.template_name, {
            "form": form,
            "product_images_form": product_images_form,
            "product": product,
            "existing_products": existing_images,
            
        })

    def post(self, request, product_id):
        # Get the existing product
        product = get_object_or_404(Product, id=product_id)
        # Initialize forms with POST data and instance
        form = ProductForm(request.POST, instance=product)
        
        product_images_form = ProductImagesForm(request.POST, request.FILES)

        if product_images_form.is_valid() and form.is_valid():
            # Save updated product details
            form.save()

            # Handle images
            images = product_images_form.cleaned_data.get('images', [])

            if images:  # Only update images if new ones are provided
                # Optionally, delete existing images (uncomment if needed)
                # ProductImage.objects.filter(product=product).delete()
                has_primary = ProductImage.objects.filter(product=product)
                has_primary.delete()

                for index, image in enumerate(images):
                    product_image = ProductImage(
                        product=product,
                        image=image,
                        is_primary=(index == 0),
                    )
                    product_image.save()

            return redirect("list_products_url")

        return render(request, self.template_name, {
            "form": form,
            "product_images_form": product_images_form,
            "product": product
        })

# Category Views


@method_decorator(never_cache, name='dispatch')
class CreateCategory(LoginRequiredMixin, View):
    template_name = "products/create_category.html"

    def get(self, request):
        premission = check_permission(request=request)
        if premission:
            return premission
        form = ProductCategoryForm()
        return render(request, self.template_name, {"form": form, 'iscreate': True})

    def post(self, request):
        form = ProductCategoryForm(request.POST)
        if form.is_valid():
            if Category.objects.filter(name__iexact=form.cleaned_data['name']).exists():
               form.add_error(
                   'name', "A category with this name already exists.")
            else:
                form.save()
                return redirect("list_category_url")
        form.add_error(None, "Category is not saved")
        return render(request, self.template_name, {"form": form, 'iscreate': True})


@method_decorator(never_cache, name='dispatch')
class ListCategory(LoginRequiredMixin, View):
    template_name = 'products/list_category.html'

    def get(self, request):
        premission = check_permission(request=request)
        if premission:
            return premission

        categorys = Category.objects.all().order_by("-created_at")
        # Use 'page' as the query parameter
        page_number = request.GET.get('page')
        filter = CategoryFilter(request.GET, queryset=categorys)
        paginator = Paginator(filter.qs, per_page=10)
        page_obj = paginator.get_page(page_number)  # Get the page object
        return render(request, self.template_name, {'categorys': filter.qs, 'filter': filter, "pages": page_obj})


@method_decorator(never_cache, name='dispatch')
class EditCategory(LoginRequiredMixin, View):
    template_name = "products/create_category.html"

    def get(self, request, id):
        premission = check_permission(request=request)
        if premission:
            return premission
        category = get_object_or_404(Category, id=id)
        form = ProductCategoryForm(instance=category)
        return render(request, self.template_name, {'form': form})

    def post(self, request, id):
        permission = check_permission(request=request)
        if permission:
            return permission
        category = get_object_or_404(Category, id=id)
        form = ProductCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('list_category_url')
        return render(request, self.template_name, {'form': form})


@method_decorator(never_cache, name='dispatch')
# Soft delete on category
class DeleteCategory(LoginRequiredMixin, View):
    login_url = 'login_admin_url'

    def post(self, request, id):
        premission = check_permission(request=request)
        if premission:
            return premission
        category_delete = Category.objects.filter(id=id).first()
        if category_delete.status == 0:
            category_delete.status = 1
        else:
            category_delete.status = 0
        category_delete.save(update_fields=['status'])
        return redirect("list_category_url")


@method_decorator(never_cache, name='dispatch')
class CreateColor(LoginRequiredMixin, View):

    template_name = "products/create_color.html"

    def get(self, request):
        premission = check_permission(request=request)
        if premission:
            return premission
        form = CreatColorForm()
        colors = ProductColor.objects.all()
        return render(request, self.template_name, {'form': form, 'colors': colors})

    def post(self, request):
        form = CreatColorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_color_url')
        form.add_error("name", "color creation failed")
        return render(request, self.template_name, {'form': form})


@method_decorator(never_cache, name='dispatch')
class ProductDetail(LoginRequiredMixin, DetailBreadcrumbMixin, View):

    login_url = "login_user_url"
    template_name = "products/product_detail.html"

    def get(self, request, id):        
        product = Product.objects.filter(id=id).first()
        rating = Product.objects.filter(id=id).annotate(max_rating=Avg('reviews__rating')).values('max_rating')[0]['max_rating']

        return render(request,self.template_name,{'product':product,'product_rating':rating})
    
@method_decorator(never_cache, name='dispatch')    
class AddBrand(LoginRequiredMixin,View):
    template_name = 'products/create_brand.html'
    def get(self,request):
        brands = Brand.objects.all()
        form = ProductBrandForm()
        return render(request,self.template_name,{'form':form,'brands':brands})
    def post(self,request):
        form = ProductBrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'New brand as be added')   
            return redirect('add_brand_url')
        messages.error(request,"Please correct the errors!")
        return render(request,self.template_name,{'form':form})
    
    
class DeactivateBrand(LoginRequiredMixin,View):
    template_name = 'products/create_brand.html'
    def post(self,request,id):
        brand = get_object_or_404(Brand,id=id)
        if brand.status  == 1:
            brand.status=0
        elif brand.status == 0:
            brand.status=1        
        brand.save()   
        messages.success(request,'Deactivated')  
        return redirect('add_brand_url')
    
    
class DeleteBrand(LoginRequiredMixin,View):
    def post(self,request,id):
        brand = get_object_or_404(Brand,id=id)
        brand.delete()
        messages.success(request,'Deleted')
        return redirect('add_brand_url')

        
  