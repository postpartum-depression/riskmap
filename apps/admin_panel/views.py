from django.http import HttpResponse

def admin_dashboard(request):
    return HttpResponse('<h1>Admin Dashboard</h1><p>Панель администратора</p>')

def user_management(request):
    return HttpResponse('<h1>User Management</h1>')

def delete_user(request, user_id):
    return HttpResponse(f'<h1>Delete User {user_id}</h1>')

def vulnerability_management(request):
    return HttpResponse('<h1>Vulnerability Management</h1>')

def process_management(request):
    return HttpResponse('<h1>Process Management</h1>')
