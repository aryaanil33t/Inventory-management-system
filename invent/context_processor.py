from .models import Category

def all_categories(request):
    # Only active categories
    return {
        'categories': Category.objects.filter(active_status=True)
    }