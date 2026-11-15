
class SetRemoteAddrFromForwardedFor(object):
    """
    Set REMOTE_ADDR from a syntactically valid IPv4 X-Forwarded-For value.

    The header must still be supplied by a trusted proxy; validating its
    syntax does not make an untrusted header safe.
    """
    def process_request(self, request):
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if not forwarded_for:
            return None

        # The left-most address is the originating client according to the
        # existing proxy convention.
        real_ip = forwarded_for.split(",")[0].strip()
        octets = real_ip.split(".")
        if len(octets) != 4:
            return None

        for octet in octets:
            if not octet or not all('0' <= character <= '9' for character in octet):
                return None
            if len(octet) > 1 and octet[0] == "0":
                return None
            if int(octet) > 255:
                return None

        request.META['REMOTE_ADDR'] = real_ip
        return None
