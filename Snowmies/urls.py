from django.conf.urls import url, include  # Notice we added include  
# comment out or delete the line below, we will not be using the admin module
# from django.contrib import admin
# Why won't we use the admin module? Because we're focusing on how to code, 
# not on how to help people who do not know how to code how to manage the app.
urlpatterns = [
    url(r'^', include('apps.snowmies.urls')) # And now we use the include function to pull in our first_app.urls...
]