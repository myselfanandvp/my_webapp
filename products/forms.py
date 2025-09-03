from django import forms
from .models import Product,Brand,Category,ProductReview,ProductColor
from django.core.validators import FileExtensionValidator
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

inputfield_style={"class":"bg-gray-50 border border-gray-500 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"}
imagefield_style={"class":"visually-hidden"}



class ProductColorForm(forms.ModelForm):
    class Meta:
        model = ProductColor
        fields = ['color', 'name']
        widgets = {
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
            }),
            'name': forms.TextInput(attrs={
                **inputfield_style,
                'placeholder': 'Optional color name (e.g., Red)',
            }),
        }

    def clean_color(self):
        color = self.cleaned_data['color']
        if not color or not color.startswith('#') or len(color) != 7:
            raise forms.ValidationError('Invalid hex color code.')
        return color



class ProductForm(forms.ModelForm): 
    description=forms.CharField(widget=forms.Textarea(attrs={'class':"block w-full h-20 resize-none text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500"}))
    name = forms.CharField(widget=forms.TextInput(attrs={**inputfield_style}))
    slug = forms.CharField(widget=forms.TextInput(attrs={**inputfield_style}))
    price = forms.CharField(widget=forms.NumberInput(attrs={**inputfield_style}))
   
    category=forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select Category",
        required=True,
        widget=forms.Select(attrs={
            "class":"w-full px-3 py-2 text-sm text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-gray-200 dark:bg-gray-800 dark:border-gray-600 dark:focus:ring-blue-600"
        })
    )
    
    
    
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        empty_label="Select Brand",
        required=True,
        widget=forms.Select(attrs={"class":"w-full px-3 py-2 text-sm text-gray-700 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-gray-200 dark:bg-gray-800 dark:border-gray-600 dark:focus:ring-blue-600"
                                   
                                   
                                   })
    )
    
    
    colors = forms.ModelMultipleChoiceField(
        queryset=ProductColor.objects.all(),
        required=False,  # Changed to align with blank=True in model
        widget=forms.CheckboxSelectMultiple(attrs={
            "class": "fg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-1"
        }),
        
    )

    stock_qty= forms.CharField(widget=forms.NumberInput(attrs={**inputfield_style}))

    class Meta:
        model = Product
        # fields = ['description','name','brand','category','slug','price','status','is_deleted','colors','stock_qty']
        fields = ['name','slug','price','colors','stock_qty','brand','category','description','is_deleted']
        
        
class ProductBrandForm(forms.ModelForm):
    slug= forms.CharField(widget=forms.TextInput(attrs={**inputfield_style}))
    name= forms.CharField(widget=forms.TextInput(attrs={**inputfield_style}))
    status = forms.ChoiceField(choices=[  (1, 'Active'),
        (0, 'Inactive')],widget=forms.Select(attrs={**inputfield_style}))
    
    class Meta:
        model =Brand
        fields =['name','slug','status']
        
class ProductCategoryForm(forms.ModelForm):
    slug= forms.CharField(widget=forms.TextInput(attrs={**inputfield_style}))
    name= forms.CharField(widget=forms.TextInput(attrs={**inputfield_style}))
    type= forms.CharField(widget=forms.TextInput(attrs={**inputfield_style}))
    status = forms.ChoiceField(choices=[  (1, 'Active'),
        (0, 'Inactive')],widget=forms.Select(attrs={**inputfield_style}))
    class Meta:
        model =Category
        fields ="__all__"


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model =ProductReview
        fields ="__all__"

    
class ProductImagesForm(forms.Form):
    image1 = forms.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], required=False, label="Image 1", widget=forms.FileInput(attrs={**imagefield_style}))
    image2 = forms.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], required=False, label="Image 2", widget=forms.FileInput(attrs={**imagefield_style}))
    image3 = forms.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], required=False, label="Image 3", widget=forms.FileInput(attrs={**imagefield_style}))
    image4 = forms.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], required=False, label="Image 4", widget=forms.FileInput(attrs={**imagefield_style}))

    def clean(self):
        cleaned_data = super().clean()
        cropped_images = []
        images = [cleaned_data.get(f'image{i}') for i in range(1, 5) if cleaned_data.get(f'image{i}')]
        for idx, image in enumerate(images):
            if image and image.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError(f"{image.name} exceeds the 5MB size limit.")
            if image:
                try:
                    img = Image.open(image)
                    width, height = img.size
                    min_dim = min(width, height)
                    left = (width - min_dim) / 2
                    top = (height - min_dim) / 2
                    right = (width + min_dim) / 2
                    bottom = (height + min_dim) / 2
                    img_cropped = img.crop((left, top, right, bottom))
                    img_cropped = img_cropped.resize((800, 800), Image.Resampling.LANCZOS)
                    buffer = BytesIO()
                    img_cropped.save(buffer, format='JPEG')
                    buffer.seek(0)
                    new_name = f"{image.name.split('.')[0]}_cropped.jpg"
                    new_image = ContentFile(buffer.read(), name=new_name)
                    cropped_images.append(new_image)
                except Exception as e:
                    raise forms.ValidationError(f"Error processing image {idx+1}: {str(e)}")
        cleaned_data['images'] = cropped_images
        return cleaned_data
    
    
    
class CreatColorForm(forms.ModelForm):
    color = forms.CharField(widget=forms.TextInput(attrs={ "value":"#8c1ff9" ,"type":"color","class":"w-32 h-10  bg-gradient-to-r from-indigo-600 to-purple-600   rounded-lg  hover:from-indigo-700 hover:to-purple-700 transition duration-300 transform hover:scale-105"}))
    name = forms.CharField(widget=forms.TextInput(attrs={ "class":"bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5","placeholder":"Enter the name of the color"}))
    class Meta:
        model = ProductColor
        fields =['color','name']
        
        
        
