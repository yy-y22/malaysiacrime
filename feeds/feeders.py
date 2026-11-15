from django.contrib.gis.feeds import Feed

from crime.models import Crime, recently_commented


class LatestEntries(Feed):
    title = "Malaysia Crime Latest Reports"
    link = "/"
    description = "Updates on latest entries in www.malaysiacrime.com."

    def items(self):
        return Crime.objects.filter(is_removed=False).order_by('-created_at')[:50]

    def item_geometry(self, item):
        return (item.lng, item.lat)

    def item_pubdate(self, item):
        return item.updated_at

    def item_author_name(self, item):
        return item.author

    def item_categories(self, item):
        return (item.icon,)

class CommentedEntries(Feed):
    title = "Malaysia Crime Recent Commented Reports"
    link = "/recent/commented/"
    description = "Updates on recent commented entries in www.malaysiacrime.com."

    def items(self):
        return recently_commented(10, 10)

    def item_pubdate(self, item):
        return item.updated_at

    def item_author_name(self, item):
        return item.author

    def item_categories(self, item):
        return (item.icon,)

    def item_geometry(self, item):
        return (item.lng, item.lat)

class UpdatedEntries(Feed):
    title = "Malaysia Crime Recent Updated Reports"
    link = "/recent/updated/"
    description = "Updates on recent updated entries in www.malaysiacrime.com."

    def items(self):
        return Crime.objects.filter(is_removed=False).order_by('-updated_at')[:10]

    def item_pubdate(self, item):
        return item.updated_at

    def item_author_name(self, item):
        return item.author

    def item_categories(self, item):
        return (item.icon,)

    def item_geometry(self, item):
        return (item.lng, item.lat)
