from django.contrib import messages
from .forms import TenantForm, PaymentForm
from .models import HistoryLog, Payment, Tenant, Room
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.utils.dateparse import parse_date
import csv
from django.http import HttpResponse
from django.utils import timezone


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


@login_required
def dashboard(request):
    total_tenants = Tenant.objects.count()
    active_tenants = Tenant.objects.filter(is_active=True).count()
    removed_tenants = Tenant.objects.filter(is_active=False).count()

    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(tenant__is_active=True).distinct().count()
    vacant_rooms = total_rooms - occupied_rooms

    recent_logs = HistoryLog.objects.all().order_by('-timestamp')[:5]

    return render(request, 'manager/dashboard.html', {
        'total_tenants': total_tenants,
        'active_tenants': active_tenants,
        'removed_tenants': removed_tenants,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'vacant_rooms': vacant_rooms,
        'recent_logs': recent_logs,
    })


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


@login_required
@staff_member_required
def tenant_list(request):
    sort = request.GET.get('sort')
    tenants = Tenant.objects.all()

    # Sorting
    if sort == 'recent':
        tenants = tenants.order_by('-id')
    else:
        tenants = tenants.order_by('full_name')

    # Filters
    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    if status_filter is None:
        status_filter = 'active'  # Default only when no 'status' at all

    # Apply search filter
    if query:
        tenants = tenants.filter(full_name__icontains=query)

    # Apply status filter
    status_filter = request.GET.get('status', 'active')

    if status_filter == 'removed':
        tenants = tenants.filter(is_active=False)
    elif status_filter == 'active':
        tenants = tenants.filter(is_active=True)

    # print(f"Status Filter: '{status_filter}'")

    return render(request, 'manager/tenant_list.html', {
        'tenants': tenants,
        'query': query or '',
        'status_filter': status_filter,
        'sort': sort or 'alpha',
    })


@login_required
@staff_member_required
def tenant_add(request):
    if request.method == 'POST':
        form = TenantForm(request.POST, request.FILES)
        if form.is_valid():
            tenant = form.save(commit=False)
            tenant.is_active = True
            tenant.save()

            if tenant.room:
                tenant.room.is_occupied = True
                tenant.room.save()

            HistoryLog.objects.create(
                user=request.user,
                tenant_name=tenant.full_name,
                action='ADD',
                note=f"{tenant.full_name} added to {tenant.room}"
            )

            messages.success(request, 'Tenant added successfully.')
            return redirect('tenant_list')
    else:
        form = TenantForm()
    return render(request, 'manager/tenant_form.html', {'form': form, 'action': 'Add'})


@login_required
def tenant_edit(request, tenant_id):
    tenant = Tenant.objects.get(id=tenant_id)
    old_room = tenant.room

    if request.method == 'POST':
        form = TenantForm(request.POST, request.FILES, instance=tenant)
        if form.is_valid():
            tenant = form.save()

            # Update room statuses
            if old_room != tenant.room:
                if old_room and not Tenant.objects.filter(room=old_room, is_active=True).exclude(id=tenant.id).exists():
                    old_room.is_occupied = False
                    old_room.save()
                if tenant.room:
                    tenant.room.is_occupied = True
                    tenant.room.save()

            HistoryLog.objects.create(
                user=request.user,
                tenant_name=tenant.full_name,
                action='UPDATE',
                note="Tenant info updated."
            )

            messages.success(request, 'Tenant updated.')
            return redirect('tenant_list')
    else:
        form = TenantForm(instance=tenant)
    return render(request, 'manager/tenant_form.html', {'form': form, 'action': 'Edit'})


