from unittest import mock

from widgets import (
    HemaraPoller,
    colors,
    hemara_icons,
)


def _endpoint(group: str, success: bool) -> dict:
    """
    Endpoint de Gatus con un único resultado.
    """
    return {"group": group, "results": [{"success": success}]}


def test_only_failing_group_blinks() -> None:
    """
    Prod sano queda fijo; pre caído alterna entre rojo y apagado.
    """
    endpoints = [_endpoint("Producción", True), _endpoint("Preproducción", False)]
    on = hemara_icons(endpoints, blink_on=True)
    off = hemara_icons(endpoints, blink_on=False)
    assert on.index(colors["ok"]) < on.index(colors["fail"])
    assert colors["fail"] not in off
    assert off.count(colors["ok"]) == 1


def test_unreachable_gatus_is_dim() -> None:
    """
    Sin respuesta de Gatus los dos íconos quedan apagados y no titilan.
    """
    assert hemara_icons(None, blink_on=True).count(colors["inactive"]) == 2


def test_poller_fetches_once_per_refresh() -> None:
    """
    Llamadas seguidas no vuelven a consultar Gatus hasta que pasa `refresh`.
    """
    poller = HemaraPoller(refresh=60)
    with (
        mock.patch("widgets.fetch_endpoints", return_value=[]) as fetch,
        mock.patch("widgets.time.monotonic", side_effect=[100.0, 100.5, 161.0]),
    ):
        poller()
        poller()
        poller()
    assert fetch.call_count == 2


if __name__ == "__main__":
    test_only_failing_group_blinks()
    test_unreachable_gatus_is_dim()
    test_poller_fetches_once_per_refresh()
    print("ok")
