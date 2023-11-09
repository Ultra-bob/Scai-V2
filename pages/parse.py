from jinja2 import Environment, FileSystemLoader
import filters
environment = Environment(loader=FileSystemLoader("templates/"), lstrip_blocks=True, trim_blocks=True)

environment.filters.update({"fix_camelcase": filters.fix_camelcase, "commas": filters.numberFormat})

def parse(data, format_):
    if format_ == "component":
        format_ = f"components/{data['type'].lower()}"
    return environment.get_template(f"{format_}.jinja").render(data)