@login_required
def tenant_remove(request, tenant_id):
    tenant = Tenant.objects.get(id=tenant_id)

    tenant.is_active = False
    if not tenant.move_out_date:
        tenant.move_out_date = timezone.now().date()
    tenant.save()

    if tenant.room and not Tenant.objects.filter(room=tenant.room, is_active=True).exists():
        tenant.room.is_occupied = False
        tenant.room.save()

    HistoryLog.objects.create(
        user=request.user,
        tenant_name=tenant.full_name,
        action='REMOVE',
        note='Tenant marked as inactive/removed.'
    )

    messages.success(request, 'Tenant removed from active list.')
    return redirect('tenant_list')


@login_required
@staff_member_required
def payment_list(request):
    payments = Payment.objects.select_related('tenant').all().order_by('-year', '-month')

    tenant_query = request.GET.get('tenant')
    month_query = request.GET.get('month')
    year_query = request.GET.get('year')

    if tenant_query:
        payments = payments.filter(tenant__id=tenant_query)
    if month_query:
        payments = payments.filter(month__iexact=month_query)
    if year_query:
        payments = payments.filter(year=year_query)

    tenants = Tenant.objects.filter(is_active=True).order_by('full_name')
    months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    years = Payment.objects.values_list('year', flat=True).distinct().order_by('-year')

    return render(request, 'manager/payment_list.html', {
        'payments': payments,
        'tenants': tenants,
        'months': months,
        'years': years,
        'tenant_query': tenant_query or '',
        'month_query': month_query or '',
        'year_query': year_query or '',
    })


@login_required
def payment_add(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()

            HistoryLog.objects.create(
                user=request.user,
                tenant_name=payment.tenant.full_name,
                action='PAYMENT',  # ✅ Valid short action
                note=f"Recorded payment. Rent: {payment.rent_amount}, Electric: {payment.electricity_bill}, Water: {payment.water_bill}"
            )

            messages.success(request, 'Payment recorded successfully.')
            return redirect('payment_list')
    else:
        form = PaymentForm()
    return render(request, 'manager/payment_form.html', {'form': form})


@login_required
def payment_edit(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            updated_payment = form.save()

            HistoryLog.objects.create(
                user=request.user,
                tenant_name=updated_payment.tenant.full_name,
                action='EDIT_PAYMENT',
                note=f"Updated to — Rent: {updated_payment.rent_amount}, Electric: {updated_payment.electricity_bill}, Water: {updated_payment.water_bill}"
            )

            messages.success(request, 'Payment updated successfully.')
            return redirect('payment_list')
    else:
        form = PaymentForm(instance=payment)
    return render(request, 'manager/payment_form.html', {'form': form})


@login_required
@staff_member_required
def history_log(request):
    logs = HistoryLog.objects.all().order_by('-timestamp')

    search = request.GET.get('q')
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    export = request.GET.get('export')

    if search:
        logs = logs.filter(
            models.Q(user__username__icontains=search) |
            models.Q(tenant_name__icontains=search) |
            models.Q(action__icontains=search) |
            models.Q(note__icontains=search)
        )

    if start_date:
        logs = logs.filter(timestamp__date__gte=parse_date(start_date))
    if end_date:
        logs = logs.filter(timestamp__date__lte=parse_date(end_date))

    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=history_log.csv'
        writer = csv.writer(response)
        writer.writerow(['User', 'Action', 'Tenant', 'Note', 'Time'])
        for log in logs:
            writer.writerow([
                log.user.username,
                log.action,
                log.tenant_name,
                log.note,
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ])
        return response

    return render(request, 'manager/history_log.html', {
        'logs': logs,
        'search': search or '',
        'start_date': start_date or '',
        'end_date': end_date or ''
    })


@login_required
def room_list(request):
    rooms = Room.objects.all()
    occupied_rooms = {}
    vacant_rooms = []

    for room in rooms:
        tenants = Tenant.objects.filter(room=room, is_active=True)
        if tenants.exists():
            occupied_rooms[room] = tenants
        else:
            vacant_rooms.append(room)

    return render(request, 'manager/room_list.html', {
        'occupied_rooms': occupied_rooms,
        'vacant_rooms': vacant_rooms,
    })
