from config.celery import app

import variants.models


@app.task(bind=True)
def refresh_variants_smallvariantsummary(_self):
    variants.models.refresh_variants_smallvariantsummary()
