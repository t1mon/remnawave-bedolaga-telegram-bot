"""AHOWS patch: tests for ``promo__clickId=VALUE`` /start deeplink parser.

``__`` is Telegram-safe stand-in for ``&``. Keitaro ``_subid_`` must keep working.
"""

import pytest

from app.handlers.start import _split_start_param_ahows_click_id, _split_start_param_subid


class TestAhowsClickIdParser:
    def test_campaign_and_click_id(self) -> None:
        assert _split_start_param_ahows_click_id('promo123__clickId=abc123xyz') == (
            'promo123',
            'abc123xyz',
        )

    def test_click_id_only(self) -> None:
        assert _split_start_param_ahows_click_id('clickId=abc123xyz') == (None, 'abc123xyz')

    def test_leading_separator(self) -> None:
        assert _split_start_param_ahows_click_id('__clickId=abc') == (None, 'abc')

    def test_extra_kv_segments_preserved_in_campaign(self) -> None:
        assert _split_start_param_ahows_click_id('promo__foo=1__clickId=xyz') == (
            'promo__foo=1',
            'xyz',
        )

    def test_rejects_empty_click_id(self) -> None:
        assert _split_start_param_ahows_click_id('promo__clickId=') == ('promo__clickId=', None)

    def test_rejects_oversized_click_id(self) -> None:
        oversized = 'x' * 256
        param = f'promo__clickId={oversized}'
        assert _split_start_param_ahows_click_id(param) == (param, None)

    def test_unchanged_when_no_click_id_key(self) -> None:
        assert _split_start_param_ahows_click_id('promo123') == ('promo123', None)
        assert _split_start_param_ahows_click_id('GIFT_abc') == ('GIFT_abc', None)

    def test_none_and_empty(self) -> None:
        assert _split_start_param_ahows_click_id(None) == (None, None)
        assert _split_start_param_ahows_click_id('') == ('', None)


class TestSplitStartParamSubidAhowsFallback:
    """Unified entry-point must prefer Keitaro, then fall back to AHOWS."""

    def test_keitaro_still_wins(self) -> None:
        assert _split_start_param_subid('clkcl_subid_KEITARO-1') == ('clkcl', 'KEITARO-1')

    def test_ahows_via_unified_parser(self) -> None:
        assert _split_start_param_subid('promo123__clickId=abc123xyz') == (
            'promo123',
            'abc123xyz',
        )

    @pytest.mark.parametrize(
        ('param', 'expected'),
        [
            ('vpn__clickId=a-b-c', ('vpn', 'a-b-c')),
            ('clickId=only', (None, 'only')),
            ('summer_promo__clickId=xyz', ('summer_promo', 'xyz')),
        ],
    )
    def test_parametrized_ahows(self, param: str, expected: tuple[str | None, str]) -> None:
        assert _split_start_param_subid(param) == expected
