from compressor.filters.css_default import CssAbsoluteFilter
from compressor.utils import staticfiles


class CustomCssAbsoluteFilter(CssAbsoluteFilter):
    def find(self, basename):
        # The line below is the original line.  I removed settings.DEBUG.
        # if settings.DEBUG and basename and staticfiles.finders:
        if basename and staticfiles.finders:
            return staticfiles.finders.find(basename)