"""
@ Author：YueC
@ Description：
"""
import pytest

if __name__ == '__main__':
    pytest.main(['-v', '--maxfail=30', './tests/test_case/', '--alluredir', ' /report/test'])
