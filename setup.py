from setuptools import setup, find_packages

setup(
    name="autotelemetry",
    version="0.1.0",
    description="Une bibliothèque simplifiée d'observabilité pour Python avec auto-instrumentation",
    author="AutoTelemetry Team",
    author_email="contact@autotelemetry.io",
    packages=find_packages(),
    install_requires=[
        "opentelemetry-api>=1.12.0",
        "opentelemetry-sdk>=1.12.0",
        "opentelemetry-exporter-otlp-proto-grpc>=1.12.0",
        "prometheus-client>=0.14.1",
        "opentelemetry-exporter-prometheus>=0.33b0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.3.0",
            "flake8>=4.0.1",
            "mypy>=0.942"
        ],
        "data": [
            "pandas>=1.4.0",
            "numpy>=1.22.0",
            "scikit-learn>=1.0.2"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
) 