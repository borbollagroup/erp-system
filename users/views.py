from django.shortcuts import render, redirect

from django.contrib import messages
from .forms import UserRegisterForm , UserUpdateForm , ProfileUpdateForm
from django.contrib.auth.decorators import login_required

from django.utils import timezone
import datetime



from decimal import Decimal

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('cotizaciones')
        else:
            # Form has errors
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {"form": form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST , instance = request.user)
        p_form = ProfileUpdateForm(request.POST , 
                                   request.FILES , 
                                   instance = request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance = request.user)
        p_form = ProfileUpdateForm(instance = request.user.profile)

    user = request.user
    employee = getattr(user, 'employee', None)
    
    today = timezone.now().date()
    start_of_week = today - datetime.timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + datetime.timedelta(days=6)  # Sunday

    
    context = {
        'user': user,
        'employee': employee,
        'pay_period_start': start_of_week,
        'pay_period_end': end_of_week,
        'payment_date': today,
        'week_number': start_of_week.isocalendar()[1],
        'u_form':u_form,
        'p_form':p_form
    }
    
    if employee:
        seventh_day = Decimal('228.57')
        efficiency_bonus = Decimal('100.00')
        punctuality_bonus = Decimal('0.00')
        attendance_bonus = Decimal('0.00')
        overtime_pay = employee.overtime_pay if hasattr(employee, 'overtime_pay') else Decimal('0.00')
        loans = Decimal('0.00')

        total_perceptions = (
            employee.salary +
            seventh_day +
            efficiency_bonus +
            punctuality_bonus +
            attendance_bonus +
            overtime_pay
        )
        total_deductions = (
            employee.IMSS +
            employee.INFONAVIT +
            loans
        )
        net_received = total_perceptions - total_deductions

        context.update({
            'normal_salary': employee.salary,
            'seventh_day': seventh_day,
            'efficiency_bonus': efficiency_bonus,
            'punctuality_bonus': punctuality_bonus,
            'attendance_bonus': attendance_bonus,
            'overtime': overtime_pay,
            'imss': employee.IMSS,
            'infonavit': employee.INFONAVIT,
            'loans': loans,
            'total_perceptions': total_perceptions,
            'total_deductions': total_deductions,
            'net_received': net_received,
        })

    return render(request, 'users/profile.html', context)