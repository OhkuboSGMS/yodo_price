from jinja2 import Environment, FileSystemLoader

_test_html = "100000001000193273.html"
env = Environment(loader=FileSystemLoader("tests/test_data"))


def with_price(price: int):
    template = env.get_template(_test_html)
    return template.render(price=price)
