from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.conf import settings
from datetime import datetime
import os
from .utils import generate_prs, generate_report, upload_schedule
from .models import CommerceReport
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    """Main page with upload form and download options"""
    # if request.user.is_dispatcher:
    #     return render(request, 'aggregator/home.html')
    # else:
    #     return render(request, 'aggregator/home.html')
    return render(request, 'aggregator/home.html')


@login_required
def upload_file(request):
    """Handle file upload"""
    if request.method == 'POST':
        if 'schedule_file' not in request.FILES:
            messages.error(request, 'No file selected')
            return redirect('home')
        
        file = request.FILES['schedule_file']
        if file.name == '':
            messages.error(request, 'No file selected')
            return redirect('home')
        
        if not file.name.endswith('.xlsx'):
            messages.error(request, 'Please upload an Excel (.xlsx) file')
            return redirect('home')
        
        try:
            result = upload_schedule(file, request.user)
            if result and result.startswith('Success'):
                messages.success(request, 'Schedule uploaded successfully!')
            else:
                messages.error(request, result)
        except Exception as e:
            messages.error(request, f'Error uploading file: {str(e)}')
    
    return redirect('home')


@login_required
def generate_commerce_report(request):
    """Generate and download commerce report"""
    if request.method == 'POST':
        date_str = request.POST.get('report_date')
        if not date_str:
            messages.error(request, 'Please select a date')
            return redirect('home')
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            generate_report(date, request.user)
            
            # Find the latest report file
            report = CommerceReport.objects.filter(date=date).order_by('-version').first()
            if report:
                filename = f'commerce_report_{date.strftime("%Y-%m-%d")}_v{report.version}.xlsx'
                file_path = f'/Users/tritaer/programing/mergo/{filename}'
                
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                        response['Content-Disposition'] = f'attachment; filename="{filename}"'
                        return response
                else:
                    messages.error(request, 'Report file not found')
            else:
                messages.error(request, 'No report generated')
        except Exception as e:
            messages.error(request, f'Error generating report: {str(e)}')
    
    return redirect('home')


@login_required
def generate_prs_file(request):
    """Generate and download PRS XML file"""
    if request.method == 'POST':
        date_str = request.POST.get('prs_date')
        if not date_str:
            messages.error(request, 'Please select a date')
            return redirect('home')
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            generate_prs(date)
            
            # Find the PRS file with version 1 (or you could implement version tracking)
            version = 1
            filename = f'PRS_ETG-AGG_d_{date.strftime("%Y.%m.%d")}_IPS_v{version}.xml'
            file_path = f'/Users/tritaer/programing/mergo/data/{filename}'
            
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/xml')
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return response
            else:
                messages.error(request, 'PRS file not found')
        except Exception as e:
            messages.error(request, f'Error generating PRS: {str(e)}')
    
    return redirect('home')
