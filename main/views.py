from datetime import datetime

from django.core.urlresolvers import reverse
from django.core.paginator import InvalidPage, Paginator
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from crime.models import Crime, recently_commented


def index(request, template_name='main/index.html'):
    """
    Index page.
    """
    if request.method == 'GET':
        paginator = Paginator(Crime.objects.filter(is_removed=False).order_by('-created_at', '-id'), 20)
        try:
            page = paginator.page(request.GET.get('page', 1))
        except InvalidPage:
            raise Http404
    else:
        return HttpResponseRedirect(request.path)

    context = RequestContext(request, {
        'crimes': page.object_list,
        'page': page,
        'crime_total': paginator.count,
        'now': datetime.now(),
    })
    return render_to_response(template_name, context_instance=context)

def recent_updated(request, template_name='main/recent_updated.html'):
    """
    Return crime reports sort by recent updated.
    """
    if request.method == 'GET':
        crimes = Crime.objects.filter(is_removed=False).order_by('-updated_at')[:200]
    else:
        return HttpResponseRedirect(request.path)

    context = RequestContext(request, {
        'crimes': crimes,
        'crime_total': Crime.objects.count(),
        'now': datetime.now(),
    })
    return render_to_response(template_name, context_instance=context)

def recent_commented(request, template_name='main/recent_commented.html'):
    """
    Return crime reports sort by recent commented.
    """
    if request.method == 'GET':
        crimes = recently_commented(500, 200)
    else:
        return HttpResponseRedirect(request.path)

    context = RequestContext(request, {
        'crimes': crimes,
        'crime_total': Crime.objects.count(),
        'now': datetime.now(),
    })
    return render_to_response(template_name, context_instance=context)
