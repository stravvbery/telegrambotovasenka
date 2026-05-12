"""Tests for bot.search.detector module."""

import pytest

from bot.search.detector import search_needed


class TestSearchNeededReturnsTrue:
    """Queries that need internet search should return True."""

    def test_latest_news_about_ai(self):
        assert search_needed("latest news about AI") is True

    def test_current_bitcoin_price(self):
        assert search_needed("current bitcoin price") is True

    def test_weather_in_london_today(self):
        assert search_needed("weather in London today") is True

    def test_who_won_the_match_yesterday(self):
        assert search_needed("who won the match yesterday") is True

    def test_whats_happening_in_ukraine(self):
        assert search_needed("what happened in Ukraine today") is True

    def test_breaking_news(self):
        assert search_needed("breaking news about elections") is True

    def test_stock_price(self):
        assert search_needed("stock price of Tesla") is True

    def test_trending_topics(self):
        assert search_needed("trending topics on Twitter") is True

    def test_this_week(self):
        assert search_needed("events this week in NYC") is True


class TestSearchNeededReturnsFalse:
    """Simple knowledge queries should return False."""

    def test_what_is_two_plus_two(self):
        assert search_needed("what is 2+2") is False

    def test_explain_photosynthesis(self):
        assert search_needed("explain photosynthesis") is False

    def test_write_poem_about_cats(self):
        assert search_needed("write me a poem about cats") is False

    def test_hello_how_are_you(self):
        assert search_needed("hello how are you") is False

    def test_translate_hello_to_french(self):
        assert search_needed("translate hello to French") is False

    def test_simple_math(self):
        assert search_needed("calculate 15 times 23") is False

    def test_definition_query(self):
        assert search_needed("what is the meaning of life") is False
