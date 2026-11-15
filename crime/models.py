from django.contrib.comments.models import Comment
from django.db import models
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

class Crime(models.Model):
    """
    Represents a crime report.
    """
    headline       = models.CharField(max_length=100, unique=True)
    slug           = models.SlugField(max_length=100, unique=True, db_index=True)
    date           = models.DateField()
    location       = models.CharField(max_length=300)
    icon           = models.CharField(max_length=50)
    lat            = models.FloatField()
    lng            = models.FloatField()
    zoom           = models.IntegerField()
    details        = models.TextField()
    author         = models.CharField(max_length=50)
    remote_address = models.IPAddressField(null=True)
    password       = models.CharField(max_length=128)
    is_removed     = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.headline)
        super(Crime, self).save()

    def __unicode__(self):
        return self.headline

    @models.permalink
    def get_absolute_url(self):
        return ('crime-title', (), {'slug': self.slug})

def recently_commented(comment_window, limit):
    """
    Crimes ordered by their latest comment among the `comment_window` most recent
    comments. Non-numeric, missing and removed crimes are skipped, then the first `limit`
    are returned.
    """
    ids = []
    for pk in Comment.objects.order_by('-submit_date').values_list('object_pk', flat=True)[:comment_window]:
        try:
            pk = int(pk)
        except ValueError:
            continue
        # Ids outside the 64-bit database integer range cannot exist and make in_bulk overflow.
        if abs(pk) < 2 ** 63 and pk not in ids:
            ids.append(pk)
    crimes = Crime.objects.filter(is_removed=False).in_bulk(ids)
    return [crimes[pk] for pk in ids if pk in crimes][:limit]
