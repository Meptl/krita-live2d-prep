from .extension import Live2DExporterExtension

Krita.instance().addExtension(Live2DExporterExtension(Krita.instance()))
