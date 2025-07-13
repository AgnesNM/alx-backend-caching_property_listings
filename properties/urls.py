from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    # Property list view - cached for 15 minutes
    path('', views.property_list, name='property_list'),
    
    # Alternative: Class-based view (commented out)
    # path('', views.PropertyListView.as_view(), name='property_list'),
    
    # JSON API for properties
    path('api/', views.property_list_json, name='property_list_json'),
    
    # Property detail view
    path('<int:property_id>/', views.property_detail, name='property_detail'),
]
