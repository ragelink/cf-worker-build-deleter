"""
Cloudflare Pages Deployment Deleter

Top-level package for the Cloudflare Pages deployment deletion utility.
"""

# Import version from the src module
try:
    from deleter.src import __version__
except ImportError:
    __version__ = '1.0.0'  # Default version if not importable 