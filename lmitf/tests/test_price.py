from __future__ import annotations

from unittest.mock import Mock
from unittest.mock import patch

import pandas as pd
import pytest
import requests

from lmitf.pricing.fetch_dmxapi import DMXPricing
from lmitf.pricing.fetch_dmxapi import fetch_all
from lmitf.pricing.fetch_dmxapi import fetch_model_from_supplier
from lmitf.pricing.fetch_dmxapi import fetch_price
from lmitf.pricing.fetch_dmxapi import ModelPrice


class TestModelPrice:
    def test_model_price_token_billing(self):
        """Test ModelPrice for token billing"""
        price = ModelPrice(
            billing_type='token',
            input_per_m=10.0,
            output_per_m=20.0,
            per_call=None,
        )
        assert price.billing_type == 'token'
        assert price.input_per_m == 10.0
        assert price.output_per_m == 20.0
        assert price.per_call is None

    def test_model_price_per_call_billing(self):
        """Test ModelPrice for per-call billing"""
        price = ModelPrice(
            billing_type='per_call',
            input_per_m=None,
            output_per_m=None,
            per_call=5.0,
        )
        assert price.billing_type == 'per_call'
        assert price.input_per_m is None
        assert price.output_per_m is None
        assert price.per_call == 5.0


class TestDMXPricing:
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_pricing_data = {
            'data': {
                'model_info': '[["gpt-4", {"supplier": "OpenAI", "tags": ["优质", "智能"], "illustrate": "高级对话模型<em>强调</em>智能🤖"}], ["gpt-3.5-turbo", {"supplier": "OpenAI", "tags": ["经济"], "illustrate": "经济实惠模型"}], ["dall-e-3", {"supplier": "OpenAI", "tags": ["图像"], "illustrate": "图像生成模型"}]]',
                'model_group': {
                    'default': {
                        'GroupRatio': 1.0,
                        'ModelPrice': {
                            'gpt-4': {'isPrice': False, 'price': 10.0},
                            'gpt-3.5-turbo': {'isPrice': False, 'price': 5.0},
                            'dall-e-3': {'isPrice': True, 'price': 15.0},
                        },
                    },
                },
                'model_completion_ratio': {
                    'gpt-4': 2.0,
                    'gpt-3.5-turbo': 1.5,
                },
            },
        }

    def mock_requests_get(self, url, **kwargs):
        """Mock requests.get response"""
        mock_response = Mock()
        mock_response.json.return_value = self.mock_pricing_data
        mock_response.raise_for_status.return_value = None
        return mock_response

    @patch('lmitf.pricing.fetch_dmxapi.requests.get')
    def test_init_success(self, mock_get):
        """Test successful initialization"""
        mock_get.side_effect = self.mock_requests_get

        pricing = DMXPricing('https://test.com/pricing')

        assert pricing.group_name == 'default'
        assert pricing.group_ratio == 1.0
        assert isinstance(pricing.df, pd.DataFrame)
        assert not pricing.df.empty

    @patch('lmitf.pricing.fetch_dmxapi.requests.get')
    def test_url_normalization(self, mock_get):
        """Test URL normalization from /pricing to /api/pricing"""
        mock_get.side_effect = self.mock_requests_get

        pricing = DMXPricing('https://test.com/pricing')

        # Verify the call was made with normalized URL
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert called_url == 'https://test.com/api/pricing'

    @patch('lmitf.pricing.fetch_dmxapi.requests.get')
    def test_get_model_price_token_billing(self, mock_get):
        """Test getting model price for token billing"""
        mock_get.side_effect = self.mock_requests_get

        pricing = DMXPricing('https://test.com/pricing')
        price = pricing.get_model_price('gpt-4')

        assert isinstance(price, ModelPrice)
        assert price.billing_type == 'token'
        assert price.input_per_m == 20.0  # 2.0 * 10.0 * 1.0
        assert price.output_per_m == 40.0  # 20.0 * 2.0 (completion ratio)
        assert price.per_call is None

    @patch('lmitf.pricing.fetch_dmxapi.requests.get')
    def test_get_model_price_per_call_billing(self, mock_get):
        """Test getting model price for per-call billing"""
        mock_get.side_effect = self.mock_requests_get

        pricing = DMXPricing('https://test.com/pricing')
        price = pricing.get_model_price('dall-e-3')

        assert isinstance(price, ModelPrice)
        assert price.billing_type == 'per_call'
        assert price.input_per_m is None
        assert price.output_per_m is None
        assert price.per_call == 15.0

    @patch('lmitf.pricing.fetch_dmxapi.requests.get')
    def test_get_model_price_nonexistent(self, mock_get):
        """Test getting price for non-existent model"""
        mock_get.side_effect = self.mock_requests_get

        pricing = DMXPricing('https://test.com/pricing')

        with pytest.raises(KeyError, match='未找到模型或价格信息'):
            pricing.get_model_price('nonexistent-model')

    @patch('lmitf.pricing.fetch_dmxapi.requests.get')
    def test_get_models_by_vendor(self, mock_get):
        """Test filtering models by vendor"""
        mock_get.side_effect = self.mock_requests_get

        pricing = DMXPricing('https://test.com/pricing')
        openai_models = pricing.get_models_by_vendor('OpenAI')

        assert isinstance(openai_models, pd.DataFrame)
        assert len(openai_models) == 3  # gpt-4, gpt-3.5-turbo, dall-e-3
        assert all(openai_models['模型厂商'] == 'OpenAI')

    @patch('lmitf.pricing.fetch_dmxapi.requests.get')
    def test_dataframe_structure(self, mock_get):
        """Test DataFrame structure and content"""
        mock_get.side_effect = self.mock_requests_get

        pricing = DMXPricing('https://test.com/pricing')
        df = pricing.df

        expected_columns = [
            '模型厂商', '模型名称', '标签', '计费类型',
            '人民币计费价格（输入tokens/百万）', '人民币计费价格（输出tokens/百万）',
            '人民币计费价格（按次）', '分组', '说明',
        ]

        for col in expected_columns:
            assert col in df.columns

        # Check specific model data
        gpt4_row = df[df['模型名称'] == 'gpt-4'].iloc[0]
        assert gpt4_row['模型厂商'] == 'OpenAI'
        assert gpt4_row['计费类型'] == '按tokens'
        assert gpt4_row['说明'] == '高级对话模型强调智能'  # HTML and emoji stripped

    def test_init_no_data_field(self):
        """Test initialization when response lacks data field"""
        mock_data = {'error': 'No data'}

        with patch('lmitf.pricing.fetch_dmxapi.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            with pytest.raises(ValueError, match='pricing 接口返回缺少 data 字段'):
                DMXPricing('https://test.com/pricing')

    def test_init_no_model_group(self):
        """Test initialization when model_group is empty"""
        mock_data = {
            'data': {
                'model_info': '[]',
                'model_group': {},
                'model_completion_ratio': {},
            },
        }

        with patch('lmitf.pricing.fetch_dmxapi.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            with pytest.raises(ValueError, match='未找到 model_group 数据'):
                DMXPricing('https://test.com/pricing')

    @patch('lmitf.pricing.fetch_dmxapi.requests.get')
    def test_requests_error_handling(self, mock_get):
        """Test handling of requests errors"""
        mock_get.side_effect = requests.RequestException('Connection error')

        with pytest.raises(requests.RequestException):
            DMXPricing('https://test.com/pricing')

    @patch('lmitf.pricing.fetch_dmxapi.DMXPricing')
    def test_fetch_price_function(self, mock_dmx_pricing):
        """Test fetch_price convenience function"""
        mock_client = Mock()
        mock_price = ModelPrice('token', 10.0, 20.0, None)
        mock_client.get_model_price.return_value = mock_price
        mock_dmx_pricing.return_value = mock_client

        result = fetch_price('https://test.com', 'gpt-4')

        assert result == mock_price.__dict__
        mock_dmx_pricing.assert_called_once_with('https://test.com')
        mock_client.get_model_price.assert_called_once_with('gpt-4')

    @patch('lmitf.pricing.fetch_dmxapi.DMXPricing')
    def test_fetch_all_function(self, mock_dmx_pricing):
        """Test fetch_all convenience function"""
        mock_client = Mock()
        mock_df = pd.DataFrame({'model': ['gpt-4']})
        mock_client.df = mock_df
        mock_dmx_pricing.return_value = mock_client

        result = fetch_all('https://test.com')

        assert result is mock_df
        mock_dmx_pricing.assert_called_once_with('https://test.com')

    @patch('lmitf.pricing.fetch_dmxapi.DMXPricing')
    def test_fetch_model_from_supplier_function(self, mock_dmx_pricing):
        """Test fetch_model_from_supplier convenience function"""
        mock_client = Mock()
        mock_df = pd.DataFrame({'模型名称': ['gpt-4', 'gpt-3.5-turbo']})
        mock_client.get_models_by_vendor.return_value = mock_df
        mock_dmx_pricing.return_value = mock_client

        result = fetch_model_from_supplier('https://test.com', 'OpenAI')

        assert result == ['gpt-4', 'gpt-3.5-turbo']
        mock_dmx_pricing.assert_called_once_with('https://test.com')
        mock_client.get_models_by_vendor.assert_called_once_with('OpenAI')
