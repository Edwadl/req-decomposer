"""
req-decomposer 安装配置
需求文档拆解框架 - 将模糊需求自动拆解为结构化输出
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="req-decomposer",
    version="1.0.0",
    author="Edward",
    author_email="edward@example.com",
    description="需求文档拆解框架 - 将模糊需求自动拆解为结构化输出",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/edward/req-decomposer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Requirements Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "req-decomposer=req_decomposer.cli:main",
        ],
    },
)
