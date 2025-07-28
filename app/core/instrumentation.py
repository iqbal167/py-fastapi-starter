from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


def instrument_fastapi_app(app):
    FastAPIInstrumentor.instrument_app(app)
