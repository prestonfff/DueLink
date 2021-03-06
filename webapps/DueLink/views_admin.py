from django.contrib.auth.models import User, Permission, Group
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponseForbidden, \
    Http404
from DueLink.forms import *
from DueLink.models import *


# TODO yizhong shunjian rang ni biancheng guanliyuan de yemian
@login_required
def admin_get(request):
    try:
        if Group.objects.filter(name='duelink_admin').count() == 0:
            Group.objects.create(name="duelink_admin")

        g = Group.objects.get(name='duelink_admin')
        t = Permission.objects.filter(codename__icontains='school') | Permission.objects.filter(
            codename__icontains='course')
        for each in t: g.permissions.add(each)

        request.user.groups.add(g)
    except:
        return HttpResponse("Fail to get promoted")

    return HttpResponse("You are good to go")


@permission_required('DueLink.add_course')
@permission_required('DueLink.delete_course')
@login_required
def manage_course(request):
    if not request.method == 'GET':
        return HttpResponseForbidden("Invalid method")

    return HttpResponseRedirect(reverse('add_course'))


@login_required
@permission_required('DueLink.add_course')
def add_course(request):
    if request.method == 'GET':
        form = AddCourseForm()
        context = {'add_course_form': form, 'add_course': True}
        return render(request, 'duelink_admin/add_course.html', context)

    if request.method == 'POST':
        form = AddCourseForm(request.POST)
        if form.is_valid():  # Validate input data & duplicate course sections
            form.save()
            response_form = AddCourseForm()
            # success_flag and add_course is for the alerts in return pages
            context = {'add_course_form': response_form, 'success_flag': True, 'add_course': True}
            return render(request, 'duelink_admin/add_course.html', context)
        else:
            context = {'add_course_form': form, 'fail_flag': True, 'add_course': True}
            return render(request, 'duelink_admin/add_course.html', context)


@login_required
@permission_required('DueLink.add_course')
def add_section(request):
    if request.method == 'GET':
        form = AddSectionForm()
        context = {'add_section_form': form, 'add_section': True}
        return render(request, 'duelink_admin/add_section.html', context)

    if request.method == 'POST':
        form = AddSectionForm(request.POST)
        if form.is_valid():
            origin_course = form.cleaned_data['origin_course']
            new_course = Course(course_name=origin_course.course_name, course_number=origin_course.course_number,
                                school=origin_course.school)
            new_course.section = form.cleaned_data['new_section']
            # If admin leave the instructor input blank, use the exist one
            if form.cleaned_data['new_instructor'] is None or form.cleaned_data['new_instructor'] == '':
                new_course.instructor = origin_course.instructor
            else:
                new_course.instructor = form.cleaned_data['new_instructor']
            new_course.save()

            response_form = AddSectionForm()
            context = {'add_section_form': response_form, 'success_flag': True, 'add_section': True}
            return render(request, 'duelink_admin/add_section.html', context)
        else:
            context = {'add_section_form': form, 'fail_flag': True, 'add_section': True}
            return render(request, 'duelink_admin/add_section.html', context)


@login_required
@permission_required('DueLink.delete_course')
def delete_course(request):
    if request.method == 'GET':
        form = DeleteCourseForm()
        context = {'delete_course_form': form, 'delete_course': True}
        return render(request, 'duelink_admin/delete_course.html', context)

    if request.method == 'POST':
        form = DeleteCourseForm(request.POST)
        if form.is_valid():
            # TODO: 404
            course = form.cleaned_data['courses']
            course.delete()
            response_form = DeleteCourseForm()
            context = {'delete_course_form': response_form, 'success_flag': True, 'delete_course': True}
            return render(request, 'duelink_admin/delete_course.html', context)
        else:
            context = {'delete_course_form': form, 'fail_flag': True, 'delete_course': True}
            return render(request, 'duelink_admin/delete_course.html', context)


@login_required
@permission_required('DueLink.add_school')
def add_school(request):
    if request.method == 'GET':
        form = AddSchoolForm()
        context = {'add_school_form': form, 'add_school': True}
        return render(request, 'duelink_admin/add_school.html', context)

    if request.method == 'POST':
        form = AddSchoolForm(request.POST)
        if form.is_valid():
            form.save()
            context = {'add_school_form': form, 'add_school': True, 'success_flag': True}
            return render(request, 'duelink_admin/add_school.html', context)
        else:
            context = {'add_school_form': form, 'add_school': True, 'fail_flag': True}
            return render(request, 'duelink_admin/add_school.html', context)


@login_required
@permission_required('DueLink.add_course')
@permission_required('DueLink.delete_course')
def publish_deadline(request):
    if request.method == 'GET':
        form = PublishDeadlineForm()
        context = {'publish_deadline_form': form, 'publish_deadline': True}
        return render(request, 'duelink_admin/publish_deadline.html', context)

    if request.method == 'POST':
        form = PublishDeadlineForm(request.POST)
        print(request.POST)
        if 'deadline_datetime' in request.POST:
            form_time = DueTimeForm()
            due = form_time.clean_deadline_datetime(request.POST['deadline_datetime'])
            if due is None:
                return HttpResponseForbidden("Invalid datetime")
        else:
            return HttpResponseForbidden("Invalid datetime")

        if form.is_valid():
            new_deadline = Deadline(name=form.cleaned_data['name'], due=due,
                                    course=form.cleaned_data['course'])
            new_deadline.save()

            target_course = form.cleaned_data['course']

            for student in target_course.students.all():
                new_event = DueEvent.objects.create(deadline=new_deadline, user=student)
                new_event.save()
                new_deadline.students.add(student)

            context = {'publish_deadline_form': form, 'publish_deadline': True, 'success_flag': True}
            return render(request, 'duelink_admin/publish_deadline.html', context)
        else:
            print(form.errors)
            print(form_time.errors)
            return HttpResponseForbidden("Fail")
