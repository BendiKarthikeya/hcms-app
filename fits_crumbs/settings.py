from fits.settings import TEMPLATES

TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "fits_crumbs.context_processors.breadcrumbs",
)
